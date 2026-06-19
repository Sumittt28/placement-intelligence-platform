from app.services.ai.gemini_client import GeminiClient


class ResumeParser:
    def __init__(self):
        self.client = GeminiClient()

    async def parse(self, resume_text: str) -> dict:
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
