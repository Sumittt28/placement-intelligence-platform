from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.common import APIResponse
from app.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter()


@router.get("", response_model=APIResponse)
async def search_knowledge_base(
    q: str = Query(..., min_length=1),
    type: str = Query(None),
    company: str = Query(None),
    round_type: str = Query(None),
    difficulty: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = KnowledgeBaseService(db)
    results = await service.search(
        query=q, search_type=type, company=company,
        round_type=round_type, difficulty=difficulty,
        page=page, limit=limit,
    )
    return APIResponse(data=results)
