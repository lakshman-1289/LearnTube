from pydantic import BaseModel, Field
from typing import List, Optional


class AnswerSubmission(BaseModel):
    quiz_id: int = Field(..., description="Quiz/question ID")
    selected_answer: int = Field(..., ge=0, le=3, description="Index of the selected option (0-3)")


class ExamSubmission(BaseModel):
    video_id: str = Field(..., description="YouTube video ID of the course")
    answers: List[AnswerSubmission] = Field(..., min_length=1)


class QuizResult(BaseModel):
    quiz_id: int
    correct: bool
    correct_answer: int
    selected_answer: int
    explanation: str


class ExamResult(BaseModel):
    video_id: str
    total_questions: int
    correct_count: int
    score: float  # percentage 0-100
    passed: bool
    passing_score: int = 70
    results: List[QuizResult]


class CertificateResponse(BaseModel):
    certificate_id: str
    user_name: str
    course_title: str
    completion_date: str
    video_id: str
    issued_at: str
