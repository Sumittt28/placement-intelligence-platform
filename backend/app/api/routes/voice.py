from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import get_current_user
from app.schemas.common import APIResponse
from pydantic import BaseModel

router = APIRouter()


class SynthesizeRequest(BaseModel):
    text: str


@router.post("/transcribe", response_model=APIResponse)
async def transcribe(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    # Voice engine integration — Phase 9
    from app.services.ai.voice_engine import VoiceEngine
    engine = VoiceEngine()
    text = await engine.transcribe(file)
    return APIResponse(data={"text": text})


@router.post("/synthesize", response_model=APIResponse)
async def synthesize(
    request: SynthesizeRequest,
    current_user: dict = Depends(get_current_user),
):
    from app.services.ai.voice_engine import VoiceEngine
    engine = VoiceEngine()
    audio = await engine.synthesize(request.text)
    return APIResponse(data={"audio_base64": audio})
