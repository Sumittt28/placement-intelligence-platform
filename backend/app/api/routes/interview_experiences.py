from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.interview_experience import ExperienceCreate
from app.schemas.common import APIResponse
from app.services.experience_service import ExperienceService

router = APIRouter()


@router.post("", response_model=APIResponse)
async def create_experience(
    request: ExperienceCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExperienceService(db)
    experience = await service.create_experience(current_user["sub"], request)
    # Log activity (best-effort — must not break experience submission)
    try:
        from app.middleware.activity_logger import log_activity
        await log_activity(db, current_user["sub"], "experience_submitted", "experience", experience["id"])
    except Exception:
        pass
    return APIResponse(data=experience)


@router.get("", response_model=APIResponse)
async def list_experiences(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExperienceService(db)
    result = await service.list_experiences(current_user["sub"], page, limit)
    return APIResponse(data=result)


@router.get("/{experience_id}", response_model=APIResponse)
async def get_experience(
    experience_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExperienceService(db)
    experience = await service.get_experience(experience_id)
    return APIResponse(data=experience)


@router.put("/{experience_id}", response_model=APIResponse)
async def update_experience(
    experience_id: str,
    request: ExperienceCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExperienceService(db)
    experience = await service.update_experience(experience_id, current_user["sub"], request)
    return APIResponse(data=experience)


@router.delete("/{experience_id}", response_model=APIResponse)
async def delete_experience(
    experience_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExperienceService(db)
    await service.delete_experience(experience_id, current_user["sub"])
    return APIResponse(data={"deleted": True})
