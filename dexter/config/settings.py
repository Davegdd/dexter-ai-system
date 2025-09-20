import os
import logging.config
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Centralized configuration management for DeXteR"""
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    YOUTUBE_API_KEY: str = os.getenv("YOUTUBE_API_KEY", "")
    CEREBRAS_API_KEY: str = os.getenv("CEREBRAS_API_KEY", "")
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    
    # Directories
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    MEMORY_DIRECTORY: Path = Path(os.getenv("MEMORY_DIRECTORY", BASE_DIR / "dexter" / "memory"))
    SESSIONS_DIRECTORY: Path = Path(os.getenv("SESSIONS_DIRECTORY", BASE_DIR / "dexter" / "memory" / "sessions"))
    DATA_DIR: Path = BASE_DIR / "data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    MODELS_DIR: Path = BASE_DIR / "dexter" / "models"
    
    # LLM Settings
    DEFAULT_MODEL: str = "gemini/gemini-2.0-flash"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 4000
    TOP_P: float = 0.9
    MAX_RETRY_ATTEMPTS: int = 4
    RETRY_MIN_WAIT: int = 1
    RETRY_MAX_WAIT: int = 10
    
    # Audio/TTS Settings
    TTS_MODEL_PATH: Path = MODELS_DIR / "tts" / "en_US-hfc_male-medium.onnx"
    AUDIO_SAMPLE_RATE: int = 24000
    TTS_DEFAULT_SPEED: float = 0.8
    TTS_CLEAN_TEXT: bool = True
    TTS_APPLY_DISTORTION: bool = True
    
    # STT Settings
    STT_MODEL_ID: str = "mlx-community/parakeet-tdt-0.6b-v3"
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def setup_logging(cls) -> None:
        """Setup logging configuration"""
        from .logging_config import get_logging_config
        logging.config.dictConfig(get_logging_config(cls.LOGS_DIR, cls.LOG_LEVEL))
    
    @classmethod
    def ensure_directories_exist(cls) -> None:
        """Ensure all required directories exist"""
        directories = [
            cls.MEMORY_DIRECTORY,
            cls.SESSIONS_DIRECTORY,
            cls.DATA_DIR,
            cls.LOGS_DIR,
            cls.MODELS_DIR
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

settings = Settings()

settings.ensure_directories_exist()