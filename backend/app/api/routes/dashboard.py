from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.common import APIResponse
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("", response_model=APIResponse)
async def get_dashboard(current_user: dict = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    service = DashboardService(db)
    data = await service.get_dashboard_data(current_user["sub"])
    return APIResponse(data=data)
