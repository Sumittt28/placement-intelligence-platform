from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, GoogleAuthRequest, TokenResponse
from app.schemas.common import APIResponse
from app.core.security import get_current_user, create_access_token
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=APIResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.register(request)
    # Log activity (best-effort — must not break registration)
    try:
        from app.middleware.activity_logger import log_activity
        await log_activity(db, result["user"]["id"], "user_registered", "auth")
    except Exception:
        pass  # Activity logging failure must never roll back auth
    return APIResponse(data=result)


@router.post("/login", response_model=APIResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.login(request)
    # Log activity (best-effort — must not break login)
    try:
        from app.middleware.activity_logger import log_activity
        await log_activity(db, result["user"]["id"], "user_logged_in", "auth")
    except Exception:
        pass
    return APIResponse(data=result)


@router.post("/google", response_model=APIResponse)
async def google_auth(request: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    result = await service.google_auth(request)
    return APIResponse(data=result)


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh JWT token for authenticated user."""
    new_token = create_access_token({
        "sub": current_user["sub"],
        "email": current_user["email"],
        "role": current_user.get("role", "student"),
    })
    return APIResponse(data={"access_token": new_token, "token_type": "bearer"})


@router.post("/logout", response_model=APIResponse)
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout (client-side token removal). Server acknowledges."""
    return APIResponse(data={"message": "Logged out successfully"})
