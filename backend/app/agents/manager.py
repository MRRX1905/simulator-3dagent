import json
import uuid
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.models import TaskModel
from app.core.state_machine import AgentState
from app.llm.factory import get_llm_provider
from app.database import get_connection

class ManagerAgent(BaseAgent):
    """
    Citra - Manager Agent
    Receives high-level goals from user, breaks down into task graph, delegates to workers.
    """

    async def execute_task(self, task: TaskModel) -> Dict[str, Any]:
        self.set_status(AgentState.PLANNING)
        self.record_thought(f"Decomposing task '{task.title}' into subtasks.")

        prompt = (
            f"You are Manager Agent {self.name} in AI City.\n"
            f"Goal: {task.goal}\n"
            f"Breakdown this task into 2-4 subtasks with role assignments (developer, researcher, reviewer).\n"
            f"Return JSON with key 'subtasks': list of objects with 'role', 'goal', 'priority'."
        )

        llm = get_llm_provider()
        response_text = await llm.generate(prompt=prompt, system_prompt="You are a systematic Project Manager in AI City.")

        try:
            plan = json.loads(response_text)
            subtasks = plan.get("subtasks", [])
        except Exception:
            subtasks = [
                {"role": "developer", "goal": f"Implement core logic for {task.goal}", "priority": 0.8},
                {"role": "reviewer", "goal": f"Review implementation for {task.goal}", "priority": 0.9}
            ]

        self.set_status(AgentState.EXECUTING)

        created_subtask_ids = []
        conn = get_connection()
        cursor = conn.cursor()

        for st in subtasks:
            sub_id = f"task_{uuid.uuid4().hex[:8]}"
            cursor.execute("""
                INSERT INTO tasks (id, title, goal, created_by, status, priority, risk, requirements_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'PENDING', ?, 'low', ?, datetime('now'), datetime('now'))
            """, (
                sub_id,
                f"Subtask: {st.get('goal', 'Worker task')[:50]}",
                st.get("goal", ""),
                self.id,
                float(st.get("priority", 0.5)),
                json.dumps({"target_role": st.get("role", "developer")})
            ))
            created_subtask_ids.append(sub_id)

        conn.commit()
        conn.close()

        self.set_status(AgentState.DONE)
        self.set_status(AgentState.IDLE)

        return {
            "status": "planned",
            "manager": self.id,
            "created_subtasks": created_subtask_ids,
            "plan": subtasks
        }
