from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.models import AgentModel, MemoryModel
from app.agents.registry import agent_registry
from app.skills.registry import skill_registry
from app.memory.memory_store import memory_store

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.get("", response_model=List[AgentModel])
async def list_agents():
    return agent_registry.get_all_agents()

@router.get("/{agent_id}", response_model=AgentModel)
async def get_agent(agent_id: str):
    instance = agent_registry.get_agent_instance(agent_id)
    if not instance:
        raise HTTPException(status_code=404, detail="Agent not found")
    return instance.data

@router.get("/{agent_id}/skills")
async def get_agent_skills(agent_id: str):
    return skill_registry.get_agent_skills(agent_id)

@router.get("/{agent_id}/memories", response_model=List[MemoryModel])
async def get_agent_memories(agent_id: str, limit: int = 15):
    return memory_store.get_memories_for_agent(agent_id, limit=limit)
