from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.common import APIResponse
from app.services.recommendation_service import RecommendationService

router = APIRouter()


@router.get("", response_model=APIResponse)
async def get_recommendations(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = RecommendationService(db)
    recs = await service.get_recommendations(current_user["sub"])
    return APIResponse(data=recs)


@router.put("/{rec_id}/complete", response_model=APIResponse)
async def mark_complete(
    rec_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = RecommendationService(db)
    result = await service.mark_complete(rec_id, current_user["sub"])
    return APIResponse(data=result)
