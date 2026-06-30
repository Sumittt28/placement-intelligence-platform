from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from app.models.user import User, Profile
from app.schemas.user import ProfileUpdate
from app.utils.helpers import to_uuid


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_with_profile(self, user_id: str) -> dict:
        result = await self.db.execute(
            select(User).options(selectinload(User.profile)).where(User.id == to_uuid(user_id))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        profile = user.profile
        target_companies = []
        if profile and profile.target_companies:
            target_companies = profile.target_companies if isinstance(profile.target_companies, list) else []

        return {
            "id": str(user.id),
            "email": user.email,
            "auth_provider": user.auth_provider,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "profile": {
                "id": str(profile.id),
                "user_id": str(profile.user_id),
                "full_name": profile.full_name,
                "kalvium_id": profile.kalvium_id,
                "batch": profile.batch,
                "graduation_year": profile.graduation_year,
                "resume_url": profile.resume_url,
                "linkedin_url": profile.linkedin_url,
                "github_url": profile.github_url,
                "target_companies": target_companies,
                "created_at": profile.created_at.isoformat() if profile.created_at else None,
                "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
            } if profile else None,
        }

    async def update_profile(self, user_id: str, request: ProfileUpdate) -> dict:
        result = await self.db.execute(select(Profile).where(Profile.user_id == to_uuid(user_id)))
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

        update_data = request.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(profile, key, value)

        await self.db.flush()
        return await self.get_user_with_profile(user_id)
