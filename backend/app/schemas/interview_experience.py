from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class RoundType(str, Enum):
    OA = "OA"
    TECHNICAL = "Technical"
    HM = "HM"
    HR = "HR"
    SYSTEM_DESIGN = "System Design"
    OTHER = "Other"


class Difficulty(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class Outcome(str, Enum):
    SELECTED = "Selected"
    REJECTED = "Rejected"
    WAITING = "Waiting"
    UNKNOWN = "Unknown"


class CouldAnswer(str, Enum):
    YES = "Yes"
    PARTIALLY = "Partially"
    NO = "No"


class QuestionCreate(BaseModel):
    topic: str = Field(..., min_length=1)
    question_text: str = Field(..., min_length=1)
    could_answer: CouldAnswer


class QuestionResponse(BaseModel):
    id: str
    topic: str
    question_text: str
    could_answer: str
    ai_tags: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ExperienceCreate(BaseModel):
    company_id: str
    role: str = Field(..., min_length=1)
    interview_date: date
    round_type: RoundType
    difficulty: Difficulty
    outcome: Outcome
    student_notes: Optional[str] = None
    questions: List[QuestionCreate] = Field(..., min_length=1)


class ExperienceResponse(BaseModel):
    id: str
    user_id: str
    company_id: str
    company_name: Optional[str] = None
    role: str
    interview_date: date
    round_type: str
    difficulty: str
    outcome: str
    student_notes: Optional[str] = None
    ai_extracted: Optional[Dict[str, Any]] = None
    is_approved: bool
    questions: List[QuestionResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


class ExperienceListResponse(BaseModel):
    experiences: List[ExperienceResponse]
    total: int
    page: int
    limit: int
