import base64
import tempfile
import os
import logging
from fastapi import UploadFile
from app.services.ai.base import BaseAIService
from typing import Any

logger = logging.getLogger(__name__)


class VoiceEngine(BaseAIService):
    """Voice engine using Whisper (STT) and Piper (TTS).
    Implements BaseAIService. Falls back gracefully on failure.
    Uses lazy singleton for Whisper model to avoid reloading on every request."""

    _whisper_model = None
    _whisper_load_attempted = False

    async def generate(self, prompt: str, context: dict = None) -> Any:
        """BaseAIService interface — synthesize text to speech."""
        audio = await self.synthesize(prompt)
        return {"audio_base64": audio}

    @classmethod
    def _get_whisper_model(cls):
        """Lazy-load Whisper model once and cache it."""
        if cls._whisper_load_attempted:
            return cls._whisper_model
        cls._whisper_load_attempted = True
        try:
            import whisper
            cls._whisper_model = whisper.load_model("base")
            logger.info("Whisper model loaded successfully")
        except ImportError:
            logger.warning("Whisper not installed. STT unavailable.")
            cls._whisper_model = None
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            cls._whisper_model = None
        return cls._whisper_model

    async def transcribe(self, file: UploadFile) -> str:
        """Speech-to-Text using Whisper. Latency target: < 3 seconds."""
        model = self._get_whisper_model()
        if model is None:
            return ""

        tmp_path = None
        try:
            content = await file.read()
            if not content:
                return ""

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            result = model.transcribe(tmp_path)
            text = result.get("text", "").strip()
            if not text:
                logger.warning("Whisper returned empty transcription")
            return text
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.unlink(tmp_path)

    async def synthesize(self, text: str) -> str:
        """Text-to-Speech via Piper. Latency target: < 2 seconds.
        Returns base64 encoded audio. Returns empty string on failure for graceful degradation."""
        tmp_path = None
        try:
            import subprocess
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = tmp.name

            process = subprocess.run(
                ["piper", "--model", "en_US-lessac-medium", "--output_file", tmp_path],
                input=text,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if process.returncode != 0:
                logger.warning(f"Piper TTS failed: {process.stderr}")
                return ""

            if os.path.exists(tmp_path):
                with open(tmp_path, "rb") as f:
                    audio_data = f.read()
                if len(audio_data) > 0:
                    return base64.b64encode(audio_data).decode("utf-8")

            return ""
        except FileNotFoundError:
            logger.warning("Piper TTS not installed. Voice synthesis unavailable.")
            return ""
        except subprocess.TimeoutExpired:
            logger.warning("Piper TTS timed out.")
            return ""
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return ""
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass

    def is_available(self) -> dict:
        """Check availability of STT and TTS engines."""
        stt_available = self._get_whisper_model() is not None
        tts_available = False

        try:
            import subprocess
            result = subprocess.run(["piper", "--help"], capture_output=True, timeout=5)
            tts_available = result.returncode == 0
        except Exception:
            pass

        return {"stt": stt_available, "tts": tts_available}
