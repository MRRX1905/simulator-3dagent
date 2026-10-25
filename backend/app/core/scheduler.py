import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.config import settings
from app.database import get_connection
from app.agents.registry import agent_registry
from app.models import TaskModel

class WorldScheduler:
    """
    Simulation heart of AI City:
    Executes world ticks, updates needs, dispatches pending tasks,
    and maintains the autonomous life loop.
    """

    def __init__(self):
        self.day: int = 1
        self.hour: int = 8
        self.minute: int = 0
        self.is_running: bool = False
        self._task: Optional[asyncio.Task] = None
        self.tick_count: int = 0

    def get_world_time(self) -> str:
        return f"Day {self.day} {self.hour:02d}:{self.minute:02d}"

    def advance_time(self, minutes: int = 10):
        self.minute += minutes
        if self.minute >= 60:
            self.hour += self.minute // 60
            self.minute %= 60
        if self.hour >= 24:
            self.day += self.hour // 24
            self.hour %= 24

    async def tick(self) -> Dict[str, Any]:
        self.tick_count += 1
        self.advance_time(10)

        # 1. Database operations under a single connection
        dispatched_tasks = []
        conn = get_connection()
        try:
            cursor = conn.cursor()

            # Decay needs of active agents
            all_agents = agent_registry.get_all_agents()
            for a in all_agents:
                instance = agent_registry.get_agent_instance(a.id)
                if instance:
                    instance.data.needs.food = max(0.0, round(instance.data.needs.food - 0.005, 3))
                    instance.data.needs.energy = max(0.0, round(instance.data.needs.energy - 0.005, 3))
                    cursor.execute("""
                        UPDATE agents SET needs_json = ?, updated_at = datetime('now') WHERE id = ?
                    """, (json.dumps(instance.data.needs.model_dump()), instance.id))

            # 2. Check for pending tasks and dispatch to idle agents
            cursor.execute("SELECT * FROM tasks WHERE status = 'PENDING' ORDER BY priority DESC LIMIT 3")
            pending_tasks = cursor.fetchall()

            for pt in pending_tasks:
                reqs = json.loads(pt["requirements_json"] or "{}")
                target_role = reqs.get("target_role")

                # Find matching idle agent
                cursor.execute("SELECT id FROM agents WHERE status = 'IDLE' AND role = ? LIMIT 1", (target_role,))
                idle_agent = cursor.fetchone()
                
                # If no role specified, assign to manager if available
                if not idle_agent and not target_role:
                    cursor.execute("SELECT id FROM agents WHERE status = 'IDLE' AND role = 'manager' LIMIT 1")
                    idle_agent = cursor.fetchone()

                if idle_agent:
                    agent_id = idle_agent["id"]
                    task_id = pt["id"]

                    # Mark running and assigned
                    cursor.execute("""
                        UPDATE tasks SET status = 'RUNNING', assigned_to = ?, updated_at = datetime('now')
                        WHERE id = ?
                    """, (agent_id, task_id))

                    task_obj = TaskModel(
                        id=pt["id"],
                        title=pt["title"],
                        goal=pt["goal"],
                        created_by=pt["created_by"],
                        assigned_to=agent_id,
                        status="RUNNING",
                        priority=pt["priority"],
                        risk=pt["risk"],
                        requirements=reqs,
                        blockers=json.loads(pt["blockers_json"] or "[]"),
                        created_at=pt["created_at"],
                        updated_at=pt["updated_at"]
                    )

                    instance = agent_registry.get_agent_instance(agent_id)
                    if instance:
                        asyncio.create_task(self._run_agent_task(instance, task_obj))
                        dispatched_tasks.append({"task_id": task_id, "agent_id": agent_id})

            # 3. Record world event log
            event_id = f"evt_{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO world_events (id, type, severity, payload_json, created_at)
                VALUES (?, 'world_tick', 'info', ?, datetime('now'))
            """, (event_id, json.dumps({
                "world_time": self.get_world_time(),
                "tick": self.tick_count,
                "dispatched_count": len(dispatched_tasks)
            })))
            conn.commit()
        finally:
            conn.close()

        return {
            "tick": self.tick_count,
            "world_time": self.get_world_time(),
            "dispatched_tasks": dispatched_tasks
        }

    async def _run_agent_task(self, agent_instance, task: TaskModel):
        try:
            result = await agent_instance.execute_task(task)
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks SET status = 'PASSED', result_json = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (json.dumps(result), task.id))
            conn.commit()
            conn.close()
        except Exception as e:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks SET status = 'FAILED', result_json = ?, updated_at = datetime('now')
                WHERE id = ?
            """, (json.dumps({"error": str(e)}), task.id))
            conn.commit()
            conn.close()
            agent_instance.set_status("IDLE")

    async def _loop(self):
        while self.is_running:
            await self.tick()
            await asyncio.sleep(settings.TICK_INTERVAL_SECONDS / settings.SIMULATION_SPEED)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._loop())

    def stop(self):
        self.is_running = False
        if self._task:
            self._task.cancel()
            self._task = None

world_scheduler = WorldScheduler()
