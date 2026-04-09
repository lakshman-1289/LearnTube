"""
exam_routes.py
Final exam submission and certificate generation endpoints.
Auth is handled by the Next.js proxy (which validates NextAuth session),
so these endpoints accept user_id / user_name directly in the request body.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import List

from models.exam_schemas import (
    ExamResult, QuizResult, CertificateResponse,
    AnswerSubmission,
)
from services.db_service import db_service
from services.certificate_service import build_certificate_doc, generate_pdf_certificate

router = APIRouter(prefix="/exam", tags=["exam"])

PASSING_SCORE = 70  # percent


# ── request bodies ────────────────────────────────────────────────────────────

class ExamSubmissionBody(BaseModel):
    video_id: str
    user_id: str
    user_name: str = "Learner"
    answers: List[AnswerSubmission]


class CertificateRequestBody(BaseModel):
    video_id: str
    user_id: str
    user_name: str = "Learner"


# ── helpers ───────────────────────────────────────────────────────────────────

def _build_quiz_lookup(course_data: dict) -> dict:
    lookup = {}
    for lesson in course_data.get("lessons", []):
        for quiz in lesson.get("quizzes", []):
            lookup[quiz["id"]] = quiz
    return lookup


# ── endpoints ─────────────────────────────────────────────────────────────────

@router.get("/questions/{video_id}")
async def get_exam_questions(video_id: str):
    """Return all quiz questions for a course (used to render the exam UI)."""
    cached = await db_service.get_cached_course(video_id)
    if not cached or not cached.get("course_data"):
        raise HTTPException(status_code=404, detail="Course not found.")

    questions = []
    for lesson in cached["course_data"].get("lessons", []):
        for quiz in lesson.get("quizzes", []):
            questions.append({
                "id": quiz["id"],
                "question": quiz["question"],
                "options": quiz.get("options", []),
                "lesson_title": lesson.get("title", ""),
            })

    return {
        "video_id": video_id,
        "course_title": cached.get("title", "Untitled Course"),
        "total_questions": len(questions),
        "questions": questions,
    }


@router.post("/submit-exam", response_model=ExamResult)
async def submit_exam(body: ExamSubmissionBody):
    """Grade a final exam submission."""
    cached = await db_service.get_cached_course(body.video_id)
    if not cached or not cached.get("course_data"):
        raise HTTPException(status_code=404, detail="Course not found.")

    quiz_lookup = _build_quiz_lookup(cached["course_data"])

    results = []
    correct_count = 0

    for submission in body.answers:
        quiz = quiz_lookup.get(submission.quiz_id)
        if not quiz:
            continue
        correct_idx = quiz["correctAnswer"]
        is_correct = submission.selected_answer == correct_idx
        if is_correct:
            correct_count += 1
        results.append(QuizResult(
            quiz_id=submission.quiz_id,
            correct=is_correct,
            correct_answer=correct_idx,
            selected_answer=submission.selected_answer,
            explanation=quiz.get("explanation", ""),
        ))

    total = len(results)
    score = round((correct_count / total) * 100, 1) if total > 0 else 0.0
    passed = score >= PASSING_SCORE

    exam_doc = {
        "user_id": body.user_id,
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
async def generate_certificate(body: CertificateRequestBody):
    """Issue a certificate if the user passed the exam."""
    exam = await db_service.get_exam_result(
        user_id=body.user_id, video_id=body.video_id
    )
    if not exam:
        raise HTTPException(status_code=400, detail="Submit the exam first.")
    if not exam.get("passed"):
        raise HTTPException(
            status_code=400,
            detail=f"Exam not passed (score: {exam.get('score', 0)}%). Need {PASSING_SCORE}%.",
        )

    cached = await db_service.get_cached_course(body.video_id)
    course_title = cached.get("title", "LearnTube Course") if cached else "LearnTube Course"

    cert_doc = build_certificate_doc(
        user_id=body.user_id,
        user_name=body.user_name,
        video_id=body.video_id,
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
    """Retrieve a certificate by ID (public shareable link)."""
    cert = await db_service.get_certificate(certificate_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return cert


@router.get("/certificate/{certificate_id}/pdf")
async def download_certificate_pdf(certificate_id: str):
    """Download a PDF certificate."""
    cert = await db_service.get_certificate(certificate_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")

    pdf_bytes = generate_pdf_certificate(cert)
    if pdf_bytes is None:
        raise HTTPException(status_code=501, detail="Install reportlab for PDF support.")

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="certificate-{certificate_id}.pdf"'},
    )


@router.get("/my-certificates")
async def my_certificates(user_id: str):
    """Return all certificates for a user (user_id passed as query param)."""
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    certs = await db_service.get_user_certificates(user_id)
    return {"success": True, "certificates": certs}


@router.get("/my-exam-result")
async def my_exam_result(user_id: str, video_id: str):
    """Check if user already has an exam result for this course."""
    exam = await db_service.get_exam_result(user_id=user_id, video_id=video_id)
    if not exam:
        return {"exists": False}
    return {
        "exists": True,
        "score": exam.get("score"),
        "passed": exam.get("passed"),
        "submitted_at": exam.get("submitted_at"),
    }
