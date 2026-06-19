from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from app.models.interview_experience import InterviewExperience, InterviewQuestion
from app.models.company import Company


class KnowledgeBaseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self, query: str, search_type: str = None, company: str = None,
        round_type: str = None, difficulty: str = None,
        page: int = 1, limit: int = 20,
    ) -> dict:
        offset = (page - 1) * limit

        # Base query: search in questions
        base_query = (
            select(
                InterviewQuestion.question_text,
                InterviewQuestion.topic,
                Company.name.label("company_name"),
                InterviewExperience.round_type,
                InterviewExperience.difficulty,
                func.count(InterviewQuestion.id).label("frequency"),
            )
            .join(InterviewExperience, InterviewQuestion.experience_id == InterviewExperience.id)
            .join(Company, InterviewExperience.company_id == Company.id)
        )

        # Text search filter
        search_term = f"%{query}%"
        base_query = base_query.where(
            or_(
                InterviewQuestion.question_text.ilike(search_term),
                InterviewQuestion.topic.ilike(search_term),
                Company.name.ilike(search_term),
            )
        )

        # Additional filters
        if company:
            base_query = base_query.where(Company.name.ilike(f"%{company}%"))
        if round_type:
            base_query = base_query.where(InterviewExperience.round_type == round_type)
        if difficulty:
            base_query = base_query.where(InterviewExperience.difficulty == difficulty)

        # Group and order
        base_query = base_query.group_by(
            InterviewQuestion.question_text,
            InterviewQuestion.topic,
            Company.name,
            InterviewExperience.round_type,
            InterviewExperience.difficulty,
        ).order_by(func.count(InterviewQuestion.id).desc())

        # Count total
        from sqlalchemy import text
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Paginate
        base_query = base_query.offset(offset).limit(limit)
        result = await self.db.execute(base_query)
        rows = result.all()

        results = [
            {
                "question_text": r[0],
                "topic": r[1],
                "company_name": r[2],
                "round_type": r[3],
                "difficulty": r[4],
                "frequency": r[5],
            }
            for r in rows
        ]

        return {
            "query": query,
            "results": results,
            "total": total,
        }
