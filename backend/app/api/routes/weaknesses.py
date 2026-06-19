from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timezone
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.common import APIResponse
from app.models.intelligence import Weakness

router = APIRouter()


@router.get("", response_model=APIResponse)
async def get_weaknesses(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all weaknesses for the current user."""
    result = await db.execute(
        select(Weakness)
        .where(Weakness.user_id == current_user["sub"])
        .order_by(Weakness.last_detected.desc())
    )
    weaknesses = result.scalars().all()

    return APIResponse(data=[
        {
            "id": str(w.id),
            "topic": w.topic,
            "category": w.category,
            "occurrence_count": w.occurrence_count,
            "severity": w.severity,
            "sources": w.sources or [],
            "recommended_actions": w.recommended_actions or [],
            "is_resolved": w.is_resolved,
            "first_detected": w.first_detected.isoformat() if w.first_detected else None,
            "last_detected": w.last_detected.isoformat() if w.last_detected else None,
        }
        for w in weaknesses
    ])


@router.put("/{weakness_id}/resolve", response_model=APIResponse)
async def resolve_weakness(
    weakness_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark a weakness as resolved."""
    result = await db.execute(
        select(Weakness).where(
            Weakness.id == weakness_id,
            Weakness.user_id == current_user["sub"],
        )
    )
    weakness = result.scalar_one_or_none()

    if not weakness:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Weakness not found")

    weakness.is_resolved = True
    await db.flush()

    return APIResponse(data={
        "id": str(weakness.id),
        "topic": weakness.topic,
        "is_resolved": True,
    })
