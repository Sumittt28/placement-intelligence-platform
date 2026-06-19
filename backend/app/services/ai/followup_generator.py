import json
from app.services.ai.gemini_client import GeminiClient


class FollowUpGenerator:
    def __init__(self):
        self.client = GeminiClient()

    async def generate_followup(
        self, context: dict, transcript: list, interview_type: str, difficulty: str
    ) -> dict:
        prompt = f"""You are an expert interviewer conducting a {interview_type} interview at {difficulty} difficulty.

Based on the conversation so far, generate the NEXT question. This must be DYNAMIC and ADAPTIVE.

Rules:
- If the last answer was shallow or vague -> Dig deeper: "Can you elaborate on...?"
- If the last answer was incorrect -> Redirect: "That's not quite right. Let me ask it differently..."
- If the last answer was good -> Advance to a harder related topic
- NEVER use fixed question flows
- Follow-up questions must depend on the actual previous answers
- After 3-4 follow-ups on a topic, switch to a new topic
- Keep the interview natural and conversational

Candidate context:
{json.dumps(context, default=str)}

Full conversation transcript:
{json.dumps(transcript, default=str)}

Analyze the last answer quality and decide:
1. Should this be a follow-up to dig deeper? Or a new topic?
2. What specific aspect should be explored?

Return JSON:
{{"question": "Your next question", "type": "follow_up or main", "topic": "topic category", "reasoning": "Why this question was chosen"}}
"""
        result = await self.client.generate(prompt, temperature=0.7)

        if "question" not in result:
            result = {
                "question": "Can you walk me through your problem-solving approach for a recent challenge?",
                "type": "main",
                "topic": "problem_solving",
                "reasoning": "Fallback question",
            }

        return result
