from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.common import APIResponse
from app.services.resume_service import ResumeService

router = APIRouter()

# Resume upload constraints
MAX_RESUME_SIZE_MB = 5
MAX_RESUME_SIZE_BYTES = MAX_RESUME_SIZE_MB * 1024 * 1024
ALLOWED_RESUME_TYPES = {
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
}
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".txt", ".docx"}


@router.post("/upload", response_model=APIResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate file extension
    filename = (file.filename or "").lower()
    ext = "." + filename.rsplit(".", 1)[-1] if "." in filename else ""
    if ext not in ALLOWED_RESUME_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{ext}'. Allowed: {', '.join(ALLOWED_RESUME_EXTENSIONS)}",
        )

    # Validate file size (read first MAX+1 bytes to check)
    content = await file.read()
    if len(content) > MAX_RESUME_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_RESUME_SIZE_MB}MB.",
        )
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file uploaded.",
        )

    # Pass already-read bytes directly — avoids unreliable seek() on multipart streams
    service = ResumeService(db)
    result = await service.upload_and_parse(current_user["sub"], content, file.filename or "resume")
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
