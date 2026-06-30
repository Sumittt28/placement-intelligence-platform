from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class ScoreDimension(BaseModel):
    score: float
    reason: str


class EvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    interview_id: str
    communication: ScoreDimension
    technical: ScoreDimension
    confidence: ScoreDimension
    problem_solving: ScoreDimension
    behavioral: ScoreDimension
    project: ScoreDimension
    overall_score: float
    overall_feedback: str
    strengths: List[str] = []
    improvements: List[str] = []
    created_at: datetime

    @classmethod
    def from_db(cls, eval_obj):
        return cls(
            id=str(eval_obj.id),
            interview_id=str(eval_obj.interview_id),
            communication=ScoreDimension(score=eval_obj.communication_score, reason=eval_obj.communication_reason),
            technical=ScoreDimension(score=eval_obj.technical_score, reason=eval_obj.technical_reason),
            confidence=ScoreDimension(score=eval_obj.confidence_score, reason=eval_obj.confidence_reason),
            problem_solving=ScoreDimension(score=eval_obj.problem_solving_score, reason=eval_obj.problem_solving_reason),
            behavioral=ScoreDimension(score=eval_obj.behavioral_score, reason=eval_obj.behavioral_reason),
            project=ScoreDimension(score=eval_obj.project_score, reason=eval_obj.project_reason),
            overall_score=eval_obj.overall_score,
            overall_feedback=eval_obj.overall_feedback,
            strengths=eval_obj.strengths or [],
            improvements=eval_obj.improvements or [],
            created_at=eval_obj.created_at,
        )
