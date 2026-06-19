from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user, require_admin
from app.schemas.company import CompanyCreate, CompanyUpdate
from app.schemas.common import APIResponse
from app.services.company_service import CompanyService

router = APIRouter()


@router.get("", response_model=APIResponse)
async def list_companies(
    search: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    companies = await service.list_companies(search)
    return APIResponse(data=companies)


@router.get("/{company_id}", response_model=APIResponse)
async def get_company_intelligence(
    company_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    intelligence = await service.get_company_intelligence(company_id)
    return APIResponse(data=intelligence)


@router.post("", response_model=APIResponse)
async def create_company(
    request: CompanyCreate,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    company = await service.create_company(request)
    return APIResponse(data=company)


@router.put("/{company_id}", response_model=APIResponse)
async def update_company(
    company_id: str,
    request: CompanyUpdate,
    admin: dict = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    service = CompanyService(db)
    company = await service.update_company(company_id, request)
    return APIResponse(data=company)
