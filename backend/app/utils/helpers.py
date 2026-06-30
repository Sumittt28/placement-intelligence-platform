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


def to_uuid(val: Any) -> uuid.UUID:
    """Convert a string (or UUID) to a uuid.UUID object.
    Raises HTTPException 400 if the string is not a valid UUID."""
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except (ValueError, AttributeError):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Invalid ID format: {val}")
