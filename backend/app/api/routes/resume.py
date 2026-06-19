from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.common import APIResponse
from app.services.resume_service import ResumeService

router = APIRouter()


@router.post("/upload", response_model=APIResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    result = await service.upload_and_parse(current_user["sub"], file)
    return APIResponse(data=result)


@router.get("/insights", response_model=APIResponse)
async def get_resume_insights(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    insights = await service.get_insights(current_user["sub"])
    return APIResponse(data=insights)


@router.get("/data", response_model=APIResponse)
async def get_resume_data(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ResumeService(db)
    data = await service.get_resume_data(current_user["sub"])
    return APIResponse(data=data)
