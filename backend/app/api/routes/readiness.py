from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.common import APIResponse
from app.services.readiness_service import ReadinessService

router = APIRouter()


@router.get("", response_model=APIResponse)
async def get_overall_readiness(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReadinessService(db)
    readiness = await service.get_overall_readiness(current_user["sub"])
    return APIResponse(data=readiness)


@router.get("/{company_id}", response_model=APIResponse)
async def get_company_readiness(
    company_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ReadinessService(db)
    readiness = await service.get_company_readiness(current_user["sub"], company_id)
    return APIResponse(data=readiness)
