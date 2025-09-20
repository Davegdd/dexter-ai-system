import threading, uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from dexter.agents.agents_executors import AGENTS
from concurrent.futures import Future

router = APIRouter(prefix="/agents", tags=["agents"])

active_agents: Dict[str, Future] = {}
agent_results: Dict[str, Dict[str, Any]] = {}

class AgentRequest(BaseModel):
    agent_name: str
    task: str
    additional_args: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    agent_id: str
    status: str = "started"
    message: str

class AgentStatusResponse(BaseModel):
    agent_id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None

class AgentListResponse(BaseModel):
    agents: List[str]
    status: str = "success"

@router.get("/", response_model=AgentListResponse)
async def list_agents():
    return AgentListResponse(agents=list(AGENTS.keys()))

@router.post("/execute", response_model=AgentResponse)
async def execute_agent(request: AgentRequest):
    if request.agent_name not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent '{request.agent_name}' not found")

    agent_id = str(uuid.uuid4())
    future = AGENTS[request.agent_name](request.task, request.additional_args)
    active_agents[agent_id] = future

    def monitor_completion() -> None:
        try:
            result = future.result()
            agent_results[agent_id] = {"status": "completed", "result": result}
        except Exception as e:
            agent_results[agent_id] = {"status": "failed", "error": str(e)}
        finally:
            active_agents.pop(agent_id, None)

    threading.Thread(target=monitor_completion, daemon=True).start()
    return AgentResponse(agent_id=agent_id, message=f"Agent '{request.agent_name}' started successfully")

@router.get("/{agent_id}/status", response_model=AgentStatusResponse)
async def get_agent_status(agent_id: str):
    if agent_id in active_agents:
        return AgentStatusResponse(agent_id=agent_id, status="running")
    if agent_id in agent_results:
        result_data = agent_results[agent_id]
        return AgentStatusResponse(agent_id=agent_id, status=result_data["status"], result=result_data.get("result"), error=result_data.get("error"))
    raise HTTPException(status_code=404, detail="Agent execution not found")

@router.delete("/{agent_id}")
async def cancel_agent(agent_id: str) -> Dict[str, str]:
    active_agents.pop(agent_id, None)
    agent_results.pop(agent_id, None)
    return {"status": "success", "message": f"Agent {agent_id} cancelled/cleaned up"}
