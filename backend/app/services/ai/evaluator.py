import json
from app.services.ai.gemini_client import GeminiClient


class Evaluator:
    def __init__(self):
        self.client = GeminiClient()

    async def evaluate(self, transcript: list, interview_type: str) -> dict:
        prompt = f"""You are an expert interview evaluator. Evaluate this {interview_type} interview.

CRITICAL RULES:
- Do NOT generate arbitrary scores
- EVERY score (1-10) must have a specific reason citing the student's actual answers
- Be honest and constructive
- Example: Communication: 7/10 - "Clear explanations but frequent pauses and some filler words"

Interview transcript:
{json.dumps(transcript, default=str)}

Evaluate across 6 dimensions and return this exact JSON structure:
{{
    "communication": {{
        "score": <1-10>,
        "reason": "Specific reason citing student answers"
    }},
    "technical": {{
        "score": <1-10>,
        "reason": "Specific reason citing student answers"
    }},
    "confidence": {{
        "score": <1-10>,
        "reason": "Specific reason citing student answers"
    }},
    "problem_solving": {{
        "score": <1-10>,
        "reason": "Specific reason citing student answers"
    }},
    "behavioral": {{
        "score": <1-10>,
        "reason": "Specific reason citing student answers"
    }},
    "project": {{
        "score": <1-10>,
        "reason": "Specific reason citing student answers"
    }},
    "overall_score": <weighted average 1-10>,
    "overall_feedback": "Comprehensive paragraph summarizing performance",
    "strengths": ["strength1", "strength2", "strength3"],
    "improvements": ["improvement1", "improvement2", "improvement3"]
}}

Every reason MUST reference specific answers from the transcript. No generic feedback.
"""
        result = await self.client.generate(prompt, temperature=0.3)

        # Validate structure
        required_dims = ["communication", "technical", "confidence", "problem_solving", "behavioral", "project"]
        for dim in required_dims:
            if dim not in result or "score" not in result.get(dim, {}):
                result[dim] = {"score": 5.0, "reason": f"Could not evaluate {dim} from the transcript"}

        if "overall_score" not in result:
            scores = [result[d]["score"] for d in required_dims]
            result["overall_score"] = round(sum(scores) / len(scores), 1)

        if "overall_feedback" not in result:
            result["overall_feedback"] = "Evaluation completed. Review individual dimension scores for details."

        result.setdefault("strengths", [])
        result.setdefault("improvements", [])

        return result

    async def generate_ideal_answer(self, question: str, interview_type: str) -> str:
        prompt = f"""Generate an ideal interview answer for this question in a {interview_type} interview.

Question: {question}

Provide a clear, structured, and comprehensive answer that a top candidate would give.
Keep it concise but thorough (2-3 paragraphs max).
"""
        return await self.client.generate_text(prompt, temperature=0.3)
