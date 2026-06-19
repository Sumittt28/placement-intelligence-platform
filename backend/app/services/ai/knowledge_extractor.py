import json
from app.services.ai.gemini_client import GeminiClient
from app.services.ai.base import BaseParser


class KnowledgeExtractor(BaseParser):
    def __init__(self):
        self.client = GeminiClient()

    async def parse(self, raw_input: str) -> dict:
        """Implements BaseParser interface — delegates to extract with minimal context."""
        return await self.extract(
            questions=[{"question_text": raw_input}],
            role="Software Engineer",
            company_name="Unknown",
        )

    async def extract(self, questions: list, role: str, company_name: str) -> dict:
        prompt = f"""Analyze these interview questions from {company_name} for the role of {role}.

Extract structured metadata:

Questions:
{json.dumps(questions, default=str)}

Return JSON:
{{
    "topics": ["topic1", "topic2"],
    "skills": ["skill1", "skill2"],
    "technologies": ["tech1", "tech2"],
    "patterns": ["pattern observed in questions"],
    "tags": ["tag1", "tag2"],
    "difficulty_assessment": "easy|medium|hard",
    "key_areas": ["area1", "area2"]
}}
"""
        result = await self.client.generate(prompt, temperature=0.3)

        defaults = {"topics": [], "skills": [], "technologies": [], "patterns": [], "tags": []}
        for key, default in defaults.items():
            if key not in result:
                result[key] = default

        return result
