"""Activity logging utility for tracking user actions."""
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.intelligence import ActivityLog
from app.utils.helpers import to_uuid

logger = logging.getLogger("pip.activity")


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
            user_id=to_uuid(user_id),
            action=action,
            resource=resource,
            resource_id=to_uuid(resource_id) if resource_id else None,
            metadata_=metadata or {},
        )
        db.add(activity)
        await db.flush()
        logger.debug(f"Activity logged: user={user_id} action={action} resource={resource}")
    except Exception as e:
        logger.warning(f"Failed to log activity: {e}")
        # Activity logging should never break the main request
