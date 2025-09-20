from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import asyncio
from ..deps import llm

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatMessage(BaseModel):
    message: str
    base64_data: str | None = None
    file_type: str | None = None

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

class NewConversationResponse(BaseModel):
    status: str = "success"
    message: str

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatMessage) -> ChatResponse:
    try:
        formatted_message = [{"type": "text", "text": request.message}]
        loop = asyncio.get_event_loop()

        if request.base64_data:
            await loop.run_in_executor(None, llm.llm_input, formatted_message, request.base64_data, request.file_type)
        else:
            await loop.run_in_executor(None, llm.llm_input, formatted_message)

        speech_text = getattr(llm, "speech_text", "")
        complete_response = getattr(llm, "complete_response", "No response generated")
        return ChatResponse(response=speech_text or complete_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/new-conversation", response_model=NewConversationResponse)
async def start_new_conversation():
    """Start a new conversation by clearing current history"""
    llm.new_history = True
    return NewConversationResponse(message="New conversation started successfully")
