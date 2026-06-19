"""Utility helpers for the backend."""
from datetime import datetime, timezone
from typing import Any, Optional
import uuid


def utc_now() -> datetime:
    """Return current UTC timestamp."""
    return datetime.now(timezone.utc)


def is_valid_uuid(val: str) -> bool:
    """Check if a string is a valid UUID."""
    try:
        uuid.UUID(str(val))
        return True
    except (ValueError, AttributeError):
        return False


def safe_str(val: Any) -> Optional[str]:
    """Safely convert value to string, return None if None."""
    return str(val) if val is not None else None
