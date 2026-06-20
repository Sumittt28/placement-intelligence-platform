import json
import google.generativeai as genai
from app.core.config import settings
from app.services.ai.base import BaseAIService


class GeminiClient(BaseAIService):
    def __init__(self, model: str = "gemini-2.0-flash"):
        if not settings.GEMINI_API_KEY:
            import logging
            logging.getLogger("pip.ai").warning("GEMINI_API_KEY is not set. AI features will return fallback responses.")
            self.model = None
            return
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            ),
        )

    async def generate(self, prompt: str, context: dict = None, temperature: float = 0.5) -> dict:
        if not self.model:
            return {"error": "AI service not configured. Set GEMINI_API_KEY in .env"}
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context:\n{json.dumps(context, default=str)}\n\n{prompt}"

            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            text = response.text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
            return {"error": "Failed to parse AI response", "raw": text}
        except Exception as e:
            return {"error": str(e)}

    async def generate_text(self, prompt: str, temperature: float = 0.5) -> str:
        """Generate plain text response (not JSON)."""
        if not self.model:
            return "AI service not configured. Set GEMINI_API_KEY in .env"
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.GenerationConfig(temperature=temperature),
            )
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
