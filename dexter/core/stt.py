from parakeet_mlx import from_pretrained
import tempfile
import soundfile as sf
import os
import logging
import time
import numpy as np
from ..config.settings import settings

logger = logging.getLogger(__name__)

model = None

def init_stt() -> None:
    global model
    logger.info(f"Initializing STT with parakeet-mlx model: {settings.STT_MODEL_ID}")
    
    try:
        model = from_pretrained(settings.STT_MODEL_ID)
        logger.info("STT model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to initialize STT: {e}")
        raise

def transcribe_audio_file(audio_array: np.ndarray) -> str:
    """
    Simple transcription function for audio files.
    Takes an audio array and returns the transcribed text.
    """
    temp_file_path = None
    try:
        start_time = time.time()
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            sf.write(temp_file.name, audio_array, settings.AUDIO_SAMPLE_RATE)
            temp_file_path = temp_file.name
        
        result = model.transcribe(temp_file_path)
        logger.info(f"Audio transcription took {time.time() - start_time:.2f} seconds")
        return result.text
    except Exception as e:
        logger.error(f"Error in audio transcription: {e}")
        raise e
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)