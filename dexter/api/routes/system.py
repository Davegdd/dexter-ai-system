from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..deps import llm

router = APIRouter(prefix="/system-prompt", tags=["system"])

class SystemPromptRequest(BaseModel):
    system_prompt: str

class SystemPromptResponse(BaseModel):
    system_prompt: str
    status: str = "success"

@router.get("/", response_model=SystemPromptResponse)
async def get_system_prompt():
    try:
        return SystemPromptResponse(system_prompt=llm.system_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=SystemPromptResponse)
async def update_system_prompt(request: SystemPromptRequest):
    try:
        llm.system_prompt = request.system_prompt
        return SystemPromptResponse(system_prompt=llm.system_prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
