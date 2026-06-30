from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class InterviewType(str, Enum):
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    HM = "hm"
    PROJECT = "project"
    COMPANY = "company"
    CUSTOM = "custom"


class InterviewMode(str, Enum):
    TEXT = "text"
    VOICE = "voice"


class StartInterviewRequest(BaseModel):
    interview_type: InterviewType
    difficulty: str = Field(..., pattern="^(Easy|Medium|Hard)$")
    company_id: Optional[str] = None
    mode: InterviewMode = InterviewMode.TEXT


class SubmitAnswerRequest(BaseModel):
    answer: str = Field(..., min_length=1)
    audio_url: Optional[str] = None


class InterviewQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sequence_num: int
    question_text: str
    question_type: Optional[str] = None
    topic: Optional[str] = None


class NextQuestionResponse(BaseModel):
    question: Optional[InterviewQuestionResponse] = None
    is_complete: bool = False
    message: Optional[str] = None


class StartInterviewResponse(BaseModel):
    interview_id: str
    first_question: InterviewQuestionResponse


class MockInterviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    interview_type: str
    difficulty: str
    mode: str
    status: str
    company_id: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
    questions: List[InterviewQuestionResponse] = []


class ReplayQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sequence_num: int
    question_text: str
    question_type: Optional[str] = None
    topic: Optional[str] = None
    student_answer: Optional[str] = None
    ideal_answer: Optional[str] = None
    evaluation: Optional[Dict[str, Any]] = None
    feedback: Optional[str] = None
    audio_url: Optional[str] = None


class ReplayResponse(BaseModel):
    interview: MockInterviewResponse
    questions: List[ReplayQuestionResponse]
    evaluation: Optional["EvaluationResponse"] = None


# Forward reference resolved below
from app.schemas.evaluation import EvaluationResponse  # noqa: E402
ReplayResponse.model_rebuild()
