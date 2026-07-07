"""
Unified AI Client — Groq (primary), Gemini (legacy fallback), Ollama (local dev)
==================================================================================
Class name kept as `GeminiClient` intentionally so zero imports break across
evaluator.py, interview_generator.py, resume_parser.py, etc.

Model strategy (Groq free tier):
  SMART → llama-3.3-70b-versatile  : heavy tasks — evaluation, resume parsing,
                                      knowledge extraction, recommendations
                                      (1,000 req/day free, 6,000 tokens/min)
  FAST  → llama-3.1-8b-instant     : light high-volume tasks — question generation,
                                      follow-up generation during live interviews
                                      (14,400 req/day free, 20,000 tokens/min)

Switching providers: change AI_PROVIDER in .env — no other code changes needed.
"""

import json
import asyncio
import logging
from app.core.config import settings
from app.services.ai.base import BaseAIService

logger = logging.getLogger("pip.ai.client")

AI_TIMEOUT = 30  # seconds


class GeminiClient(BaseAIService):
    """
    Unified AI client supporting Groq, Gemini, and Ollama.
    Singleton pattern — one client instance shared across all requests.
    """

    _instance = None
    _configured = False

    # ── Singleton ──────────────────────────────────────────────────────────────
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        if GeminiClient._configured:
            return
        GeminiClient._configured = True

        self.provider = settings.AI_PROVIDER
        logger.info(f"Initializing AI client — provider: {self.provider}")

        if self.provider == "groq":
            self._init_groq()
        elif self.provider == "ollama":
            self._init_ollama()
        elif self.provider == "gemini":
            self._init_gemini()
        else:
            logger.error(
                f"Unknown AI_PROVIDER '{self.provider}'. "
                "Valid options: groq | gemini | ollama"
            )

    # ── Provider initialisers ──────────────────────────────────────────────────

    def _init_groq(self):
        if not settings.GROQ_API_KEY:
            logger.warning(
                "GROQ_API_KEY is not set. "
                "Get a free key at https://console.groq.com/keys and add it to .env"
            )
            self._groq = None
            return
        try:
            from groq import AsyncGroq
            self._groq = AsyncGroq(api_key=settings.GROQ_API_KEY)
            self._smart_model = settings.GROQ_MODEL_SMART  # 70B — heavy tasks
            self._fast_model = settings.GROQ_MODEL_FAST    # 8B  — high-volume tasks
            logger.info(
                f"Groq initialised | smart={self._smart_model} | fast={self._fast_model}"
            )
        except ImportError:
            logger.error("groq package not installed. Run: pip install groq")
            self._groq = None

    def _init_ollama(self):
        self._ollama_url = settings.OLLAMA_BASE_URL
        self._ollama_model = settings.OLLAMA_MODEL
        logger.info(
            f"Ollama initialised | url={self._ollama_url} | model={self._ollama_model}"
        )

    def _init_gemini(self):
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY is not set. AI features will be unavailable.")
            self._gemini_json_model = None
            self._gemini_text_model = None
            return
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._gemini_json_model = genai.GenerativeModel(
                "gemini-2.0-flash",
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json"
                ),
            )
            self._gemini_text_model = genai.GenerativeModel("gemini-2.0-flash")
            logger.info("Gemini initialised (legacy mode)")
        except ImportError:
            logger.error(
                "google-generativeai not installed. "
                "Switch AI_PROVIDER=groq or run: pip install google-generativeai"
            )
            self._gemini_json_model = None
            self._gemini_text_model = None

    # ── Internal generation helpers ────────────────────────────────────────────

    async def _groq_generate_json(
        self, prompt: str, temperature: float, use_fast_model: bool
    ) -> str:
        model = self._fast_model if use_fast_model else self._smart_model
        response = await asyncio.wait_for(
            self._groq.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                response_format={"type": "json_object"},
            ),
            timeout=AI_TIMEOUT,
        )
        return response.choices[0].message.content

    async def _groq_generate_text(
        self, prompt: str, temperature: float, use_fast_model: bool
    ) -> str:
        model = self._fast_model if use_fast_model else self._smart_model
        response = await asyncio.wait_for(
            self._groq.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            ),
            timeout=AI_TIMEOUT,
        )
        return response.choices[0].message.content

    async def _ollama_generate(
        self, prompt: str, temperature: float, json_mode: bool
    ) -> str:
        import httpx
        payload = {
            "model": self._ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }
        if json_mode:
            payload["format"] = "json"
        async with httpx.AsyncClient(timeout=AI_TIMEOUT) as client:
            resp = await client.post(
                f"{self._ollama_url}/api/generate", json=payload
            )
            resp.raise_for_status()
            return resp.json()["response"]

    async def _gemini_generate_json(self, prompt: str, temperature: float) -> str:
        import google.generativeai as genai
        response = await asyncio.wait_for(
            self._gemini_json_model.generate_content_async(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                    response_mime_type="application/json",
                ),
            ),
            timeout=AI_TIMEOUT,
        )
        return response.text

    async def _gemini_generate_text(self, prompt: str, temperature: float) -> str:
        import google.generativeai as genai
        response = await asyncio.wait_for(
            self._gemini_text_model.generate_content_async(
                prompt,
                generation_config=genai.GenerationConfig(temperature=temperature),
            ),
            timeout=AI_TIMEOUT,
        )
        return response.text

    # ── Public interface (unchanged — all service files work as-is) ────────────

    async def generate(
        self,
        prompt: str,
        context: dict = None,
        temperature: float = 0.5,
        use_fast_model: bool = False,
    ) -> dict:
        """
        Generate a structured JSON response.

        Args:
            prompt:         The instruction/question for the AI.
            context:        Optional dict merged into the prompt as context.
            temperature:    0.0 = deterministic, 1.0 = creative.
            use_fast_model: True  → llama-3.1-8b-instant (14,400 req/day free)
                                    Use for question generation & follow-ups.
                            False → llama-3.3-70b-versatile (1,000 req/day free)
                                    Use for evaluation, resume parsing, recommendations.
        Returns:
            Parsed dict. On any error returns {"error": "..."}.
        """
        if context:
            prompt = f"Context:\n{json.dumps(context, default=str)}\n\n{prompt}"

        raw = None
        try:
            if self.provider == "groq":
                if not self._groq:
                    return {"error": "Groq not initialised. Check GROQ_API_KEY in .env"}
                raw = await self._groq_generate_json(prompt, temperature, use_fast_model)

            elif self.provider == "ollama":
                raw = await self._ollama_generate(prompt, temperature, json_mode=True)

            elif self.provider == "gemini":
                if not self._gemini_json_model:
                    return {"error": "Gemini not initialised. Check GEMINI_API_KEY in .env"}
                raw = await self._gemini_generate_json(prompt, temperature)

            else:
                return {"error": f"Unknown AI_PROVIDER: {self.provider}"}

            return json.loads(raw)

        except asyncio.TimeoutError:
            logger.error(f"AI request timed out after {AI_TIMEOUT}s [{self.provider}]")
            return {"error": f"AI request timed out after {AI_TIMEOUT} seconds"}

        except json.JSONDecodeError:
            # Last-resort: salvage JSON from partial output
            if raw:
                start, end = raw.find("{"), raw.rfind("}") + 1
                if start >= 0 and end > start:
                    try:
                        return json.loads(raw[start:end])
                    except json.JSONDecodeError:
                        pass
            logger.error(f"JSON parse failed. Raw (first 300 chars): {str(raw)[:300]}")
            return {"error": "Failed to parse AI response as JSON"}

        except Exception as e:
            logger.error(f"AI generation error [{self.provider}]: {e}", exc_info=True)
            return {"error": str(e)}

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.5,
        use_fast_model: bool = False,
    ) -> str:
        """
        Generate a plain-text response (used for ideal answer generation).

        Args:
            prompt:         The instruction for the AI.
            temperature:    Creativity level.
            use_fast_model: True → use fast/light model (8B).
        Returns:
            Plain text string. On error returns an error-message string.
        """
        try:
            if self.provider == "groq":
                if not self._groq:
                    return "Groq not initialised. Check GROQ_API_KEY in .env"
                return await self._groq_generate_text(prompt, temperature, use_fast_model)

            elif self.provider == "ollama":
                return await self._ollama_generate(prompt, temperature, json_mode=False)

            elif self.provider == "gemini":
                if not self._gemini_text_model:
                    return "Gemini not initialised. Check GEMINI_API_KEY in .env"
                return await self._gemini_generate_text(prompt, temperature)

            return "No AI provider configured."

        except asyncio.TimeoutError:
            logger.error(f"AI text request timed out after {AI_TIMEOUT}s [{self.provider}]")
            return f"AI request timed out after {AI_TIMEOUT} seconds"

        except Exception as e:
            logger.error(f"AI text generation error [{self.provider}]: {e}", exc_info=True)
            return f"Error: {str(e)}"
