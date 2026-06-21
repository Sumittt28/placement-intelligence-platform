from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime, timedelta, timezone
from app.models.company import Company, CompanyAnalytics
from app.models.interview_experience import InterviewExperience, InterviewQuestion
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.utils.cache import ttl_cache


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_companies(self, search: str = None) -> list:
        query = select(Company).where(Company.is_active == True)
        if search:
            query = query.where(Company.name.ilike(f"%{search}%"))
        query = query.order_by(Company.name)
        result = await self.db.execute(query)
        companies = result.scalars().all()

        result_list = [
            {
                "id": str(c.id),
                "name": c.name,
                "industry": c.industry,
                "website": c.website,
                "logo_url": c.logo_url,
                "description": c.description,
                "is_active": c.is_active,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in companies
        ]
        ttl_cache.set(cache_key, result_list, ttl=300)
        return result_list

    async def get_company_intelligence(self, company_id: str) -> dict:
        # Cache company intelligence for 3 minutes
        cache_key = f"company:intel:{company_id}"
        cached = ttl_cache.get(cache_key)
        if cached:
            return cached

        result = await self.db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        # Get analytics
        analytics_result = await self.db.execute(
            select(CompanyAnalytics).where(CompanyAnalytics.company_id == company_id)
        )
        analytics = analytics_result.scalar_one_or_none()

        # Recent experiences
        exp_result = await self.db.execute(
            select(InterviewExperience)
            .where(InterviewExperience.company_id == company_id)
            .order_by(InterviewExperience.interview_date.desc())
            .limit(20)
        )
        experiences = exp_result.scalars().all()

        # Frequently asked questions
        q_result = await self.db.execute(
            select(
                InterviewQuestion.question_text,
                InterviewQuestion.topic,
                func.count(InterviewQuestion.id).label("frequency"),
            )
            .join(InterviewExperience)
            .where(InterviewExperience.company_id == company_id)
            .group_by(InterviewQuestion.question_text, InterviewQuestion.topic)
            .order_by(func.count(InterviewQuestion.id).desc())
            .limit(20)
        )
        faqs = [{"question": r[0], "topic": r[1], "frequency": r[2]} for r in q_result.all()]

        # Questions by round
        round_q_result = await self.db.execute(
            select(
                InterviewExperience.round_type,
                InterviewQuestion.question_text,
                InterviewQuestion.topic,
            )
            .join(InterviewQuestion)
            .where(InterviewExperience.company_id == company_id)
            .order_by(InterviewExperience.round_type)
        )
        questions_by_round = {}
        for round_type, q_text, topic in round_q_result.all():
            if round_type not in questions_by_round:
                questions_by_round[round_type] = []
            questions_by_round[round_type].append({"question": q_text, "topic": topic})

        intel_result = {
            "company": {
                "id": str(company.id),
                "name": company.name,
                "industry": company.industry,
                "website": company.website,
                "logo_url": company.logo_url,
                "description": company.description,
                "is_active": company.is_active,
                "created_at": company.created_at.isoformat() if company.created_at else None,
            },
            "analytics": {
                "total_experiences": analytics.total_experiences if analytics else 0,
                "total_questions": analytics.total_questions if analytics else 0,
                "top_topics": analytics.top_topics if analytics else [],
                "difficulty_dist": analytics.difficulty_dist if analytics else {},
                "round_dist": analytics.round_dist if analytics else {},
                "success_rate": analytics.success_rate if analytics else 0,
                "common_weaknesses": analytics.common_weaknesses if analytics else [],
                "last_computed": analytics.last_computed.isoformat() if analytics and analytics.last_computed else None,
            },
            "recent_experiences": [
                {
                    "id": str(e.id),
                    "role": e.role,
                    "round_type": e.round_type,
                    "difficulty": e.difficulty,
                    "outcome": e.outcome,
                    "interview_date": e.interview_date.isoformat() if e.interview_date else None,
                }
                for e in experiences
            ],
            "frequently_asked_questions": faqs,
            "questions_by_round": questions_by_round,
        }
        ttl_cache.set(cache_key, intel_result, ttl=180)
        return intel_result

    async def create_company(self, request: CompanyCreate) -> dict:
        company = Company(**request.model_dump())
        self.db.add(company)
        # Create empty analytics
        await self.db.flush()
        analytics = CompanyAnalytics(company_id=company.id)
        self.db.add(analytics)
        await self.db.flush()

        # Invalidate company list cache
        ttl_cache.invalidate_prefix("companies:list:")

        return {"id": str(company.id), "name": company.name, "created_at": company.created_at.isoformat()}

    async def update_company(self, company_id: str, request: CompanyUpdate) -> dict:
        result = await self.db.execute(select(Company).where(Company.id == company_id))
        company = result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        for key, value in request.model_dump(exclude_unset=True).items():
            setattr(company, key, value)
        await self.db.flush()

        # Invalidate caches
        ttl_cache.invalidate_prefix("companies:list:")
        ttl_cache.delete(f"company:intel:{company_id}")

        return {"id": str(company.id), "name": company.name, "updated": True}

    async def recompute_analytics(self, company_id: str):
        """Recompute company analytics — called after new experience submission."""
        now = datetime.now(timezone.utc)
        ninety_days_ago = now - timedelta(days=90)

        # Total counts
        total_exp = await self.db.execute(
            select(func.count(InterviewExperience.id)).where(InterviewExperience.company_id == company_id)
        )
        total_q = await self.db.execute(
            select(func.count(InterviewQuestion.id))
            .join(InterviewExperience)
            .where(InterviewExperience.company_id == company_id)
        )

        # Difficulty distribution
        diff_result = await self.db.execute(
            select(InterviewExperience.difficulty, func.count(InterviewExperience.id))
            .where(InterviewExperience.company_id == company_id)
            .group_by(InterviewExperience.difficulty)
        )
        difficulty_dist = {r[0]: r[1] for r in diff_result.all()}

        # Round distribution
        round_result = await self.db.execute(
            select(InterviewExperience.round_type, func.count(InterviewExperience.id))
            .where(InterviewExperience.company_id == company_id)
            .group_by(InterviewExperience.round_type)
        )
        round_dist = {r[0]: r[1] for r in round_result.all()}

        # Success rate
        success_result = await self.db.execute(
            select(func.count(InterviewExperience.id))
            .where(InterviewExperience.company_id == company_id, InterviewExperience.outcome == "Selected")
        )
        total_exp_count = total_exp.scalar() or 0
        success_count = success_result.scalar() or 0
        success_rate = (success_count / total_exp_count * 100) if total_exp_count > 0 else 0

        # Top topics
        topic_result = await self.db.execute(
            select(InterviewQuestion.topic, func.count(InterviewQuestion.id).label("count"))
            .join(InterviewExperience)
            .where(InterviewExperience.company_id == company_id)
            .group_by(InterviewQuestion.topic)
            .order_by(func.count(InterviewQuestion.id).desc())
            .limit(10)
        )
        top_topics = [{"topic": r[0], "count": r[1]} for r in topic_result.all()]

        # Upsert analytics
        analytics_result = await self.db.execute(
            select(CompanyAnalytics).where(CompanyAnalytics.company_id == company_id)
        )
        analytics = analytics_result.scalar_one_or_none()
        if not analytics:
            analytics = CompanyAnalytics(company_id=company_id)
            self.db.add(analytics)

        analytics.total_experiences = total_exp_count
        analytics.total_questions = total_q.scalar() or 0
        analytics.top_topics = top_topics
        analytics.difficulty_dist = difficulty_dist
        analytics.round_dist = round_dist
        analytics.success_rate = round(success_rate, 1)
        analytics.last_computed = now
        await self.db.flush()
