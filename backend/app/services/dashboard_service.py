from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User, Profile
from app.models.interview_experience import InterviewExperience
from app.models.mock_interview import MockInterview, Evaluation
from app.models.intelligence import ActivityLog


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_data(self, user_id: str) -> dict:
        # Profile summary
        profile_result = await self.db.execute(select(Profile).where(Profile.user_id == user_id))
        profile = profile_result.scalar_one_or_none()

        profile_summary = {
            "full_name": profile.full_name if profile else "",
            "batch": profile.batch if profile else None,
            "resume_status": "uploaded" if (profile and profile.resume_url) else "not_uploaded",
            "target_companies": ", ".join(profile.target_companies) if (profile and profile.target_companies) else "Not set",
        }

        # Stats
        exp_count_result = await self.db.execute(
            select(func.count(InterviewExperience.id)).where(InterviewExperience.user_id == user_id)
        )
        exp_count_val = exp_count_result.scalar() or 0

        mock_count_result = await self.db.execute(
            select(func.count(MockInterview.id)).where(
                MockInterview.user_id == user_id, MockInterview.status == "completed"
            )
        )
        mock_count_val = mock_count_result.scalar() or 0

        stats = {
            "interviews_attempted": exp_count_val,
            "ai_interviews_completed": mock_count_val,
            "contributions_submitted": exp_count_val,
            "company_reports_viewed": 0,
        }

        # Recent activity
        activity_result = await self.db.execute(
            select(ActivityLog)
            .where(ActivityLog.user_id == user_id)
            .order_by(ActivityLog.created_at.desc())
            .limit(10)
        )
        activities = activity_result.scalars().all()
        recent_activity = [
            {
                "action": a.action,
                "resource": a.resource,
                "resource_id": str(a.resource_id) if a.resource_id else None,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in activities
        ]

        # Performance overview (avg of completed evaluations)
        eval_result = await self.db.execute(
            select(Evaluation)
            .join(MockInterview)
            .where(MockInterview.user_id == user_id)
            .order_by(Evaluation.created_at.desc())
            .limit(20)
        )
        evals = eval_result.scalars().all()

        performance = {"communication": 0, "technical_depth": 0, "problem_solving": 0, "behavioral": 0, "project_discussions": 0}
        if evals:
            n = len(evals)
            performance["communication"] = round(sum(e.communication_score for e in evals) / n, 1)
            performance["technical_depth"] = round(sum(e.technical_score for e in evals) / n, 1)
            performance["problem_solving"] = round(sum(e.problem_solving_score for e in evals) / n, 1)
            performance["behavioral"] = round(sum(e.behavioral_score for e in evals) / n, 1)
            performance["project_discussions"] = round(sum(e.project_score for e in evals) / n, 1)

        # Trends (last 10 interviews scores over time)
        trends = []
        for e in reversed(evals[:10]):
            trends.append({
                "date": e.created_at.isoformat() if e.created_at else None,
                "scores": {
                    "communication": e.communication_score,
                    "technical_depth": e.technical_score,
                    "problem_solving": e.problem_solving_score,
                    "behavioral": e.behavioral_score,
                    "project_discussions": e.project_score,
                },
            })

        return {
            "profile_summary": profile_summary,
            "stats": stats,
            "recent_activity": recent_activity,
            "performance": performance,
            "trends": trends,
        }

    async def get_platform_analytics(self) -> dict:
        """Admin-only platform-wide analytics."""
        total_users = await self.db.execute(select(func.count(User.id)))
        total_experiences = await self.db.execute(select(func.count(InterviewExperience.id)))
        total_interviews = await self.db.execute(select(func.count(MockInterview.id)))

        return {
            "total_users": total_users.scalar() or 0,
            "total_experiences": total_experiences.scalar() or 0,
            "total_mock_interviews": total_interviews.scalar() or 0,
        }
