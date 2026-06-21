from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.mock_interview import StartInterviewRequest, SubmitAnswerRequest
from app.schemas.common import APIResponse
from app.services.mock_interview_service import MockInterviewService

router = APIRouter()


@router.post("/start", response_model=APIResponse)
async def start_interview(
    request: StartInterviewRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MockInterviewService(db)
    result = await service.start_interview(current_user["sub"], request)
    return APIResponse(data=result)


@router.post("/{interview_id}/answer", response_model=APIResponse)
async def submit_answer(
    interview_id: str,
    request: SubmitAnswerRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MockInterviewService(db)
    result = await service.submit_answer(interview_id, current_user["sub"], request)
    return APIResponse(data=result)


@router.post("/{interview_id}/complete", response_model=APIResponse)
async def complete_interview(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MockInterviewService(db)
    result = await service.complete_interview(interview_id, current_user["sub"])
    return APIResponse(data=result)


@router.get("", response_model=APIResponse)
async def list_interviews(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MockInterviewService(db)
    interviews = await service.list_interviews(current_user["sub"])
    return APIResponse(data=interviews)


@router.get("/{interview_id}", response_model=APIResponse)
async def get_interview(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MockInterviewService(db)
    interview = await service.get_interview(interview_id, user_id=current_user["sub"])
    return APIResponse(data=interview)


@router.get("/{interview_id}/replay", response_model=APIResponse)
async def get_replay(
    interview_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MockInterviewService(db)
    replay = await service.get_replay(interview_id, user_id=current_user["sub"])
    return APIResponse(data=replay)
