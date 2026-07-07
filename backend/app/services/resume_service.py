import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.intelligence import ResumeData
from app.models.user import Profile
from app.utils.helpers import to_uuid

logger = logging.getLogger("pip.resume")

# Safety limit: truncate resume text sent to AI to avoid token-limit errors.
# ~8000 chars ≈ ~2000 tokens — well within Groq's context window.
MAX_RESUME_CHARS = 8000


class ResumeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_and_parse(self, user_id: str, content: bytes, filename: str) -> dict:
        """
        Parse a resume from raw bytes and store structured data.

        Args:
            user_id:  JWT subject (UUID string).
            content:  Raw file bytes (already read & validated by the route).
            filename: Original filename — used to detect PDF vs plain text.
        """
        uid = to_uuid(user_id)

        # ── Step 1: Extract plain text from file ──────────────────────────────
        text = self._extract_text(content, filename)

        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Could not extract text from the uploaded file. "
                    "If this is a scanned PDF, please upload a text-based PDF or a .txt file."
                ),
            )

        # ── Step 2: AI parsing ────────────────────────────────────────────────
        from app.services.ai.resume_parser import ResumeParser
        parser = ResumeParser()
        parsed = await parser.parse(text)

        if parsed.get("error"):
            logger.warning(f"AI resume parsing returned error: {parsed['error']}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"AI parsing failed: {parsed['error']}. Please try again.",
            )

        # Guard: if AI returned no skills AND no technologies, the resume text was
        # likely unreadable garbage (e.g. binary PDF headers slipping through).
        has_content = bool(parsed.get("skills")) or bool(parsed.get("technologies"))
        if not has_content:
            logger.warning(f"AI returned empty skills/technologies for user {user_id} — resume text may be unreadable")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Could not extract any skills from the resume. "
                    "Please ensure the file is a text-based PDF (not scanned) or a .txt file."
                ),
            )

        # ── Step 3: Upsert resume data in DB ──────────────────────────────────
        result = await self.db.execute(
            select(ResumeData).where(ResumeData.user_id == uid)
        )
        resume_data = result.scalar_one_or_none()

        if not resume_data:
            resume_data = ResumeData(user_id=uid)
            self.db.add(resume_data)

        resume_data.raw_text      = text
        resume_data.skills        = parsed.get("skills", [])
        resume_data.projects      = parsed.get("projects", [])
        resume_data.experience    = parsed.get("experience", [])
        resume_data.technologies  = parsed.get("technologies", [])
        resume_data.domains       = parsed.get("domains", [])
        resume_data.insights      = parsed.get("insights", {})
        # Bug fix #5: explicitly update parsed_at on every upload, not just creation
        resume_data.parsed_at     = datetime.now(timezone.utc)

        # ── Step 4: Update profile resume_url ────────────────────────────────
        profile_result = await self.db.execute(
            select(Profile).where(Profile.user_id == uid)
        )
        profile = profile_result.scalar_one_or_none()
        if profile:
            profile.resume_url = f"uploaded:{filename}"

        await self.db.flush()

        logger.info(
            f"Resume parsed for user {user_id} — "
            f"skills={len(resume_data.skills)}, "
            f"projects={len(resume_data.projects)}, "
            f"technologies={len(resume_data.technologies)}"
        )

        return {
            "skills":       resume_data.skills,
            "projects":     resume_data.projects,
            "experience":   resume_data.experience,
            "technologies": resume_data.technologies,
            "domains":      resume_data.domains,
            "insights":     resume_data.insights,
            "parsed_at":    resume_data.parsed_at.isoformat(),
        }

    def _extract_text(self, content: bytes, filename: str) -> str:
        """
        Extract plain text from file bytes.
        Supports PDF (text-based), .txt, and .docx.
        Falls back to UTF-8 decode on any extraction failure.
        """
        fname = filename.lower()

        if fname.endswith(".pdf"):
            try:
                import io
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(content))
                pages_text = [page.extract_text() or "" for page in reader.pages]
                text = "\n".join(pages_text).strip()
                if not text:
                    logger.warning(f"pypdf returned empty text for '{filename}' — likely a scanned/image PDF")
                return text
            except Exception as e:
                logger.error(f"PDF extraction failed for '{filename}': {e}")
                # Do NOT fall back to raw bytes — binary PDF headers are not resume text
                return ""

        if fname.endswith(".docx"):
            try:
                import io
                import zipfile
                import xml.etree.ElementTree as ET
                with zipfile.ZipFile(io.BytesIO(content)) as z:
                    with z.open("word/document.xml") as doc_xml:
                        tree = ET.parse(doc_xml)
                        root = tree.getroot()
                        ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
                        texts = [node.text for node in root.iter(f"{ns}t") if node.text]
                        return " ".join(texts)
            except Exception as e:
                logger.error(f"DOCX extraction failed for '{filename}': {e}")
                return content.decode("utf-8", errors="ignore")

        # .txt or any other file — plain decode
        return content.decode("utf-8", errors="ignore")

    async def get_insights(self, user_id: str) -> dict:
        result = await self.db.execute(
            select(ResumeData).where(ResumeData.user_id == to_uuid(user_id))
        )
        resume_data = result.scalar_one_or_none()
        if not resume_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No resume data found. Upload your resume first.",
            )
        return {
            "skills":       resume_data.skills or [],
            "projects":     resume_data.projects or [],
            "experience":   resume_data.experience or [],
            "technologies": resume_data.technologies or [],
            "domains":      resume_data.domains or [],
            "insights":     resume_data.insights or {},
            "parsed_at":    resume_data.parsed_at.isoformat() if resume_data.parsed_at else None,
        }

    async def get_resume_data(self, user_id: str) -> dict:
        return await self.get_insights(user_id)
