import json
from app.services.ai.gemini_client import GeminiClient
from app.services.ai.base import BaseQuestionGenerator


class InterviewGenerator(BaseQuestionGenerator):
    def __init__(self):
        self.client = GeminiClient()

    async def generate_question(
        self, context: dict, interview_type: str = "technical", difficulty: str = "medium",
        previous_questions: list = None,
    ) -> dict:
        previous_questions = previous_questions or []
        prompt = f"""You are an expert interviewer conducting a {interview_type} interview at {difficulty} difficulty.

Generate the NEXT interview question. The question must be:
1. Resume-aware: If the candidate knows specific technologies, ask about those
2. Company-specific: If company data is available, align with what the company typically asks
3. NOT a repeat of previous questions
4. Adaptive: Based on the interview type and difficulty

Context about the candidate:
{json.dumps(context, default=str)}

Previous questions asked (do NOT repeat these):
{json.dumps(previous_questions, default=str)}

Rules:
- For TECHNICAL: Ask coding, system design, or technology-specific questions
- For BEHAVIORAL: Ask STAR-method behavioral questions
- For HM (Hiring Manager): Ask about leadership, decision-making, project management
- For PROJECT: Ask deep questions about the candidate's projects from their resume
- For COMPANY: Focus on topics the target company typically asks
- If resume mentions FastAPI, ask "Why FastAPI?", "How does async work in FastAPI?", etc.
- If resume mentions React, ask about hooks, state management, rendering, etc.

Return JSON:
{{"question": "Your interview question here", "topic": "topic category", "expected_depth": "brief|moderate|deep"}}
"""
        result = await self.client.generate(prompt, temperature=0.7)

        if "question" not in result:
            result = {
                "question": "Tell me about a challenging project you've worked on and what you learned from it.",
                "topic": "general",
                "expected_depth": "moderate",
            }

        return result
