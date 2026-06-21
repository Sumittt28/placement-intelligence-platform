import json
import asyncio
import logging
import google.generativeai as genai
from app.core.config import settings
from app.services.ai.base import BaseAIService

logger = logging.getLogger("pip.ai.gemini")

# Default timeout for AI generation calls (seconds)
GEMINI_TIMEOUT = 15


class GeminiClient(BaseAIService):
    """Singleton-pattern Gemini client. Reuses the same model instance across requests."""

    _instance = None
    _model = None
    _text_model = None
    _configured = False

    def __new__(cls, model: str = "gemini-2.0-flash"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model: str = "gemini-2.0-flash"):
        if GeminiClient._configured:
            return
        GeminiClient._configured = True

        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set. AI features will return fallback responses.")
            GeminiClient._model = None
            GeminiClient._text_model = None
            return

        genai.configure(api_key=settings.GEMINI_API_KEY)
        GeminiClient._model = genai.GenerativeModel(
            model,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            ),
        )
        GeminiClient._text_model = genai.GenerativeModel(model)

    @property
    def model(self):
        return GeminiClient._model

    async def generate(self, prompt: str, context: dict = None, temperature: float = 0.5) -> dict:
        if not self.model:
            return {"error": "AI service not configured. Set GEMINI_API_KEY in .env"}
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context:\n{json.dumps(context, default=str)}\n\n{prompt}"

            response = await asyncio.wait_for(
                self.model.generate_content_async(
                    full_prompt,
                    generation_config=genai.GenerationConfig(
                        temperature=temperature,
                        response_mime_type="application/json",
                    ),
                ),
                timeout=GEMINI_TIMEOUT,
            )
            return json.loads(response.text)
        except asyncio.TimeoutError:
            logger.error(f"Gemini API timed out after {GEMINI_TIMEOUT}s")
            return {"error": f"AI request timed out after {GEMINI_TIMEOUT} seconds"}
        except json.JSONDecodeError:
            # Try to extract JSON from response
            text = response.text
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass
            return {"error": "Failed to parse AI response", "raw": text[:500]}
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {"error": str(e)}

    async def generate_text(self, prompt: str, temperature: float = 0.5) -> str:
        """Generate plain text response (not JSON)."""
        if not GeminiClient._text_model:
            return "AI service not configured. Set GEMINI_API_KEY in .env"
        try:
            response = await asyncio.wait_for(
                GeminiClient._text_model.generate_content_async(
                    prompt,
                    generation_config=genai.GenerationConfig(temperature=temperature),
                ),
                timeout=GEMINI_TIMEOUT,
            )
            return response.text
        except asyncio.TimeoutError:
            logger.error(f"Gemini text API timed out after {GEMINI_TIMEOUT}s")
            return f"AI request timed out after {GEMINI_TIMEOUT} seconds"
        except Exception as e:
            logger.error(f"Gemini text API error: {e}")
            return f"Error: {str(e)}"
