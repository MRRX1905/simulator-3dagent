import json
from typing import Dict, Any, List, Optional
from app.models import AgentModel, TaskModel
from app.core.state_machine import AgentState, can_transition
from app.database import get_connection
from app.memory.memory_store import memory_store

class BaseAgent:
    def __init__(self, data: AgentModel):
        self.data = data

    @property
    def id(self) -> str:
        return self.data.id

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def role(self) -> str:
        return self.data.role

    @property
    def status(self) -> str:
        return self.data.status

    def set_status(self, new_status: str) -> bool:
        if can_transition(self.data.status, new_status):
            self.data.status = new_status
            self._save_to_db()
            return True
        return False

    def decay_needs(self, food_delta: float = 0.01, energy_delta: float = 0.01):
        self.data.needs.food = max(0.0, round(self.data.needs.food - food_delta, 3))
        self.data.needs.energy = max(0.0, round(self.data.needs.energy - energy_delta, 3))
        self._save_to_db()

    def rest_and_eat(self):
        self.data.needs.food = 1.0
        self.data.needs.energy = 1.0
        self._save_to_db()

    def record_thought(self, thought: str, importance: float = 0.5):
        memory_store.record_memory(
            agent_id=self.id,
            mem_type="episodic",
            content=thought,
            importance=importance,
            source="self"
        )

    def _save_to_db(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE agents 
            SET status = ?, needs_json = ?, money = ?, reputation = ?, location = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (
            self.data.status,
            json.dumps(self.data.needs.model_dump()),
            self.data.money,
            self.data.reputation,
            self.data.location,
            self.id
        ))
        conn.commit()
        conn.close()

    async def execute_task(self, task: TaskModel) -> Dict[str, Any]:
        """Override in subclasses to implement role-specific behavior."""
        raise NotImplementedError
