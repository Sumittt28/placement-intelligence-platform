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
    Implements BaseAIService. Falls back gracefully on failure."""

    async def generate(self, prompt: str, context: dict = None) -> Any:
        """BaseAIService interface — synthesize text to speech."""
        return await self.synthesize(prompt)

    async def transcribe(self, file: UploadFile) -> str:
        """Speech-to-Text using Whisper. Latency target: < 3 seconds."""
        try:
            import whisper

            # Save uploaded audio to temp file
            content = await file.read()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name

            # Transcribe
            model = whisper.load_model("base")
            result = model.transcribe(tmp_path)

            # Cleanup
            os.unlink(tmp_path)

            text = result.get("text", "").strip()
            if not text:
                raise ValueError("Whisper returned empty transcription")
            return text
        except ImportError:
            logger.warning("Whisper not installed. Falling back to empty transcription.")
            return ""
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return ""

    async def synthesize(self, text: str) -> str:
        """Text-to-Speech via Piper. Latency target: < 2 seconds.
        Returns base64 encoded audio. Returns empty string on failure for graceful degradation."""
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
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                return ""

            if os.path.exists(tmp_path):
                with open(tmp_path, "rb") as f:
                    audio_data = f.read()
                os.unlink(tmp_path)
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

    def is_available(self) -> dict:
        """Check availability of STT and TTS engines."""
        stt_available = False
        tts_available = False

        try:
            import whisper  # noqa: F401
            stt_available = True
        except ImportError:
            pass

        try:
            import subprocess
            result = subprocess.run(["piper", "--help"], capture_output=True, timeout=5)
            tts_available = result.returncode == 0
        except Exception:
            pass

        return {"stt": stt_available, "tts": tts_available}
