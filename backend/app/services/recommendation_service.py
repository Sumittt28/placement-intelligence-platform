from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.intelligence import Recommendation, Weakness, ResumeData
from app.utils.helpers import to_uuid


class RecommendationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_recommendations(self, user_id: str) -> list:
        uid = to_uuid(user_id)
        # Get existing recommendations
        result = await self.db.execute(
            select(Recommendation)
            .where(Recommendation.user_id == uid, Recommendation.is_completed.is_(False))
            .order_by(Recommendation.priority.desc())
        )
        existing = result.scalars().all()

        if existing:
            return [self._serialize(r) for r in existing]

        # Auto-generate recommendations based on weaknesses
        await self._generate_recommendations(uid)

        result = await self.db.execute(
            select(Recommendation)
            .where(Recommendation.user_id == uid, Recommendation.is_completed.is_(False))
            .order_by(Recommendation.priority.desc())
        )
        return [self._serialize(r) for r in result.scalars().all()]

    async def mark_complete(self, rec_id: str, user_id: str) -> dict:
        result = await self.db.execute(
            select(Recommendation).where(Recommendation.id == to_uuid(rec_id), Recommendation.user_id == to_uuid(user_id))
        )
        rec = result.scalar_one_or_none()
        if not rec:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation not found")
        rec.is_completed = True
        await self.db.flush()
        return {"id": str(rec.id), "completed": True}

    async def _generate_recommendations(self, user_id):
        """Generate recommendations from weaknesses and resume data."""
        # Get weaknesses
        weakness_result = await self.db.execute(
            select(Weakness).where(Weakness.user_id == user_id, Weakness.is_resolved.is_(False))
            .order_by(Weakness.occurrence_count.desc())
        )
        weaknesses = weakness_result.scalars().all()

        for i, w in enumerate(weaknesses[:5]):
            rec = Recommendation(
                user_id=user_id,
                type="topic",
                title=f"Improve {w.topic}",
                description=f"This weakness has appeared {w.occurrence_count} times. Focus on improving your {w.topic} skills.",
                priority=100 - i * 10,
            )
            self.db.add(rec)

        if not weaknesses:
            # Generic recommendations
            from app.services.ai.recommendation_engine import RecommendationEngine
            try:
                engine = RecommendationEngine()
                resume_result = await self.db.execute(select(ResumeData).where(ResumeData.user_id == user_id))  # already UUID
                resume = resume_result.scalar_one_or_none()
                if resume:
                    recs = await engine.generate_recommendations(
                        resume_data={
                            "skills": resume.skills or [],
                            "technologies": resume.technologies or [],
                        },
                    )
                    for i, r in enumerate(recs[:5]):
                        rec = Recommendation(
                            user_id=user_id,
                            type=r.get("type", "topic"),
                            title=r.get("title", "Practice"),
                            description=r.get("description", ""),
                            priority=r.get("priority", 50),
                        )
                        self.db.add(rec)
            except Exception:
                pass

        await self.db.flush()

    def _serialize(self, rec: Recommendation) -> dict:
        return {
            "id": str(rec.id),
            "type": rec.type,
            "title": rec.title,
            "description": rec.description,
            "priority": rec.priority,
            "is_completed": rec.is_completed,
            "created_at": rec.created_at.isoformat() if rec.created_at else None,
        }
