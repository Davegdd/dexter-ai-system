import io, os, tempfile, urllib.parse
import librosa
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from fastapi.responses import Response
from typing import Union
from ..deps import llm, tts_manager
from dexter.core.stt import transcribe_audio_file
from pydantic import BaseModel

router = APIRouter(prefix="/transcribe", tags=["transcribe"])

class TranscriptionResponse(BaseModel):
    transcription: str
    response: str
    status: str = "success"

@router.post("/", response_model=None)
async def transcribe_audio(audio_file: UploadFile = File(...), response_type: str = Form("text")) -> Union[TranscriptionResponse, Response]:
    try:
        audio_bytes = await audio_file.read()
        audio_array, sample_rate = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        transcription_text = transcribe_audio_file(audio_array)

        formatted_message = [{"type": "text", "text": transcription_text}]
        llm.llm_input(formatted_message)
        llm_response = getattr(llm, "complete_response", "No response generated")

        if response_type == "audio":
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            try:
                audio_file_path = tts_manager.generate_audio_file(llm_response, temp_path)
                if audio_file_path and os.path.exists(audio_file_path):
                    with open(audio_file_path, "rb") as audio_file:
                        audio_data = audio_file.read()
                    os.unlink(audio_file_path)
                    encoded_transcription = urllib.parse.quote(transcription_text, safe='')
                    return Response(content=audio_data, media_type="audio/wav", headers={"X-Transcription": encoded_transcription})
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        return TranscriptionResponse(transcription=transcription_text, response=llm_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
