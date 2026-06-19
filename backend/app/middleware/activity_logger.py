"""Activity logging utility for tracking user actions."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.intelligence import ActivityLog

logger = logging.getLogger("pip.activity")

# Map of route patterns to action descriptions
ROUTE_ACTIONS = {
    ("POST", "/auth/register"): "user_registered",
    ("POST", "/auth/login"): "user_logged_in",
    ("POST", "/experiences"): "experience_submitted",
    ("POST", "/interviews/start"): "mock_interview_started",
    ("POST", "/resume/upload"): "resume_uploaded",
    ("GET", "/companies/"): "company_viewed",
    ("GET", "/dashboard"): "dashboard_viewed",
    ("GET", "/readiness"): "readiness_checked",
    ("GET", "/search"): "knowledge_base_searched",
}


async def log_activity(
    db: AsyncSession,
    user_id: str,
    action: str,
    resource: str = None,
    resource_id: str = None,
    metadata: dict = None,
):
    """Log a user activity to the database."""
    try:
        activity = ActivityLog(
            user_id=user_id,
            action=action,
            resource=resource,
            resource_id=resource_id,
            metadata_=metadata or {},
        )
        db.add(activity)
        await db.flush()
        logger.debug(f"Activity logged: user={user_id} action={action} resource={resource}")
    except Exception as e:
        logger.warning(f"Failed to log activity: {e}")
        # Activity logging should never break the main request
