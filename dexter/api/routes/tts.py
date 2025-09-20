import os, tempfile
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from ..deps import tts_manager

router = APIRouter(prefix="/tts", tags=["tts"])

class TTSRequest(BaseModel):
    text: str

@router.post("/")
async def text_to_speech(request: TTSRequest) -> Response:
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        try:
            audio_file_path = tts_manager.generate_audio_file(request.text, temp_path)
            if audio_file_path and os.path.exists(audio_file_path):
                with open(audio_file_path, "rb") as audio_file:
                    audio_data = audio_file.read()
                os.unlink(audio_file_path)
                return Response(content=audio_data, media_type="audio/wav")
            raise HTTPException(status_code=500, detail="Audio generation failed")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
