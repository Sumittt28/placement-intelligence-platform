import uuid
import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.mock_interview import MockInterview, MockInterviewQuestion, Evaluation
from app.models.intelligence import ResumeData, Weakness
from app.models.company import CompanyAnalytics
from app.schemas.mock_interview import StartInterviewRequest, SubmitAnswerRequest
from app.schemas.evaluation import EvaluationResponse

logger = logging.getLogger("pip.interviews")


class MockInterviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_interview(self, user_id: str, request: StartInterviewRequest) -> dict:
        # Load context: resume + company analytics + past weaknesses
        context = await self._build_context(user_id, request.company_id)

        # Create interview
        interview = MockInterview(
            user_id=user_id,
            company_id=request.company_id,
            interview_type=request.interview_type.value,
            difficulty=request.difficulty,
            mode=request.mode.value,
            status="in_progress",
            context=context,
        )
        self.db.add(interview)
        await self.db.flush()

        # Generate first question
        from app.services.ai.interview_generator import InterviewGenerator
        generator = InterviewGenerator()
        first_q = await generator.generate_question(
            context=context,
            interview_type=request.interview_type.value,
            difficulty=request.difficulty,
            previous_questions=[],
        )

        question = MockInterviewQuestion(
            interview_id=interview.id,
            sequence_num=1,
            question_text=first_q["question"],
            question_type="main",
            topic=first_q.get("topic", "general"),
        )
        self.db.add(question)
        await self.db.flush()

        return {
            "interview_id": str(interview.id),
            "first_question": {
                "id": str(question.id),
                "sequence_num": 1,
                "question_text": question.question_text,
                "question_type": "main",
                "topic": question.topic,
            },
        }

    async def submit_answer(self, interview_id: str, user_id: str, request: SubmitAnswerRequest) -> dict:
        # Get interview
        result = await self.db.execute(
            select(MockInterview)
            .options(selectinload(MockInterview.questions))
            .where(MockInterview.id == interview_id, MockInterview.user_id == user_id)
        )
        interview = result.scalar_one_or_none()
        if not interview or interview.status != "in_progress":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found or completed")

        # Save answer to current question
        current_q = interview.questions[-1] if interview.questions else None
        if current_q:
            current_q.student_answer = request.answer
            if request.audio_url:
                current_q.audio_url = request.audio_url
            await self.db.flush()

        # Check if we should end (max ~12 questions)
        if len(interview.questions) >= 12:
            return {"question": None, "is_complete": True, "message": "Interview complete. Call /complete to get evaluation."}

        # Generate follow-up or next question
        from app.services.ai.followup_generator import FollowUpGenerator
        generator = FollowUpGenerator()
        transcript = [
            {"question": q.question_text, "answer": q.student_answer or ""}
            for q in interview.questions
        ]
        next_q_data = await generator.generate_followup(
            context=interview.context or {},
            transcript=transcript,
            interview_type=interview.interview_type,
            difficulty=interview.difficulty,
        )

        next_seq = len(interview.questions) + 1
        next_question = MockInterviewQuestion(
            interview_id=interview.id,
            sequence_num=next_seq,
            question_text=next_q_data["question"],
            question_type=next_q_data.get("type", "follow_up"),
            topic=next_q_data.get("topic", "general"),
        )
        self.db.add(next_question)
        await self.db.flush()

        return {
            "question": {
                "id": str(next_question.id),
                "sequence_num": next_seq,
                "question_text": next_question.question_text,
                "question_type": next_question.question_type,
                "topic": next_question.topic,
            },
            "is_complete": False,
            "message": None,
        }

    async def complete_interview(self, interview_id: str, user_id: str) -> dict:
        result = await self.db.execute(
            select(MockInterview)
            .options(selectinload(MockInterview.questions))
            .where(MockInterview.id == interview_id, MockInterview.user_id == user_id)
        )
        interview = result.scalar_one_or_none()
        if not interview:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

        interview.status = "completed"
        interview.completed_at = datetime.now(timezone.utc)
        await self.db.flush()

        # Generate evaluation
        from app.services.ai.evaluator import Evaluator
        evaluator = Evaluator()
        transcript = [
            {"question": q.question_text, "answer": q.student_answer or ""}
            for q in interview.questions
        ]
        eval_data = await evaluator.evaluate(
            transcript=transcript,
            interview_type=interview.interview_type,
        )

        # Save evaluation
        evaluation = Evaluation(
            interview_id=interview.id,
            communication_score=eval_data["communication"]["score"],
            communication_reason=eval_data["communication"]["reason"],
            technical_score=eval_data["technical"]["score"],
            technical_reason=eval_data["technical"]["reason"],
            confidence_score=eval_data["confidence"]["score"],
            confidence_reason=eval_data["confidence"]["reason"],
            problem_solving_score=eval_data["problem_solving"]["score"],
            problem_solving_reason=eval_data["problem_solving"]["reason"],
            behavioral_score=eval_data["behavioral"]["score"],
            behavioral_reason=eval_data["behavioral"]["reason"],
            project_score=eval_data["project"]["score"],
            project_reason=eval_data["project"]["reason"],
            overall_score=eval_data["overall_score"],
            overall_feedback=eval_data["overall_feedback"],
            strengths=eval_data.get("strengths", []),
            improvements=eval_data.get("improvements", []),
        )
        self.db.add(evaluation)

        # Generate ideal answers in parallel (with timeout protection)
        try:
            questions_needing_ideals = [q for q in interview.questions if q.student_answer]
            if questions_needing_ideals:
                async def _gen_ideal(q):
                    try:
                        return q, await evaluator.generate_ideal_answer(q.question_text, interview.interview_type)
                    except Exception:
                        return q, None

                results = await asyncio.wait_for(
                    asyncio.gather(*[_gen_ideal(q) for q in questions_needing_ideals]),
                    timeout=60,  # Total timeout for all ideal answers
                )
                for q, ideal in results:
                    if ideal:
                        q.ideal_answer = ideal
        except asyncio.TimeoutError:
            logger.warning(f"Ideal answer generation timed out for interview {interview_id}")
        except Exception as e:
            logger.warning(f"Ideal answer generation failed for interview {interview_id}: {e}")

        await self.db.flush()

        # Detect weaknesses
        try:
            await self._detect_weaknesses(user_id, interview.id, eval_data)
        except Exception:
            pass

        return EvaluationResponse.from_db(evaluation).model_dump()

    async def list_interviews(self, user_id: str) -> list:
        result = await self.db.execute(
            select(MockInterview)
            .where(MockInterview.user_id == user_id)
            .order_by(MockInterview.created_at.desc())
        )
        interviews = result.scalars().all()
        return [
            {
                "id": str(i.id),
                "interview_type": i.interview_type,
                "difficulty": i.difficulty,
                "mode": i.mode,
                "status": i.status,
                "company_id": str(i.company_id) if i.company_id else None,
                "started_at": i.started_at.isoformat() if i.started_at else None,
                "completed_at": i.completed_at.isoformat() if i.completed_at else None,
            }
            for i in interviews
        ]

    async def get_interview(self, interview_id: str, user_id: str = None) -> dict:
        query = (
            select(MockInterview)
            .options(selectinload(MockInterview.questions))
            .where(MockInterview.id == interview_id)
        )
        if user_id:
            query = query.where(MockInterview.user_id == user_id)
        result = await self.db.execute(query)
        interview = result.scalar_one_or_none()
        if not interview:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

        return {
            "id": str(interview.id),
            "interview_type": interview.interview_type,
            "difficulty": interview.difficulty,
            "mode": interview.mode,
            "status": interview.status,
            "company_id": str(interview.company_id) if interview.company_id else None,
            "started_at": interview.started_at.isoformat() if interview.started_at else None,
            "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
            "questions": [
                {
                    "id": str(q.id),
                    "sequence_num": q.sequence_num,
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "topic": q.topic,
                }
                for q in interview.questions
            ],
        }

    async def get_replay(self, interview_id: str, user_id: str = None) -> dict:
        query = (
            select(MockInterview)
            .options(selectinload(MockInterview.questions), selectinload(MockInterview.evaluation))
            .where(MockInterview.id == interview_id)
        )
        if user_id:
            query = query.where(MockInterview.user_id == user_id)
        result = await self.db.execute(query)
        interview = result.scalar_one_or_none()
        if not interview:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview not found")

        eval_data = None
        if interview.evaluation:
            eval_data = EvaluationResponse.from_db(interview.evaluation).model_dump()

        return {
            "interview": {
                "id": str(interview.id),
                "interview_type": interview.interview_type,
                "difficulty": interview.difficulty,
                "mode": interview.mode,
                "status": interview.status,
                "started_at": interview.started_at.isoformat() if interview.started_at else None,
                "completed_at": interview.completed_at.isoformat() if interview.completed_at else None,
            },
            "questions": [
                {
                    "id": str(q.id),
                    "sequence_num": q.sequence_num,
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "topic": q.topic,
                    "student_answer": q.student_answer,
                    "ideal_answer": q.ideal_answer,
                    "evaluation": q.evaluation,
                    "feedback": q.feedback,
                    "audio_url": q.audio_url,
                }
                for q in interview.questions
            ],
            "evaluation": eval_data,
        }

    async def get_evaluation(self, interview_id: str, user_id: str = None) -> dict:
        query = select(Evaluation).where(Evaluation.interview_id == interview_id)
        if user_id:
            # Join to verify ownership
            query = (
                select(Evaluation)
                .join(MockInterview, Evaluation.interview_id == MockInterview.id)
                .where(Evaluation.interview_id == interview_id, MockInterview.user_id == user_id)
            )
        result = await self.db.execute(query)
        evaluation = result.scalar_one_or_none()
        if not evaluation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evaluation not found")
        return EvaluationResponse.from_db(evaluation).model_dump()

    async def _build_context(self, user_id: str, company_id: str = None) -> dict:
        context = {}

        # Resume data
        resume_result = await self.db.execute(select(ResumeData).where(ResumeData.user_id == user_id))
        resume = resume_result.scalar_one_or_none()
        if resume:
            context["resume"] = {
                "skills": resume.skills or [],
                "projects": resume.projects or [],
                "technologies": resume.technologies or [],
                "domains": resume.domains or [],
            }

        # Company analytics
        if company_id:
            analytics_result = await self.db.execute(
                select(CompanyAnalytics).where(CompanyAnalytics.company_id == company_id)
            )
            analytics = analytics_result.scalar_one_or_none()
            if analytics:
                context["company"] = {
                    "top_topics": analytics.top_topics or [],
                    "difficulty_dist": analytics.difficulty_dist or {},
                    "common_weaknesses": analytics.common_weaknesses or [],
                }

        # Past weaknesses
        weakness_result = await self.db.execute(
            select(Weakness).where(Weakness.user_id == user_id, Weakness.is_resolved == False)
        )
        weaknesses = weakness_result.scalars().all()
        if weaknesses:
            context["weaknesses"] = [{"topic": w.topic, "severity": w.severity} for w in weaknesses]

        return context

    async def _detect_weaknesses(self, user_id: str, interview_id: str, eval_data: dict):
        """Detect recurring weaknesses from evaluation data."""
        weak_dimensions = []
        for dim_name in ["communication", "technical", "confidence", "problem_solving", "behavioral", "project"]:
            if eval_data[dim_name]["score"] < 5.0:
                weak_dimensions.append(dim_name)

        for dim in weak_dimensions:
            # Check if weakness already exists
            result = await self.db.execute(
                select(Weakness).where(
                    Weakness.user_id == user_id,
                    Weakness.topic == dim,
                    Weakness.is_resolved == False,
                )
            )
            existing = result.scalar_one_or_none()

            if existing:
                existing.occurrence_count += 1
                existing.last_detected = datetime.now(timezone.utc)
                sources = existing.sources or []
                sources.append(str(interview_id))
                existing.sources = sources
                # Update severity
                if existing.occurrence_count >= 5:
                    existing.severity = "high"
                elif existing.occurrence_count >= 3:
                    existing.severity = "medium"
            else:
                weakness = Weakness(
                    user_id=user_id,
                    topic=dim,
                    category="technical" if dim in ["technical", "problem_solving"] else "behavioral",
                    occurrence_count=1,
                    severity="low",
                    sources=[str(interview_id)],
                    recommended_actions=[f"Practice {dim} skills", f"Take a focused {dim} mock interview"],
                )
                self.db.add(weakness)

        await self.db.flush()
