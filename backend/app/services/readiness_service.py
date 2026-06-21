from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.mock_interview import Evaluation, MockInterview
from app.models.company import Company, CompanyAnalytics
from app.models.intelligence import Weakness
from app.models.user import Profile
from app.utils.cache import ttl_cache
import json


class ReadinessService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overall_readiness(self, user_id: str) -> dict:
        # Cache readiness for 2 minutes
        cache_key = f"readiness:{user_id}"
        cached = ttl_cache.get(cache_key)
        if cached:
            return cached

        # Get target companies from profile
        profile_result = await self.db.execute(select(Profile).where(Profile.user_id == user_id))
        profile = profile_result.scalar_one_or_none()

        target_ids = []
        if profile and profile.target_companies:
            try:
                targets = json.loads(profile.target_companies) if isinstance(profile.target_companies, str) else profile.target_companies
                target_ids = targets if isinstance(targets, list) else []
            except (json.JSONDecodeError, TypeError):
                pass

        # Get avg scores
        avg_scores = await self._get_avg_scores(user_id)
        overall = sum(avg_scores.values()) / len(avg_scores) * 10 if avg_scores and any(avg_scores.values()) else 0

        companies = []
        for company_id in target_ids[:5]:
            try:
                readiness = await self.get_company_readiness(user_id, company_id)
                companies.append(readiness)
            except Exception:
                pass

        result = {
            "overall_readiness": round(overall, 1),
            "companies": companies,
        }
        ttl_cache.set(cache_key, result, ttl=120)
        return result

    async def get_company_readiness(self, user_id: str, company_id: str) -> dict:
        # Get company
        company_result = await self.db.execute(select(Company).where(Company.id == company_id))
        company = company_result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        # Get student's avg scores
        avg_scores = await self._get_avg_scores(user_id)

        # Get company requirements (from analytics)
        analytics_result = await self.db.execute(
            select(CompanyAnalytics).where(CompanyAnalytics.company_id == company_id)
        )
        analytics = analytics_result.scalar_one_or_none()

        # Get active weaknesses
        weakness_result = await self.db.execute(
            select(Weakness).where(Weakness.user_id == user_id, Weakness.is_resolved == False)
        )
        weaknesses = weakness_result.scalars().all()
        weak_topics = {w.topic for w in weaknesses}

        # Calculate readiness per dimension
        dimensions = []
        dim_names = ["communication", "technical", "problem_solving", "behavioral", "project"]
        for dim in dim_names:
            score = avg_scores.get(dim, 0)
            gap = ""
            if score < 5:
                gap = f"Needs significant improvement in {dim}"
            elif score < 7:
                gap = f"Good but can improve {dim}"
            else:
                gap = f"Strong in {dim}"

            if dim in weak_topics:
                gap += " (recurring weakness detected)"

            dimensions.append({
                "name": dim,
                "score": score,
                "gap": gap,
            })

        # Readiness percent = average of dimension scores / 10 * 100
        readiness_pct = sum(d["score"] for d in dimensions) / len(dimensions) * 10 if dimensions else 0

        recommendations = []
        for w in weaknesses[:3]:
            recommendations.append(f"Improve {w.topic} - appeared in {w.occurrence_count} interviews")

        return {
            "company_id": str(company.id),
            "company_name": company.name,
            "readiness_percent": round(readiness_pct, 1),
            "dimensions": dimensions,
            "recommendations": recommendations,
        }

    async def _get_avg_scores(self, user_id: str) -> dict:
        eval_result = await self.db.execute(
            select(Evaluation)
            .join(MockInterview)
            .where(MockInterview.user_id == user_id)
            .order_by(Evaluation.created_at.desc())
            .limit(10)
        )
        evals = eval_result.scalars().all()

        if not evals:
            return {"communication": 0, "technical": 0, "problem_solving": 0, "behavioral": 0, "project": 0}

        n = len(evals)
        return {
            "communication": round(sum(e.communication_score for e in evals) / n, 1),
            "technical": round(sum(e.technical_score for e in evals) / n, 1),
            "problem_solving": round(sum(e.problem_solving_score for e in evals) / n, 1),
            "behavioral": round(sum(e.behavioral_score for e in evals) / n, 1),
            "project": round(sum(e.project_score for e in evals) / n, 1),
        }
