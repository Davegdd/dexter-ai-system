import uvicorn
from dexter.api.app import app
from dexter.config.settings import settings
from dexter.config.logging_config import get_logging_config

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_config=get_logging_config(settings.LOGS_DIR, settings.LOG_LEVEL),
    )
