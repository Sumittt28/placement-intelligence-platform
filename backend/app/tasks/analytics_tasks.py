"""
Celery tasks for analytics recomputation.
Triggered after new experience submissions.
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta
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


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def recompute_company_analytics(self, company_id: str):
    """
    Recompute company analytics after a new experience is submitted.
    Applies 90-day time weighting per blueprint specification.
    """
    try:
        logger.info(f"Recomputing analytics for company {company_id}")

        async def _recompute():
            from app.db.session import async_session_factory
            from app.models.company import CompanyAnalytics
            from app.models.interview_experience import InterviewExperience, InterviewQuestion
            from sqlalchemy import select, func

            cid = to_uuid(company_id)

            async with async_session_factory() as session:
                # Get all experiences for this company
                result = await session.execute(
                    select(InterviewExperience).where(
                        InterviewExperience.company_id == cid,
                        InterviewExperience.is_approved.is_(True),
                    )
                )
                experiences = result.scalars().all()

                if not experiences:
                    logger.info(f"No approved experiences for company {company_id}")
                    return

                now = datetime.now(timezone.utc)
                ninety_days_ago = now - timedelta(days=90)

                total_experiences = len(experiences)
                total_questions = 0
                topic_counts = {}
                difficulty_dist = {"Easy": 0, "Medium": 0, "Hard": 0}
                round_dist = {}
                success_count = 0
                weakness_counts = {}

                for exp in experiences:
                    # Time weighting: 1.0 for last 90 days, decayed otherwise
                    exp_date = exp.created_at
                    if exp_date and exp_date.tzinfo is None:
                        exp_date = exp_date.replace(tzinfo=timezone.utc)

                    if exp_date and exp_date >= ninety_days_ago:
                        weight = 1.0
                    else:
                        days_old = (now - (exp_date or now)).days
                        weight = max(0.1, 0.5 * (1 - days_old / 365))

                    # Difficulty distribution
                    diff = exp.difficulty or "Medium"
                    difficulty_dist[diff] = difficulty_dist.get(diff, 0) + weight

                    # Round distribution
                    round_type = exp.round_type or "Other"
                    round_dist[round_type] = round_dist.get(round_type, 0) + weight

                    # Success tracking
                    if exp.outcome == "Selected":
                        success_count += weight

                    # Get questions for this experience
                    q_result = await session.execute(
                        select(InterviewQuestion).where(
                            InterviewQuestion.experience_id == exp.id
                        )
                    )
                    questions = q_result.scalars().all()
                    total_questions += len(questions)

                    for q in questions:
                        topic = q.topic or "general"
                        topic_counts[topic] = topic_counts.get(topic, 0) + weight
                        if q.could_answer in ("No", "Partially"):
                            weakness_counts[topic] = weakness_counts.get(topic, 0) + 1

                # Compute top topics
                sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
                top_topics = [{"topic": t, "count": round(c, 1)} for t, c in sorted_topics[:15]]

                # Compute common weaknesses
                sorted_weaknesses = sorted(weakness_counts.items(), key=lambda x: x[1], reverse=True)
                common_weaknesses = [{"topic": t, "count": c} for t, c in sorted_weaknesses[:10]]

                # Success rate
                success_rate = (success_count / total_experiences * 100) if total_experiences > 0 else 0

                # Compute recent 90-day weight (proportion of data from last 90 days)
                recent_count = sum(1 for e in experiences
                                   if e.created_at and e.created_at.replace(tzinfo=timezone.utc) >= ninety_days_ago)
                recent_90d_weight = recent_count / total_experiences if total_experiences > 0 else 0

                # Upsert analytics
                result = await session.execute(
                    select(CompanyAnalytics).where(CompanyAnalytics.company_id == cid)
                )
                analytics = result.scalar_one_or_none()

                if analytics:
                    analytics.total_experiences = total_experiences
                    analytics.total_questions = total_questions
                    analytics.top_topics = top_topics
                    analytics.difficulty_dist = difficulty_dist
                    analytics.round_dist = round_dist
                    analytics.success_rate = round(success_rate, 1)
                    analytics.common_weaknesses = common_weaknesses
                    analytics.recent_90d_weight = round(recent_90d_weight, 2)
                    analytics.last_computed = now
                    analytics.updated_at = now
                else:
                    analytics = CompanyAnalytics(
                        company_id=cid,
                        total_experiences=total_experiences,
                        total_questions=total_questions,
                        top_topics=top_topics,
                        difficulty_dist=difficulty_dist,
                        round_dist=round_dist,
                        success_rate=round(success_rate, 1),
                        common_weaknesses=common_weaknesses,
                        recent_90d_weight=round(recent_90d_weight, 2),
                        last_computed=now,
                    )
                    session.add(analytics)

            logger.info(
                f"Analytics recomputed for company {company_id}: "
                f"{total_experiences} experiences, {total_questions} questions, "
                f"{round(success_rate, 1)}% success rate"
            )

        return run_async(_recompute())

    except Exception as exc:
        logger.error(f"Error recomputing analytics for {company_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task
def recompute_all_company_analytics():
    """Batch job to recompute analytics for all companies. Run periodically."""
    async def _recompute_all():
        from app.db.session import async_session_factory
        from app.models.company import Company
        from sqlalchemy import select

        async with async_session_factory() as session:
            result = await session.execute(select(Company.id).where(Company.is_active.is_(True)))
            company_ids = [str(row[0]) for row in result.all()]

        for cid in company_ids:
            recompute_company_analytics.delay(cid)

        logger.info(f"Queued analytics recomputation for {len(company_ids)} companies")

    run_async(_recompute_all())
