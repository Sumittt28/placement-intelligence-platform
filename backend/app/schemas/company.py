from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CompanyCreate(BaseModel):
    name: str = Field(..., min_length=1)
    industry: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None


class CompanyResponse(BaseModel):
    id: str
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CompanyAnalyticsResponse(BaseModel):
    total_experiences: int = 0
    total_questions: int = 0
    top_topics: List[Dict[str, Any]] = []
    difficulty_dist: Dict[str, int] = {}
    round_dist: Dict[str, int] = {}
    success_rate: float = 0.0
    common_weaknesses: List[str] = []
    last_computed: Optional[datetime] = None


class CompanyIntelligenceResponse(BaseModel):
    company: CompanyResponse
    analytics: CompanyAnalyticsResponse
    recent_experiences: List[Any] = []
    frequently_asked_questions: List[Dict[str, Any]] = []
    questions_by_round: Dict[str, List[Dict[str, Any]]] = {}
