from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.user import ProfileUpdate, UserResponse
from app.schemas.common import APIResponse
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=APIResponse)
async def get_me(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user_with_profile(current_user["sub"])
    return APIResponse(data=user)


@router.put("/me/profile", response_model=APIResponse)
async def update_profile(
    request: ProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = UserService(db)
    profile = await service.update_profile(current_user["sub"], request)
    return APIResponse(data=profile)
