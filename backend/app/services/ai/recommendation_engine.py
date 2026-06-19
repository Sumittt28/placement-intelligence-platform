import json
from app.services.ai.gemini_client import GeminiClient


class RecommendationEngine:
    def __init__(self):
        self.client = GeminiClient()

    async def generate(self, skills: list = None, technologies: list = None) -> list:
        prompt = f"""Based on this student's profile, generate personalized learning recommendations.

Skills: {json.dumps(skills or [])}
Technologies: {json.dumps(technologies or [])}

Return a JSON array of recommendations:
[
    {{
        "type": "topic|practice_plan|mock_interview",
        "title": "Recommendation title",
        "description": "Why this is recommended",
        "priority": <1-100, higher = more important>
    }}
]

Generate 5 recommendations. Focus on:
1. Skills gaps (what's missing for placement readiness)
2. Topics to practice
3. Suggested mock interview types
"""
        result = await self.client.generate(prompt, temperature=0.5)

        if isinstance(result, list):
            return result
        if isinstance(result, dict) and "recommendations" in result:
            return result["recommendations"]
        return []
