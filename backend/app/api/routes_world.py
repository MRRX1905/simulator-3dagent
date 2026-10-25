import json
import os
from fastapi import APIRouter
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.core.scheduler import world_scheduler
from app.agents.registry import agent_registry
from app.database import get_connection
from app.config import settings

router = APIRouter(tags=["World & Simulation"])

@router.get("/world")
async def get_world_state():
    return await _world_summary()

@router.get("/world/status")
async def get_world_status():
    """Alias used by the browser JS client."""
    return await _world_summary()

@router.get("/world/llm-status")
async def get_llm_status():
    """Return current active LLM provider config."""
    return {
        "provider": os.getenv("LLM_PROVIDER", settings.LLM_PROVIDER),
        "model": os.getenv("LLM_MODEL", settings.OLLAMA_MODEL if os.getenv("LLM_PROVIDER", settings.LLM_PROVIDER) == "ollama" else "llama-3.3-70b-versatile"),
        "base_url": os.getenv("LLM_BASE_URL", settings.OLLAMA_BASE_URL if os.getenv("LLM_PROVIDER", settings.LLM_PROVIDER) == "ollama" else ""),
    }

@router.get("/world/state")
async def get_initial_world_state_http():
    """Full initial payload — agents + buildings — for the browser 3D client."""
    agents_data = agent_registry.get_all_agents()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, type, x, z, condition, value FROM buildings")
    buildings_rows = cursor.fetchall()
    conn.close()

    return {
        "population": len(agents_data),
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": os.getenv("LLM_MODEL", "llama-3.3-70b-versatile"),
        "agents": [
            {
                "id": a.id,
                "name": a.name,
                "role": a.role,
                "status": a.status,
                "location": a.location,
                "money": a.money,
                "reputation": a.reputation,
            }
            for a in agents_data
        ],
        "buildings": [
            {"id": b["id"], "type": b["type"], "x": b["x"], "z": b["z"]}
            for b in buildings_rows
        ]
    }

@router.get("/world/events")
async def list_world_events_alias(limit: int = 20):
    """Alias used by the browser JS client (same as /events)."""
    return await _load_events(limit)

@router.get("/events")
async def list_world_events(limit: int = 20):
    return await _load_events(limit)

class LlmConfigRequest(BaseModel):
    provider: str
    api_key: Optional[str] = ""
    model: Optional[str] = ""
    base_url: Optional[str] = ""

@router.post("/world/llm-config")
async def update_llm_config(req: LlmConfigRequest):
    """Save LLM config to .env and hot-reload the provider."""
    env_path = settings.DATABASE_PATH.parent.parent / ".env"
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        def set_line(lines, key, val):
            for i, l in enumerate(lines):
                if l.startswith(f"{key}=") or l.startswith(f"# {key}="):
                    lines[i] = f'{key}="{val}"\n'
                    return lines
            lines.append(f'{key}="{val}"\n')
            return lines

        lines = set_line(lines, "LLM_PROVIDER", req.provider)
        if req.api_key:
            lines = set_line(lines, "LLM_API_KEY", req.api_key)
        if req.model:
            lines = set_line(lines, "LLM_MODEL", req.model)
        if req.base_url:
            lines = set_line(lines, "LLM_BASE_URL", req.base_url)

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)

        # Update os.environ so factory picks up new values immediately
        os.environ["LLM_PROVIDER"] = req.provider
        if req.api_key:
            os.environ["LLM_API_KEY"] = req.api_key
        if req.model:
            os.environ["LLM_MODEL"] = req.model
        if req.base_url:
            os.environ["LLM_BASE_URL"] = req.base_url

        # Skip live test for mock
        if req.provider == "mock":
            return {"success": True, "message": "✅ Smart Offline Engine aktif."}

        # For Ollama: test connectivity by hitting /api/tags (list models)
        if req.provider == "ollama":
            import httpx
            base = (req.base_url or "http://127.0.0.1:11434").rstrip("/")
            model_name = req.model or "qwen2.5:3b"
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    r = await client.get(f"{base}/api/tags")
                    if r.status_code != 200:
                        return {"success": False, "message": f"Ollama tidak merespons di {base}. Pastikan Ollama sudah dijalankan."}
                    available = [m["name"] for m in r.json().get("models", [])]
                    if not available:
                        return {"success": False, "message": f"Ollama berjalan tapi belum ada model. Jalankan: ollama pull {model_name}"}
                    if not any(model_name.split(":")[0] in m for m in available):
                        return {"success": False, "message": f"Model '{model_name}' belum diunduh. Jalankan: ollama pull {model_name}\nModel tersedia: {', '.join(available[:5])}"}
                    return {"success": True, "message": f"✅ Ollama aktif! Model '{model_name}' siap digunakan."}
            except Exception as e:
                return {"success": False, "message": f"Tidak bisa terhubung ke Ollama di {base}. Pastikan Ollama sudah diinstall dan berjalan.\nError: {e}"}

        # For Groq/OpenAI: do a quick generate test
        from app.llm.factory import get_llm_provider
        provider_obj = get_llm_provider(req.provider)
        test_reply = await provider_obj.generate("Say 'OK' in one word.", max_tokens=8)
        if not test_reply:
            return {"success": False, "message": "Provider tersambung tapi tidak merespons."}
        return {"success": True, "message": f"✅ Provider {req.provider} aktif & terverifikasi!"}

    except Exception as e:
        return {"success": False, "message": f"Gagal: {str(e)}"}


async def _world_summary():
    agents_data = agent_registry.get_all_agents()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM tasks WHERE status IN ('PENDING','RUNNING')")
    active_tasks = cursor.fetchone()["cnt"]
    cursor.execute("SELECT COUNT(*) as cnt FROM buildings")
    building_count = cursor.fetchone()["cnt"]
    conn.close()
    return {
        "world_time": world_scheduler.get_world_time(),
        "tick_count": world_scheduler.tick_count,
        "is_running": world_scheduler.is_running,
        "population": len(agents_data),
        "active_tasks": active_tasks,
        "buildings": building_count
    }

async def _load_events(limit: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM world_events ORDER BY created_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "type": r["type"],
            "severity": r["severity"],
            "payload": json.loads(r["payload_json"] or "{}"),
            "created_at": r["created_at"]
        }
        for r in rows
    ]


@router.post("/simulation/tick")
async def trigger_simulation_tick():
    result = await world_scheduler.tick()
    return result

@router.post("/simulation/pause")
async def pause_simulation():
    world_scheduler.stop()
    return {"status": "paused", "world_time": world_scheduler.get_world_time()}

@router.post("/simulation/resume")
async def resume_simulation():
    world_scheduler.start()
    return {"status": "running", "world_time": world_scheduler.get_world_time()}
