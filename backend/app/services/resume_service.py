from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, UploadFile
from app.models.intelligence import ResumeData
from app.models.user import Profile


class ResumeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_and_parse(self, user_id: str, file: UploadFile) -> dict:
        # Read file content
        content = await file.read()
        text = ""

        if file.filename.endswith(".pdf"):
            try:
                import io
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(content))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception:
                text = content.decode("utf-8", errors="ignore")
        else:
            text = content.decode("utf-8", errors="ignore")

        # AI parse
        from app.services.ai.resume_parser import ResumeParser
        import logging
        logger = logging.getLogger("pip.resume")
        parser = ResumeParser()
        parsed = await parser.parse(text)

        # Check if AI parsing actually returned data
        if parsed.get("error"):
            logger.warning(f"AI resume parsing failed: {parsed['error']}")
            # Still save the raw text so user can retry later

        # Upsert resume data
        result = await self.db.execute(select(ResumeData).where(ResumeData.user_id == user_id))
        resume_data = result.scalar_one_or_none()

        if not resume_data:
            resume_data = ResumeData(user_id=user_id)
            self.db.add(resume_data)

        resume_data.raw_text = text
        resume_data.skills = parsed.get("skills", [])
        resume_data.projects = parsed.get("projects", [])
        resume_data.experience = parsed.get("experience", [])
        resume_data.technologies = parsed.get("technologies", [])
        resume_data.domains = parsed.get("domains", [])
        resume_data.insights = parsed.get("insights", {})

        # Update profile resume_url placeholder
        profile_result = await self.db.execute(select(Profile).where(Profile.user_id == user_id))
        profile = profile_result.scalar_one_or_none()
        if profile:
            profile.resume_url = f"uploaded:{file.filename}"

        await self.db.flush()

        return {
            "skills": resume_data.skills,
            "projects": resume_data.projects,
            "technologies": resume_data.technologies,
            "domains": resume_data.domains,
            "insights": resume_data.insights,
            "parsed_at": resume_data.parsed_at.isoformat() if resume_data.parsed_at else None,
        }

    async def get_insights(self, user_id: str) -> dict:
        result = await self.db.execute(select(ResumeData).where(ResumeData.user_id == user_id))
        resume_data = result.scalar_one_or_none()
        if not resume_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No resume data found. Upload your resume first.")

        return {
            "skills": resume_data.skills or [],
            "projects": resume_data.projects or [],
            "technologies": resume_data.technologies or [],
            "domains": resume_data.domains or [],
            "insights": resume_data.insights or {},
            "parsed_at": resume_data.parsed_at.isoformat() if resume_data.parsed_at else None,
        }

    async def get_resume_data(self, user_id: str) -> dict:
        return await self.get_insights(user_id)
