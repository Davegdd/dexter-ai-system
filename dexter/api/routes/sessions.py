from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from ..deps import llm

router = APIRouter(prefix="/sessions", tags=["sessions"])

class SessionTagRequest(BaseModel):
    session_tag: Optional[str] = None

class SessionTagResponse(BaseModel):
    session_tag: Optional[str] = None
    status: str = "success"

class SessionListResponse(BaseModel):
    sessions: List[str]
    status: str = "success"

class SessionHistoryResponse(BaseModel):
    history: List[Dict]
    status: str = "success"

class LoadSessionResponse(BaseModel):
    status: str = "success"
    message: str

@router.get("/session-tag", response_model=SessionTagResponse)
async def get_session_tag():
    return SessionTagResponse(session_tag=llm.session_tag)

@router.post("/session-tag", response_model=SessionTagResponse)
async def set_session_tag(request: SessionTagRequest):
    llm.session_tag = request.session_tag
    return SessionTagResponse(session_tag=llm.session_tag)

@router.get("/", response_model=SessionListResponse)
async def list_sessions():
    return SessionListResponse(sessions=llm.history_manager.list_sessions())

@router.get("/{session_tag}", response_model=SessionHistoryResponse)
async def get_session_history(session_tag: str):
    return SessionHistoryResponse(history=llm.history_manager.get_session_history(session_tag))

@router.delete("/{session_tag}")
async def delete_session(session_tag: str) -> Dict[str, str]:
    success = llm.history_manager.delete_session(session_tag)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"status": "success", "message": f"Session '{session_tag}' deleted"}

@router.post("/{session_tag}/load", response_model=LoadSessionResponse)
async def load_session(session_tag: str):
    system_prompt, history = llm.history_manager.load_session_into_history(session_tag)
    llm.history = history
    llm.system_prompt = system_prompt
    return LoadSessionResponse(message=f"Session '{session_tag}' loaded into conversation history")
