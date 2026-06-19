import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User, Profile, Role, UserRole
from app.schemas.auth import RegisterRequest, LoginRequest, GoogleAuthRequest
from app.core.security import hash_password, verify_password, create_access_token


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_or_create_student_role(self) -> Role:
        result = await self.db.execute(select(Role).where(Role.name == "student"))
        role = result.scalar_one_or_none()
        if not role:
            role = Role(name="student", description="Student user")
            self.db.add(role)
            await self.db.flush()
        return role

    async def _get_or_create_admin_role(self) -> Role:
        result = await self.db.execute(select(Role).where(Role.name == "admin"))
        role = result.scalar_one_or_none()
        if not role:
            role = Role(name="admin", description="Admin user")
            self.db.add(role)
            await self.db.flush()
        return role

    async def register(self, request: RegisterRequest) -> dict:
        # Check existing
        existing = await self.db.execute(select(User).where(User.email == request.email))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        # Create user
        user = User(
            email=request.email,
            hashed_password=hash_password(request.password),
            auth_provider="email",
        )
        self.db.add(user)
        await self.db.flush()

        # Create profile
        profile = Profile(
            user_id=user.id,
            full_name=request.full_name,
            kalvium_id=request.kalvium_id,
            batch=request.batch,
            graduation_year=request.graduation_year,
        )
        self.db.add(profile)

        # Assign student role
        role = await self._get_or_create_student_role()
        user_role = UserRole(user_id=user.id, role_id=role.id)
        self.db.add(user_role)
        await self.db.flush()

        token = create_access_token({"sub": str(user.id), "email": user.email, "role": "student"})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": profile.full_name,
                "role": "student",
            },
        }

    async def login(self, request: LoginRequest) -> dict:
        result = await self.db.execute(select(User).where(User.email == request.email))
        user = result.scalar_one_or_none()
        if not user or not user.hashed_password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        # Get profile and role
        profile_result = await self.db.execute(select(Profile).where(Profile.user_id == user.id))
        profile = profile_result.scalar_one_or_none()

        role_result = await self.db.execute(
            select(Role).join(UserRole).where(UserRole.user_id == user.id)
        )
        role = role_result.scalar_one_or_none()
        role_name = role.name if role else "student"

        token = create_access_token({"sub": str(user.id), "email": user.email, "role": role_name})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": profile.full_name if profile else "",
                "role": role_name,
            },
        }

    async def google_auth(self, request: GoogleAuthRequest) -> dict:
        # Verify Google token via HTTP call
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {request.access_token}"},
            )
            if resp.status_code != 200:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")
            google_user = resp.json()

        email = google_user.get("email")
        name = google_user.get("name", email.split("@")[0])

        # Find or create user
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            user = User(email=email, auth_provider="google", supabase_uid=google_user.get("sub"))
            self.db.add(user)
            await self.db.flush()

            profile = Profile(user_id=user.id, full_name=name)
            self.db.add(profile)

            role = await self._get_or_create_student_role()
            user_role = UserRole(user_id=user.id, role_id=role.id)
            self.db.add(user_role)
            await self.db.flush()

        profile_result = await self.db.execute(select(Profile).where(Profile.user_id == user.id))
        profile = profile_result.scalar_one_or_none()

        role_result = await self.db.execute(
            select(Role).join(UserRole).where(UserRole.user_id == user.id)
        )
        role = role_result.scalar_one_or_none()
        role_name = role.name if role else "student"

        token = create_access_token({"sub": str(user.id), "email": user.email, "role": role_name})
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": profile.full_name if profile else name,
                "role": role_name,
            },
        }
