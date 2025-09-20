import logging.config
from pathlib import Path

def get_logging_config(logs_dir: Path, log_level: str = "INFO") -> dict:
    """Get the logging configuration dictionary with configurable parameters"""
    logs_dir.mkdir(exist_ok=True)
    
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s"
            },
            "access": { 
                "format": '%(asctime)s [%(levelname)s] %(client_addr)s - "%(request_line)s" %(status_code)s'
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "filename": str(logs_dir / "dexter.log"),
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 5,
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console", "file"],
        },
        "loggers": {
            "uvicorn": {"level": "INFO"},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {
                "handlers": ["console", "file"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }

def setup_logging(logs_dir: Path, log_level: str = "INFO"):
    """Setup logging configuration with configurable parameters"""
    logging.config.dictConfig(get_logging_config(logs_dir, log_level))
