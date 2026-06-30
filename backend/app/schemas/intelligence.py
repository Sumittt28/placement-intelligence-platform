from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


# --- Weakness ---
class WeaknessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    topic: str
    category: Optional[str] = None
    occurrence_count: int
    severity: Optional[str] = None
    sources: List[str] = []
    recommended_actions: List[str] = []
    is_resolved: bool
    first_detected: datetime
    last_detected: datetime


# --- Recommendation ---
class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str
    title: str
    description: Optional[str] = None
    priority: int
    metadata: Optional[Dict[str, Any]] = None
    is_completed: bool
    created_at: datetime


# --- Resume ---
class ResumeInsightsResponse(BaseModel):
    skills: List[str] = []
    projects: List[Dict[str, Any]] = []
    experience: List[Dict[str, Any]] = []
    technologies: List[str] = []
    domains: List[str] = []
    insights: Dict[str, Any] = {}
    parsed_at: Optional[datetime] = None


# --- Readiness ---
class ReadinessDimension(BaseModel):
    name: str
    score: float
    gap: str


class CompanyReadiness(BaseModel):
    company_id: str
    company_name: str
    readiness_percent: float
    dimensions: List[ReadinessDimension] = []
    recommendations: List[str] = []


class OverallReadinessResponse(BaseModel):
    overall_readiness: float
    companies: List[CompanyReadiness] = []


# --- Search ---
class SearchResult(BaseModel):
    question_text: str
    topic: str
    company_name: str
    round_type: str
    difficulty: str
    frequency: int = 1


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult] = []
    total: int = 0
