from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.common import APIResponse
from app.services.mock_interview_service import MockInterviewService

router = APIRouter()


@router.get("/{interview_id}", response_model=APIResponse)
async def get_evaluation(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MockInterviewService(db)
    evaluation = await service.get_evaluation(interview_id, user_id=current_user["sub"])
    return APIResponse(data=evaluation)
