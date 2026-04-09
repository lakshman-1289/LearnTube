"""
exam_routes.py
Final exam submission and certificate generation endpoints.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from models.exam_schemas import ExamSubmission, ExamResult, QuizResult, CertificateResponse
from services.db_service import db_service
from services.certificate_service import build_certificate_doc, generate_pdf_certificate
from routers.auth_routes import get_current_user

router = APIRouter(prefix="/exam", tags=["exam"])

PASSING_SCORE = 70  # percent


# ── helpers ─────────────────────────────────────────────────────────────────

def _build_quiz_lookup(course_data: dict) -> dict:
    """
    Returns {quiz_id: quiz_obj} from a cached course_data dict.
    """
    lookup = {}
    for lesson in course_data.get("lessons", []):
        for quiz in lesson.get("quizzes", []):
            lookup[quiz["id"]] = quiz
    return lookup


# ── endpoints ────────────────────────────────────────────────────────────────

@router.post("/submit-exam", response_model=ExamResult)
async def submit_exam(
    body: ExamSubmission,
    current_user: dict = Depends(get_current_user),
):
    """
    Grade a final exam submission.
    Expects the video_id and a list of {quiz_id, selected_answer} pairs.
    Returns score, pass/fail, and per-question results.
    """
    cached = await db_service.get_cached_course(body.video_id)
    if not cached or not cached.get("course_data"):
        raise HTTPException(status_code=404, detail="Course not found. Generate it first.")

    quiz_lookup = _build_quiz_lookup(cached["course_data"])

    results = []
    correct_count = 0

    for submission in body.answers:
        quiz = quiz_lookup.get(submission.quiz_id)
        if not quiz:
            # Skip unknown quiz IDs gracefully
            continue
        correct_idx = quiz["correctAnswer"]
        is_correct = submission.selected_answer == correct_idx
        if is_correct:
            correct_count += 1
        results.append(
            QuizResult(
                quiz_id=submission.quiz_id,
                correct=is_correct,
                correct_answer=correct_idx,
                selected_answer=submission.selected_answer,
                explanation=quiz.get("explanation", ""),
            )
        )

    total = len(results)
    score = round((correct_count / total) * 100, 1) if total > 0 else 0.0
    passed = score >= PASSING_SCORE

    # Persist exam result
    exam_doc = {
        "user_id": current_user["_id"],
        "video_id": body.video_id,
        "score": score,
        "passed": passed,
        "correct_count": correct_count,
        "total_questions": total,
        "submitted_at": datetime.now(timezone.utc).isoformat(),
    }
    await db_service.save_exam_result(exam_doc)

    return ExamResult(
        video_id=body.video_id,
        total_questions=total,
        correct_count=correct_count,
        score=score,
        passed=passed,
        passing_score=PASSING_SCORE,
        results=results,
    )


@router.post("/generate-certificate", response_model=CertificateResponse)
async def generate_certificate(
    body: dict,
    current_user: dict = Depends(get_current_user),
):
    """
    Issues a certificate if:
    - The user passed the exam (score >= 70%)
    - Called after /submit-exam

    Body: {"video_id": "..."}
    """
    video_id = body.get("video_id")
    if not video_id:
        raise HTTPException(status_code=400, detail="Missing video_id")

    user_id = current_user["_id"]

    # Check exam result
    exam = await db_service.get_exam_result(user_id=user_id, video_id=video_id)
    if not exam:
        raise HTTPException(status_code=400, detail="No exam result found. Submit the exam first.")
    if not exam.get("passed"):
        raise HTTPException(
            status_code=400,
            detail=f"Exam not passed (score: {exam.get('score', 0)}%). Need {PASSING_SCORE}% to earn a certificate.",
        )

    # Fetch course title
    cached = await db_service.get_cached_course(video_id)
    course_title = cached.get("title", "LearnTube Course") if cached else "LearnTube Course"

    cert_doc = build_certificate_doc(
        user_id=user_id,
        user_name=current_user["name"],
        video_id=video_id,
        course_title=course_title,
    )
    await db_service.save_certificate(cert_doc)

    return CertificateResponse(
        certificate_id=cert_doc["certificate_id"],
        user_name=cert_doc["user_name"],
        course_title=cert_doc["course_title"],
        completion_date=cert_doc["completion_date"],
        video_id=cert_doc["video_id"],
        issued_at=cert_doc["issued_at"],
    )


@router.get("/certificate/{certificate_id}")
async def get_certificate(certificate_id: str):
    """Retrieve a certificate by its ID (public — shareable link)."""
    cert = await db_service.get_certificate(certificate_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return cert


@router.get("/certificate/{certificate_id}/pdf")
async def download_certificate_pdf(certificate_id: str):
    """Download a PDF version of a certificate (requires reportlab)."""
    cert = await db_service.get_certificate(certificate_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    pdf_bytes = generate_pdf_certificate(cert)
    if pdf_bytes is None:
        raise HTTPException(
            status_code=501,
            detail="PDF generation not available. Install reportlab to enable this feature.",
        )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="certificate-{certificate_id}.pdf"'
        },
    )


@router.get("/my-certificates")
async def my_certificates(current_user: dict = Depends(get_current_user)):
    """Return all certificates earned by the authenticated user."""
    certs = await db_service.get_user_certificates(current_user["_id"])
    return {"success": True, "certificates": certs}
