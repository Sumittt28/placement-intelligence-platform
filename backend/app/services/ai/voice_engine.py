import base64
import tempfile
import os
from fastapi import UploadFile


class VoiceEngine:
    """Voice engine using Whisper (STT) and Piper (TTS)."""

    async def transcribe(self, file: UploadFile) -> str:
        """Speech-to-Text using Whisper."""
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

            return result.get("text", "")
        except ImportError:
            return "[Whisper not installed. Install with: pip install openai-whisper]"
        except Exception as e:
            return f"[Transcription error: {str(e)}]"

    async def synthesize(self, text: str) -> str:
        """Text-to-Speech — returns base64 encoded audio."""
        try:
            # Piper TTS integration
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

            if os.path.exists(tmp_path):
                with open(tmp_path, "rb") as f:
                    audio_data = f.read()
                os.unlink(tmp_path)
                return base64.b64encode(audio_data).decode("utf-8")

            return ""
        except Exception as e:
            return f"[TTS error: {str(e)}]"
