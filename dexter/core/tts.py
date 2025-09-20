import logging
import time
import wave
import re
import os
from piper import PiperVoice, SynthesisConfig
from .voice_distortion import VoiceDistortor
from ..config.settings import settings
from typing import Optional, Union

logger = logging.getLogger(__name__)

class TTSManager:
    def __init__(self, default_speed=None, clean_text=None, sample_rate=None):
        self.default_speed = default_speed or settings.TTS_DEFAULT_SPEED
        self.should_clean_text = clean_text if clean_text is not None else settings.TTS_CLEAN_TEXT
        
        logger.info(f"Initializing TTS with model: {settings.TTS_MODEL_PATH}")
        self.piper_voice = PiperVoice.load(settings.TTS_MODEL_PATH)
        self.distortor = VoiceDistortor(sample_rate=settings.AUDIO_SAMPLE_RATE if sample_rate is None else sample_rate)
    
    def _clean_text_content(self, text: str) -> str:
        """Clean text by removing unwanted characters before TTS processing."""
        if not text:
            return text
        
        cleaned = re.sub(r'\*+', '', text)
        cleaned = re.sub(r'[_~`]+', '', cleaned)
        cleaned = re.sub(r'#{1,6}\s*', '', cleaned)
        cleaned = re.sub(r'\[.*?\]\(.*?\)', '', cleaned)
        cleaned = re.sub(r'https?://[^\s]+', '', cleaned)
        return cleaned
    
    def generate_audio_file(self, text: str, output_path: str, voice: Optional[str] = None, speed: Optional[float] = None, apply_distortion: bool = True) -> Union[str, None]:
        """Generate audio from text and save as a single file using Piper."""
        try:
            if self.should_clean_text:
                original_text = text
                text = self._clean_text_content(text)
                if text != original_text:
                    logger.info("Text cleaned for TTS processing")
            
            start_time = time.time()
            logger.info(f"Starting TTS generation for text length: {len(text)} characters")
            
            temp_path = output_path if not apply_distortion else output_path.replace('.wav', '_temp.wav')
            
            with wave.open(temp_path, "wb") as wav_file:
                syn_config = SynthesisConfig(
                    volume=2.0,
                    length_scale=self.default_speed,
                )
                self.piper_voice.synthesize_wav(text, wav_file, syn_config=syn_config)
            
            if apply_distortion:
                logger.info("Applying robot voice distortion...")
                distortion_start = time.time()
                self.distortor.process_file(temp_path, output_path)
                distortion_time = time.time() - distortion_start
                logger.info(f"Voice distortion applied in {distortion_time:.2f} seconds")
                
                os.remove(temp_path)
            
            end_time = time.time()
            duration = end_time - start_time
            logger.info(f"Total audio generation took {duration:.2f} seconds")
            logger.info(f"Saved audio to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return None



