from fastapi import APIRouter, Depends
from app.middleware.rate_limiter import rate_limit_check
from app.api.routes import (
    auth,
    users,
    dashboard,
    companies,
    interview_experiences,
    mock_interviews,
    evaluations,
    resume,
    recommendations,
    readiness,
    knowledge_base,
    voice,
    admin,
)

api_router = APIRouter(dependencies=[Depends(rate_limit_check)])

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(companies.router, prefix="/companies", tags=["Companies"])
api_router.include_router(interview_experiences.router, prefix="/experiences", tags=["Interview Experiences"])
api_router.include_router(mock_interviews.router, prefix="/interviews", tags=["Mock Interviews"])
api_router.include_router(evaluations.router, prefix="/evaluations", tags=["Evaluations"])
api_router.include_router(resume.router, prefix="/resume", tags=["Resume"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
api_router.include_router(readiness.router, prefix="/readiness", tags=["Readiness"])
api_router.include_router(knowledge_base.router, prefix="/search", tags=["Knowledge Base"])
api_router.include_router(voice.router, prefix="/voice", tags=["Voice"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
