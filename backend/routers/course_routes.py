import os
import re
import uuid
import asyncio

from fastapi import APIRouter, BackgroundTasks, HTTPException

from services.transcript_service import extract_transcript
from services.chapter_service import generate_chapters
from services.content_classifier import classify_video_content
from course_generator.src.core.courseGenerator import CourseGenerator
from course_generator.src.core.groq_client import GroqClient
from services.db_service import db_service

router = APIRouter()


def log(msg: str):
    print(f"[LOG] {msg}")


def _extract_video_id(url: str) -> str:
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else url


async def _run_course_pipeline(url: str) -> dict:
    """
    Shared logic: transcript → chapters → course generation.
    Returns the full combined response dict (same shape as the sync endpoint).
    """
    video_id = _extract_video_id(url)

    # Check cache
    cached = await db_service.get_cached_course(video_id)
    if cached:
        log("Returning cached course.")
        return {
            "success": True,
            "course_data": cached.get("course_data"),
            "processing_stats": {"cache_hit": True},
            "video_id": cached.get("video_id"),
            "title": cached.get("title"),
            "transcript_length": cached.get("transcript_length"),
            "chapters": cached.get("chapters", []),
        }

    # Extract transcript
    log("Extracting transcript...")
    transcript_result = extract_transcript(url)

    if transcript_result and transcript_result.get("error") and not transcript_result.get("transcript"):
        return {
            "success": False,
            "error": "This video has no accessible captions. Please try another video.",
            "course_data": None,
            "processing_stats": None,
            "video_id": transcript_result.get("videoId", ""),
            "title": "",
            "transcript_length": 0,
            "chapters": [],
        }

    if not transcript_result or not transcript_result.get("transcript"):
        raise Exception("Transcript extraction failed")

    transcript_text = transcript_result["transcript"]
    if len(transcript_text.strip()) < 100:
        raise Exception("Transcript too short for course generation.")

    # Classify content (fails open — never blocks on error)
    log("Classifying video content...")
    category = await classify_video_content(
        title=transcript_result.get("title", ""),
        transcript_excerpt=transcript_text,
    )
    if category != "educational":
        return {
            "success": False,
            "message": "Course generation is only available for educational videos",
            "course_data": None,
            "processing_stats": None,
            "video_id": transcript_result.get("videoId", ""),
            "title": transcript_result.get("title", ""),
            "transcript_length": len(transcript_text),
            "chapters": [],
        }

    # Generate chapters
    log("Generating chapters...")
    segments = transcript_result.get("segments", [])
    chapters = generate_chapters(segments) if segments else []
    chapter_data = [{"title": c.title, "time": c.time} for c in chapters]

    # Generate course
    log("Generating course...")
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise Exception("GROQ_API_KEY not found in environment variables.")

    groq_client = None
    try:
        groq_client = GroqClient(api_key=groq_api_key)
        course_generator = CourseGenerator(groq_client)
        course_data = await course_generator.generate_complete_course(
            transcript_text=transcript_text,
            video_title=transcript_result["title"],
            video_url=url,
        )
        if isinstance(course_data, dict) and "error" in course_data:
            raise Exception(course_data.get("error", "Course generation failed"))
    finally:
        if groq_client and hasattr(groq_client, "session") and groq_client.session:
            await groq_client.session.close()

    # Cache result
    transcript_len = len(transcript_text)
    await db_service.cache_course(
        video_id=transcript_result["videoId"],
        youtube_url=url,
        title=transcript_result["title"],
        transcript_length=transcript_len,
        chapters=chapter_data,
        course_data=course_data,
    )

    return {
        "success": True,
        "course_data": course_data,
        "processing_stats": {"cache_hit": False},
        "video_id": transcript_result["videoId"],
        "title": transcript_result["title"],
        "transcript_length": transcript_len,
        "chapters": chapter_data,
    }


# ─────────────────────────────────────────────────────────────
#  ORIGINAL SYNC ENDPOINT — response structure UNCHANGED
# ─────────────────────────────────────────────────────────────

@router.post("/generate-course-from-youtube")
async def generate_course_from_youtube(body: dict):
    """
    Synchronous endpoint (original). Kept 100% backward-compatible.
    Check cache → Extract transcript → Classify → Generate → Cache → Return.
    """
    try:
        url = body.get("url") or body.get("youtube_url")
        if not url:
            raise Exception("Missing 'url' or 'youtube_url'")
        log(f"Processing video: {url}")
        result = await _run_course_pipeline(url)
        return result
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────
#  ASYNC ENDPOINT — for long videos that would otherwise timeout
# ─────────────────────────────────────────────────────────────

async def _background_job(job_id: str, url: str):
    """Runs the pipeline in the background and persists the result."""
    try:
        result = await _run_course_pipeline(url)
        await db_service.update_job_completed(job_id, result)
        log(f"Job {job_id} completed.")
    except Exception as exc:
        print(f"[JOB ERROR] {job_id}: {exc}")
        await db_service.update_job_failed(job_id, str(exc))


@router.post("/generate-course-async")
async def generate_course_async(body: dict, background_tasks: BackgroundTasks):
    """
    Async variant. Returns immediately with a job_id.
    Poll GET /course-status/{job_id} to get the result.
    """
    url = body.get("url") or body.get("youtube_url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' or 'youtube_url'")

    job_id = str(uuid.uuid4())
    await db_service.create_job(job_id=job_id, video_url=url)

    background_tasks.add_task(_background_job, job_id, url)

    log(f"Async job created: {job_id}")
    return {"status": "processing", "job_id": job_id}


@router.get("/course-status/{job_id}")
async def get_course_status(job_id: str):
    """
    Returns the status of an async course generation job.
    Status: 'processing' | 'completed' | 'failed'
    On 'completed', includes the full course result under 'data'.
    """
    job = await db_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    status = job.get("status", "processing")

    if status == "completed":
        return {"status": "completed", "job_id": job_id, "data": job.get("result")}
    if status == "failed":
        return {"status": "failed", "job_id": job_id, "error": job.get("error")}

    return {"status": "processing", "job_id": job_id}
