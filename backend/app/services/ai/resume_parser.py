import json
import logging
from app.services.ai.gemini_client import GeminiClient
from app.services.ai.base import BaseParser

logger = logging.getLogger("pip.ai.resume_parser")

# Truncate resume text to this length before sending to AI.
# ~8000 chars ≈ ~2000 tokens — safe for all Groq models.
MAX_RESUME_CHARS = 8000


class ResumeParser(BaseParser):
    def __init__(self):
        self.client = GeminiClient()

    async def parse(self, raw_input: str) -> dict:
        """Implements BaseParser interface."""
        return await self.parse_resume(raw_input)

    async def parse_resume(self, resume_text: str) -> dict:
        # Truncate to avoid token-limit errors on Groq
        if len(resume_text) > MAX_RESUME_CHARS:
            logger.info(
                f"Resume text truncated from {len(resume_text)} to {MAX_RESUME_CHARS} chars"
            )
            resume_text = resume_text[:MAX_RESUME_CHARS]

        prompt = f"""You are an expert resume parser for a placement preparation platform.

Analyze the resume text below and extract structured information.
Return ONLY a valid JSON object with exactly these keys — no markdown, no explanation:

{{
    "skills": ["skill1", "skill2"],
    "projects": [
        {{"name": "project name", "description": "what it does", "technologies": ["tech1", "tech2"]}}
    ],
    "experience": [
        {{"title": "job title", "company": "company name", "duration": "e.g. Jan 2023 - Jun 2023", "description": "what you did"}}
    ],
    "technologies": ["tech1", "tech2"],
    "domains": ["e.g. Web Development", "Machine Learning"],
    "insights": {{
        "missing_skills": ["skills the candidate should learn based on market demand"],
        "strength_areas": ["areas where the candidate is strong"],
        "potential_interview_topics": ["topics likely to be asked based on this resume"]
    }}
}}

RESUME:
---
{resume_text}
---
"""
        result = await self.client.generate(prompt, temperature=0.2)

        # Ensure all required keys are present
        defaults = {
            "skills": [],
            "projects": [],
            "experience": [],
            "technologies": [],
            "domains": [],
            "insights": {
                "missing_skills": [],
                "strength_areas": [],
                "potential_interview_topics": [],
            },
        }
        for key, default in defaults.items():
            if key not in result:
                result[key] = default

        # Ensure insights sub-keys exist
        if isinstance(result.get("insights"), dict):
            for sub_key in ("missing_skills", "strength_areas", "potential_interview_topics"):
                result["insights"].setdefault(sub_key, [])
        else:
            result["insights"] = defaults["insights"]

        return result

    async def generate_insights(
        self, resume_data: dict, target_companies: list = None
    ) -> dict:
        """Generate deeper insights by comparing resume against target company requirements."""
        prompt = f"""You are a placement advisor. Analyze this candidate's profile and generate actionable placement insights.

Resume Data:
{json.dumps(resume_data, default=str, indent=2)}

Target Companies: {json.dumps(target_companies or [])}

Return ONLY a valid JSON object with exactly these keys — no markdown, no explanation:
{{
    "missing_skills": ["skills needed but not present in the resume"],
    "strength_areas": ["areas where the candidate clearly excels"],
    "potential_interview_topics": ["topics likely to be asked in interviews"],
    "readiness_assessment": "one paragraph summarising overall placement readiness",
    "recommended_focus_areas": ["top 3-5 areas to focus on for placement"]
}}
"""
        result = await self.client.generate(prompt, temperature=0.3)
        if not isinstance(result, dict) or result.get("error"):
            return {
                "missing_skills": [],
                "strength_areas": [],
                "potential_interview_topics": [],
                "readiness_assessment": "Could not generate insights. Please try again.",
                "recommended_focus_areas": [],
            }
        return result
