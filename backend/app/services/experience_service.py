import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.interview_experience import InterviewExperience, InterviewQuestion, InterviewOutcome
from app.models.company import Company
from app.schemas.interview_experience import ExperienceCreate


class ExperienceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_experience(self, user_id: str, request: ExperienceCreate) -> dict:
        # Verify company exists
        company_result = await self.db.execute(select(Company).where(Company.id == request.company_id))
        company = company_result.scalar_one_or_none()
        if not company:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        # Create experience
        experience = InterviewExperience(
            user_id=user_id,
            company_id=request.company_id,
            role=request.role,
            interview_date=request.interview_date,
            round_type=request.round_type.value,
            difficulty=request.difficulty.value,
            outcome=request.outcome.value,
            student_notes=request.student_notes,
        )
        self.db.add(experience)
        await self.db.flush()

        # Create questions
        questions_data = []
        for q in request.questions:
            question = InterviewQuestion(
                experience_id=experience.id,
                topic=q.topic,
                question_text=q.question_text,
                could_answer=q.could_answer.value,
            )
            self.db.add(question)
            questions_data.append({"topic": q.topic, "question_text": q.question_text, "could_answer": q.could_answer.value})
        await self.db.flush()

        # Create outcome record
        is_success = request.outcome.value == "Selected"
        outcome = InterviewOutcome(
            experience_id=experience.id,
            company_id=request.company_id,
            success=is_success,
            topics=[q.topic for q in request.questions],
        )
        self.db.add(outcome)
        await self.db.flush()

        # Trigger async AI processing (knowledge extraction + analytics recompute)
        # In production, this would be a Celery task
        try:
            from app.services.ai.knowledge_extractor import KnowledgeExtractor
            extractor = KnowledgeExtractor()
            ai_data = await extractor.extract(questions_data, request.role, company.name)
            experience.ai_extracted = ai_data
            await self.db.flush()
        except Exception:
            pass  # AI extraction is best-effort

        # Recompute company analytics
        try:
            from app.services.company_service import CompanyService
            company_svc = CompanyService(self.db)
            await company_svc.recompute_analytics(request.company_id)
        except Exception:
            pass

        return await self._serialize_experience(experience)

    async def list_experiences(self, user_id: str, page: int, limit: int) -> dict:
        offset = (page - 1) * limit

        total_result = await self.db.execute(
            select(func.count(InterviewExperience.id)).where(InterviewExperience.user_id == user_id)
        )
        total = total_result.scalar() or 0

        result = await self.db.execute(
            select(InterviewExperience)
            .options(selectinload(InterviewExperience.questions))
            .where(InterviewExperience.user_id == user_id)
            .order_by(InterviewExperience.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        experiences = result.scalars().all()

        return {
            "experiences": [await self._serialize_experience(e) for e in experiences],
            "total": total,
            "page": page,
            "limit": limit,
        }

    async def get_experience(self, experience_id: str) -> dict:
        result = await self.db.execute(
            select(InterviewExperience)
            .options(selectinload(InterviewExperience.questions))
            .where(InterviewExperience.id == experience_id)
        )
        experience = result.scalar_one_or_none()
        if not experience:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
        return await self._serialize_experience(experience)

    async def delete_experience(self, experience_id: str, user_id: str):
        result = await self.db.execute(
            select(InterviewExperience).where(
                InterviewExperience.id == experience_id,
                InterviewExperience.user_id == user_id,
            )
        )
        experience = result.scalar_one_or_none()
        if not experience:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
        await self.db.delete(experience)

    async def list_all_experiences(self, status_filter: str = None) -> list:
        """Admin: list all experiences."""
        query = select(InterviewExperience).options(selectinload(InterviewExperience.questions))
        if status_filter == "flagged":
            query = query.where(InterviewExperience.is_flagged == True)
        elif status_filter == "pending":
            query = query.where(InterviewExperience.is_approved == False)
        query = query.order_by(InterviewExperience.created_at.desc())
        result = await self.db.execute(query)
        return [await self._serialize_experience(e) for e in result.scalars().all()]

    async def approve_experience(self, exp_id: str) -> dict:
        result = await self.db.execute(select(InterviewExperience).where(InterviewExperience.id == exp_id))
        exp = result.scalar_one_or_none()
        if not exp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
        exp.is_approved = True
        exp.is_flagged = False
        await self.db.flush()
        return {"id": str(exp.id), "approved": True}

    async def flag_experience(self, exp_id: str, reason: str) -> dict:
        result = await self.db.execute(select(InterviewExperience).where(InterviewExperience.id == exp_id))
        exp = result.scalar_one_or_none()
        if not exp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
        exp.is_flagged = True
        await self.db.flush()
        return {"id": str(exp.id), "flagged": True, "reason": reason}

    async def _serialize_experience(self, exp: InterviewExperience) -> dict:
        # Get company name
        company_name = None
        if exp.company_id:
            c_result = await self.db.execute(select(Company.name).where(Company.id == exp.company_id))
            company_name = c_result.scalar_one_or_none()

        questions = []
        if hasattr(exp, 'questions') and exp.questions:
            questions = [
                {
                    "id": str(q.id),
                    "topic": q.topic,
                    "question_text": q.question_text,
                    "could_answer": q.could_answer,
                    "ai_tags": q.ai_tags,
                    "created_at": q.created_at.isoformat() if q.created_at else None,
                }
                for q in exp.questions
            ]

        return {
            "id": str(exp.id),
            "user_id": str(exp.user_id),
            "company_id": str(exp.company_id),
            "company_name": company_name,
            "role": exp.role,
            "interview_date": exp.interview_date.isoformat() if exp.interview_date else None,
            "round_type": exp.round_type,
            "difficulty": exp.difficulty,
            "outcome": exp.outcome,
            "student_notes": exp.student_notes,
            "ai_extracted": exp.ai_extracted,
            "is_approved": exp.is_approved,
            "questions": questions,
            "created_at": exp.created_at.isoformat() if exp.created_at else None,
        }
