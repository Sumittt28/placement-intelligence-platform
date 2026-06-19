from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import require_admin
from app.schemas.common import APIResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class FlagRequest(BaseModel):
    reason: str


@router.get("/experiences", response_model=APIResponse)
async def list_experiences_admin(
    status: str = Query(None),
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.services.experience_service import ExperienceService
    service = ExperienceService(db)
    experiences = await service.list_all_experiences(status)
    return APIResponse(data=experiences)


@router.put("/experiences/{exp_id}/approve", response_model=APIResponse)
async def approve_experience(
    exp_id: str,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.services.experience_service import ExperienceService
    service = ExperienceService(db)
    result = await service.approve_experience(exp_id)
    return APIResponse(data=result)


@router.put("/experiences/{exp_id}/flag", response_model=APIResponse)
async def flag_experience(
    exp_id: str,
    request: FlagRequest,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.services.experience_service import ExperienceService
    service = ExperienceService(db)
    result = await service.flag_experience(exp_id, request.reason)
    return APIResponse(data=result)


@router.get("/analytics", response_model=APIResponse)
async def get_platform_analytics(
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.services.dashboard_service import DashboardService
    service = DashboardService(db)
    analytics = await service.get_platform_analytics()
    return APIResponse(data=analytics)
