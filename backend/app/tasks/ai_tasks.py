"""
Celery tasks for async AI processing.
These tasks are triggered after experience submissions, interview completions, etc.
"""
import asyncio
import logging
from app.worker import celery_app
from app.utils.helpers import to_uuid

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async code in Celery sync tasks."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def extract_experience_metadata(self, experience_id: str, questions: list, role: str, company_name: str):
    """
    Async AI task: Extract structured metadata from a submitted interview experience.
    Triggered after a new experience is submitted.
    """
    try:
        logger.info(f"Extracting metadata for experience {experience_id}")

        async def _extract():
            from app.services.ai.knowledge_extractor import KnowledgeExtractor
            from app.db.session import async_session_factory
            from sqlalchemy import update
            from app.models.interview_experience import InterviewExperience

            extractor = KnowledgeExtractor()
            metadata = await extractor.extract(questions=questions, role=role, company_name=company_name)

            async with async_session_factory() as session:
                await session.execute(
                    update(InterviewExperience)
                    .where(InterviewExperience.id == to_uuid(experience_id))
                    .values(ai_extracted=metadata)
                )

            logger.info(f"Metadata extracted for experience {experience_id}: {list(metadata.keys())}")
            return metadata

        return run_async(_extract())

    except Exception as exc:
        logger.error(f"Error extracting metadata for {experience_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def generate_question_embeddings(self, experience_id: str, questions: list):
    """
    Async AI task: Generate embeddings for interview questions using pgvector.
    Triggered after experience metadata extraction.
    """
    try:
        logger.info(f"Generating embeddings for experience {experience_id}")

        async def _embed():
            from app.services.ai.gemini_client import GeminiClient
            from app.db.session import async_session_factory
            from sqlalchemy import update
            from app.models.interview_experience import InterviewQuestion

            client = GeminiClient()

            async with async_session_factory() as session:
                for q in questions:
                    question_id = q.get("id")
                    question_text = q.get("question_text", "")
                    if not question_id or not question_text:
                        continue

                    # Generate embedding via Gemini
                    try:
                        import google.generativeai as genai
                        embedding_result = genai.embed_content(
                            model="models/text-embedding-004",
                            content=question_text,
                        )
                        embedding = embedding_result.get("embedding", [])
                        if embedding:
                            await session.execute(
                                update(InterviewQuestion)
                                .where(InterviewQuestion.id == to_uuid(question_id))
                                .values(embedding=embedding)
                            )
                    except Exception as e:
                        logger.warning(f"Embedding failed for question {question_id}: {e}")


            logger.info(f"Embeddings generated for experience {experience_id}")

        return run_async(_embed())

    except Exception as exc:
        logger.error(f"Error generating embeddings for {experience_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def detect_weaknesses_task(self, user_id: str, interview_id: str, evaluation_data: dict):
    """
    Async AI task: Detect and track weaknesses from evaluation results.
    Triggered after interview evaluation is completed.
    """
    try:
        logger.info(f"Detecting weaknesses for user {user_id} from interview {interview_id}")

        async def _detect():
            from app.services.ai.evaluator import Evaluator
            from app.db.session import async_session_factory
            from app.models.intelligence import Weakness
            from sqlalchemy import select

            evaluator = Evaluator()
            weak_areas = await evaluator.detect_weaknesses(evaluation_data, "general")
            uid = to_uuid(user_id)

            async with async_session_factory() as session:
                for area in weak_areas:
                    # Check if weakness already exists for this user+topic
                    result = await session.execute(
                        select(Weakness).where(
                            Weakness.user_id == uid,
                            Weakness.topic == area["topic"],
                            Weakness.is_resolved.is_(False),
                        )
                    )
                    existing = result.scalar_one_or_none()

                    if existing:
                        existing.occurrence_count += 1
                        existing.last_detected = __import__("datetime").datetime.now(
                            __import__("datetime").timezone.utc
                        )
                        # Create new list to ensure SQLAlchemy JSONB change detection
                        existing.sources = (existing.sources or []) + [interview_id]
                        # Update severity
                        if existing.occurrence_count >= 5:
                            existing.severity = "high"
                        elif existing.occurrence_count >= 3:
                            existing.severity = "medium"
                    else:
                        weakness = Weakness(
                            user_id=uid,
                            topic=area["topic"],
                            category=area.get("category", "technical"),
                            occurrence_count=1,
                            severity="low",
                            sources=[interview_id],
                            recommended_actions=[
                                f"Practice {area['topic']} questions",
                                f"Take a {area['topic']}-focused mock interview",
                            ],
                        )
                        session.add(weakness)


            logger.info(f"Weaknesses detected for user {user_id}: {[a['topic'] for a in weak_areas]}")

        return run_async(_detect())

    except Exception as exc:
        logger.error(f"Error detecting weaknesses for {user_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def regenerate_recommendations_task(self, user_id: str):
    """
    Async AI task: Regenerate personalized recommendations.
    Triggered after mock interview or experience submission.
    """
    try:
        logger.info(f"Regenerating recommendations for user {user_id}")

        async def _regen():
            from app.services.ai.recommendation_engine import RecommendationEngine
            from app.db.session import async_session_factory
            from app.models.intelligence import ResumeData, Weakness, Recommendation
            from sqlalchemy import select, delete

            engine = RecommendationEngine()

            uid = to_uuid(user_id)

            async with async_session_factory() as session:
                # Load resume data
                res = await session.execute(
                    select(ResumeData).where(ResumeData.user_id == uid)
                )
                resume = res.scalar_one_or_none()
                resume_data = {}
                if resume:
                    resume_data = {
                        "skills": resume.skills or [],
                        "technologies": resume.technologies or [],
                    }

                # Load weaknesses
                res = await session.execute(
                    select(Weakness).where(
                        Weakness.user_id == uid,
                        Weakness.is_resolved.is_(False),
                    )
                )
                weaknesses = [
                    {"topic": w.topic, "severity": w.severity, "count": w.occurrence_count}
                    for w in res.scalars().all()
                ]

                # Generate new recommendations
                recs = await engine.generate_recommendations(
                    resume_data=resume_data,
                    weaknesses=weaknesses,
                )

                # Delete old incomplete recommendations
                await session.execute(
                    delete(Recommendation).where(
                        Recommendation.user_id == uid,
                        Recommendation.is_completed.is_(False),
                    )
                )

                # Insert new ones
                for rec in recs:
                    session.add(Recommendation(
                        user_id=uid,
                        type=rec.get("type", "topic"),
                        title=rec.get("title", "Study recommendation"),
                        description=rec.get("description", ""),
                        priority=rec.get("priority", 50),
                    ))


            logger.info(f"Recommendations regenerated for user {user_id}: {len(recs)} items")

        return run_async(_regen())

    except Exception as exc:
        logger.error(f"Error regenerating recommendations for {user_id}: {exc}")
        raise self.retry(exc=exc)
