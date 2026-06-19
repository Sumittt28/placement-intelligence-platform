from app.services.ai.gemini_client import GeminiClient
from app.services.ai.base import BaseParser


class ResumeParser(BaseParser):
    def __init__(self):
        self.client = GeminiClient()

    async def parse(self, raw_input: str) -> dict:
        """Implements BaseParser interface — parse resume text into structured data."""
        return await self.parse_resume(raw_input)

    async def parse_resume(self, resume_text: str) -> dict:
        prompt = """Analyze this resume and extract structured data. Return JSON with these exact keys:
{
    "skills": ["skill1", "skill2", ...],
    "projects": [{"name": "...", "description": "...", "technologies": ["..."]}],
    "experience": [{"title": "...", "company": "...", "duration": "...", "description": "..."}],
    "technologies": ["tech1", "tech2", ...],
    "domains": ["domain1", "domain2", ...],
    "insights": {
        "missing_skills": ["skills the candidate should learn based on market demand"],
        "strength_areas": ["areas where the candidate is strong"],
        "potential_interview_topics": ["topics likely to be asked in interviews based on this resume"]
    }
}

Resume:
""" + resume_text

        result = await self.client.generate(prompt, temperature=0.3)

        # Ensure all keys exist
        defaults = {
            "skills": [], "projects": [], "experience": [],
            "technologies": [], "domains": [], "insights": {},
        }
        for key, default in defaults.items():
            if key not in result:
                result[key] = default

        return result

    async def generate_insights(self, resume_data: dict, target_companies: list = None) -> dict:
        """Generate deeper insights by comparing resume against target company requirements."""
        import json
        prompt = f"""Analyze this candidate's profile and generate placement insights.

Resume Data:
{json.dumps(resume_data, default=str)}

Target Companies: {json.dumps(target_companies or [])}

Return JSON:
{{
    "missing_skills": ["skills needed but not present"],
    "strength_areas": ["strong areas"],
    "potential_interview_topics": ["topics likely to be asked"],
    "readiness_assessment": "brief overall readiness paragraph",
    "recommended_focus_areas": ["area1", "area2"]
}}
"""
        result = await self.client.generate(prompt, temperature=0.3)
        return result if isinstance(result, dict) else {"missing_skills": [], "strength_areas": []}
