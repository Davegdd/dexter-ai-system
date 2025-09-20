import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .deps import init_components
init_components()

# Import routes after initialization
from .routes import chat, transcribe, tts, system, sessions, agents

logger = logging.getLogger(__name__)

app = FastAPI(title="DeXteR API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(transcribe.router)
app.include_router(tts.router)
app.include_router(system.router)
app.include_router(sessions.router)
app.include_router(agents.router)

@app.get("/")
async def root():
    return {"status": "DeXteR is running"}
