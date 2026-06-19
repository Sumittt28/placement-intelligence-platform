from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class PlacementStats(BaseModel):
    interviews_attempted: int = 0
    ai_interviews_completed: int = 0
    contributions_submitted: int = 0
    company_reports_viewed: int = 0


class RecentActivityItem(BaseModel):
    action: str
    resource: Optional[str] = None
    resource_id: Optional[str] = None
    created_at: datetime


class PerformanceScore(BaseModel):
    communication: float = 0.0
    technical_depth: float = 0.0
    problem_solving: float = 0.0
    behavioral: float = 0.0
    project_discussions: float = 0.0


class TrendPoint(BaseModel):
    date: datetime
    scores: PerformanceScore


class DashboardResponse(BaseModel):
    profile_summary: Dict[str, Any]
    stats: PlacementStats
    recent_activity: List[RecentActivityItem] = []
    performance: PerformanceScore
    trends: List[TrendPoint] = []
