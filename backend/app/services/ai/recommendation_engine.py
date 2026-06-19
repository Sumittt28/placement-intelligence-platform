import json
from app.services.ai.gemini_client import GeminiClient
from app.services.ai.base import BaseRecommender


class RecommendationEngine(BaseRecommender):
    def __init__(self):
        self.client = GeminiClient()

    async def recommend(self, **kwargs) -> list:
        """Implements BaseRecommender interface."""
        return await self.generate_recommendations(
            resume_data=kwargs.get("resume_data"),
            weaknesses=kwargs.get("weaknesses", []),
            evaluations=kwargs.get("evaluations", []),
            target_companies=kwargs.get("target_companies", []),
        )

    async def generate_recommendations(
        self,
        resume_data: dict = None,
        weaknesses: list = None,
        evaluations: list = None,
        target_companies: list = None,
    ) -> list:
        skills = []
        technologies = []
        if resume_data:
            skills = resume_data.get("skills", [])
            technologies = resume_data.get("technologies", [])

        prompt = f"""Based on this student's profile, generate personalized learning recommendations.

Skills: {json.dumps(skills)}
Technologies: {json.dumps(technologies)}
Weaknesses: {json.dumps(weaknesses or [])}
Target Companies: {json.dumps(target_companies or [])}
Recent Evaluation Scores: {json.dumps(evaluations or [])}

Return a JSON array of recommendations:
[
    {{
        "type": "topic|practice_plan|mock_interview",
        "title": "Recommendation title",
        "description": "Why this is recommended",
        "priority": <1-100, higher = more important>
    }}
]

Generate 5-8 recommendations. Priority ranking based on:
- Weakness severity (higher priority for recurring weaknesses)
- Target company requirements (align with what companies ask)
- Recency (focus on most recent gaps)

Focus on:
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
