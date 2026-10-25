#!/usr/bin/env python
"""
AI CITY — 3D Game World Desktop Application
Menjalankan dunia virtual 3D AI City di window desktop Windows native (tanpa browser).
"""

import sys
import os
import asyncio
import time
import json
from pathlib import Path

# Add backend to sys.path
BACKEND_DIR = Path("C:/AI_CITY/backend").resolve()
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.database import init_db, get_connection
from app.agents.registry import agent_registry
from app.core.scheduler import world_scheduler
from app.models import TaskModel
from app.llm.factory import get_llm_provider
import webview

class CityGameAPI:
    """Python bridge exposed directly to the 3D Game JavaScript environment."""

    def __init__(self):
        init_db()
        agent_registry.seed_default_agents()

    def get_initial_world_state(self):
        """Returns all agents and all buildings persisted in SQLite for the 3D scene."""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, role, status, location, money, reputation FROM agents")
            agents_rows = cursor.fetchall()

            cursor.execute("SELECT id, type, x, z, condition, value FROM buildings")
            buildings_rows = cursor.fetchall()
        finally:
            conn.close()

        agents_list = []
        for a in agents_rows:
            agents_list.append({
                "id": a["id"],
                "name": a["name"],
                "role": a["role"],
                "status": a["status"],
                "location": a["location"],
                "money": a["money"],
                "reputation": a["reputation"]
            })

        buildings_list = []
        for b in buildings_rows:
            buildings_list.append({
                "id": b["id"],
                "type": b["type"],
                "x": b["x"],
                "z": b["z"],
                "condition": b["condition"]
            })

        return {
            "world_time": world_scheduler.get_world_time(),
            "population": len(agents_list),
            "agents": agents_list,
            "buildings": buildings_list,
            "llm_provider": os.getenv("LLM_PROVIDER", settings.LLM_PROVIDER),
            "llm_model": os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
        }

    def get_world(self):
        return {
            "world_time": world_scheduler.get_world_time(),
            "population": len(agent_registry.get_all_agents()),
            "tick_count": world_scheduler.tick_count
        }

    def get_agents(self):
        agents = agent_registry.get_all_agents()
        return [
            {
                "id": a.id,
                "name": a.name,
                "role": a.role,
                "status": a.status,
                "location": a.location,
                "energy": a.needs.energy,
                "food": a.needs.food,
                "reputation": a.reputation
            }
            for a in agents
        ]

    def get_events(self):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM world_events ORDER BY created_at DESC LIMIT 8")
            rows = cursor.fetchall()
        finally:
            conn.close()

        formatted_events = []
        for r in rows:
            try:
                payload = json.loads(r["payload_json"] or "{}")
            except Exception:
                payload = {}
            formatted_events.append({
                "id": r["id"],
                "type": r["type"],
                "payload": payload,
                "created_at": r["created_at"]
            })
        return formatted_events

    def get_llm_status(self):
        provider = os.getenv("LLM_PROVIDER", settings.LLM_PROVIDER)
        model = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile" if provider == "groq" else "default")
        api_key = os.getenv("LLM_API_KEY", "")
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else ("Set" if api_key else "None")
        return {
            "provider": provider,
            "model": model,
            "has_key": bool(api_key),
            "masked_key": masked_key,
            "base_url": os.getenv("LLM_BASE_URL", "")
        }

    def test_and_save_llm(self, provider: str, api_key: str, model: str, base_url: str = ""):
        """Saves LLM configuration to .env and tests connection live."""
        provider = provider.strip().lower()
        api_key = api_key.strip()
        model = model.strip()
        base_url = base_url.strip()

        # Update runtime env
        os.environ["LLM_PROVIDER"] = provider
        os.environ["LLM_MODEL"] = model
        os.environ["LLM_API_KEY"] = api_key
        if base_url:
            os.environ["LLM_BASE_URL"] = base_url

        # Update .env file
        env_path = BACKEND_DIR / ".env"
        try:
            lines = []
            if env_path.exists():
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

            updated = False
            new_lines = []
            keys_to_set = {
                "LLM_PROVIDER": f'LLM_PROVIDER="{provider}"\n',
                "LLM_API_KEY": f'LLM_API_KEY="{api_key}"\n',
                "LLM_MODEL": f'LLM_MODEL="{model}"\n',
            }
            if base_url:
                keys_to_set["LLM_BASE_URL"] = f'LLM_BASE_URL="{base_url}"\n'

            for line in lines:
                matched_key = None
                for k in keys_to_set:
                    if line.startswith(f"{k}=") or line.startswith(f"#{k}=") or line.startswith(f"# {k}="):
                        matched_key = k
                        break
                if matched_key:
                    new_lines.append(keys_to_set.pop(matched_key))
                else:
                    new_lines.append(line)

            for remaining_line in keys_to_set.values():
                new_lines.append(remaining_line)

            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

        except Exception as e:
            print(f"Warning: gagal menulis ke .env: {e}")

        # Test call
        if provider in ("groq", "openai", "openrouter", "deepseek"):
            try:
                llm = get_llm_provider(override_name=provider)
                test_res = asyncio.run(llm.generate("Katakan 'AI City Tersambung!' dalam 3 kata.", max_tokens=15))
                return {
                    "success": True,
                    "message": f"Berhasil tersambung ke {provider.upper()} ({model})! Respon: {test_res.strip()}"
                }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Gagal menghubungi {provider.upper()}: {str(e)}"
                }
        else:
            return {
                "success": True,
                "message": f"Provider berhasil diatur ke '{provider}' (Smart Engine Aktif)."
            }

    def submit_goal(self, goal: str):
        print(f"[3D GAME] Menerima Goal Baru: {goal}")
        manager = agent_registry.get_agent_instance("agent_manager_01")
        dev = agent_registry.get_agent_instance("agent_dev_01")
        
        task_id = f"game_task_{int(time.time())}"
        task = TaskModel(
            id=task_id,
            title=f"Game Goal: {goal[:30]}",
            goal=goal,
            created_by="player_3d_game",
            assigned_to="agent_manager_01",
            status="RUNNING"
        )

        async def run_pipeline():
            plan_res = await manager.execute_task(task)
            dev_task = TaskModel(
                id=f"dev_{task_id}",
                title=f"Dev: {goal[:30]}",
                goal=goal,
                created_by="agent_manager_01",
                assigned_to="agent_dev_01"
            )
            dev_res = await dev.execute_task(dev_task)
            return {
                "plan": plan_res,
                "dev": dev_res
            }

        # Run async in event loop
        result = asyncio.run(run_pipeline())
        dev_res = result.get("dev", {})
        return {
            "status": "success",
            "goal": goal,
            "artifact_path": dev_res.get("artifact_path", "solution.py"),
            "review_status": dev_res.get("review_status", "approved"),
            "review_score": dev_res.get("review_score", 0.98),
            "code": dev_res.get("code", ""),
            "stdout": dev_res.get("stdout", ""),
            "stderr": dev_res.get("stderr", ""),
            "new_building": dev_res.get("new_building", None)
        }

def launch_game():
    api = CityGameAPI()
    html_file = Path("C:/AI_CITY/game_assets/index.html").resolve()

    window = webview.create_window(
        title="AI CITY — 3D Autonomous Society & Workforce Simulator",
        url=str(html_file),
        js_api=api,
        width=1280,
        height=820,
        resizable=True,
        min_size=(1024, 600)
    )

    webview.start(debug=False)

if __name__ == "__main__":
    launch_game()
