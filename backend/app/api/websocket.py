import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from app.core.scheduler import world_scheduler
from app.agents.registry import agent_registry

router = APIRouter(prefix="/ws", tags=["WebSocket Bridge"])

class ConnectionManager:
    def __init__(self):
        self.world_connections: List[WebSocket] = []
        self.agent_connections: List[WebSocket] = []

    async def connect_world(self, websocket: WebSocket):
        await websocket.accept()
        self.world_connections.append(websocket)

    def disconnect_world(self, websocket: WebSocket):
        if websocket in self.world_connections:
            self.world_connections.remove(websocket)

    async def connect_agent(self, websocket: WebSocket):
        await websocket.accept()
        self.agent_connections.append(websocket)

    def disconnect_agent(self, websocket: WebSocket):
        if websocket in self.agent_connections:
            self.agent_connections.remove(websocket)

manager = ConnectionManager()

@router.websocket("/world")
async def websocket_world_endpoint(websocket: WebSocket):
    await manager.connect_world(websocket)
    try:
        while True:
            # Send world pulse every 2 seconds
            data = {
                "event": "world_update",
                "world_time": world_scheduler.get_world_time(),
                "tick_count": world_scheduler.tick_count,
                "is_running": world_scheduler.is_running
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        manager.disconnect_world(websocket)
    except Exception:
        manager.disconnect_world(websocket)

@router.websocket("/agents")
async def websocket_agents_endpoint(websocket: WebSocket):
    await manager.connect_agent(websocket)
    try:
        while True:
            agents = agent_registry.get_all_agents()
            data = {
                "event": "agents_update",
                "count": len(agents),
                "agents": [
                    {
                        "id": a.id,
                        "name": a.name,
                        "role": a.role,
                        "status": a.status,
                        "location": a.location,
                        "needs": a.needs.model_dump()
                    }
                    for a in agents
                ]
            }
            await websocket.send_text(json.dumps(data))
            await asyncio.sleep(2.0)
    except WebSocketDisconnect:
        manager.disconnect_agent(websocket)
    except Exception:
        manager.disconnect_agent(websocket)
