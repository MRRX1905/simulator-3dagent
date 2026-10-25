import uuid
import json
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.models import TaskModel
from app.database import get_connection

router = APIRouter(prefix="/tasks", tags=["Tasks"])

class CreateTaskRequest(BaseModel):
    title: Optional[str] = None        # derived from goal[:60] when absent
    goal: str
    priority: float = 0.5
    assigned_to: Optional[str] = None
    target_role: Optional[str] = "manager"
    requirements: Dict[str, Any] = {}

@router.get("", response_model=List[TaskModel])
async def list_tasks(status: Optional[str] = None):
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC", (status,))
    else:
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()

    tasks = []
    for r in rows:
        tasks.append(TaskModel(
            id=r["id"],
            title=r["title"],
            goal=r["goal"],
            created_by=r["created_by"],
            assigned_to=r["assigned_to"],
            status=r["status"],
            priority=r["priority"],
            risk=r["risk"],
            requirements=json.loads(r["requirements_json"] or "{}"),
            result=json.loads(r["result_json"]) if r["result_json"] else None,
            blockers=json.loads(r["blockers_json"] or "[]"),
            created_at=r["created_at"],
            updated_at=r["updated_at"]
        ))
    return tasks

@router.post("", response_model=TaskModel)
async def create_task(req: CreateTaskRequest):
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    title = req.title or req.goal[:60]
    requirements = dict(req.requirements)
    if req.target_role:
        requirements["target_role"] = req.target_role

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (id, title, goal, created_by, assigned_to, status, priority, risk, requirements_json, created_at, updated_at)
        VALUES (?, ?, ?, 'user', ?, 'PENDING', ?, 'low', ?, datetime('now'), datetime('now'))
    """, (task_id, title, req.goal, req.assigned_to, req.priority, json.dumps(requirements)))
    conn.commit()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    r = cursor.fetchone()
    conn.close()

    return TaskModel(
        id=r["id"],
        title=r["title"],
        goal=r["goal"],
        created_by=r["created_by"],
        assigned_to=r["assigned_to"],
        status=r["status"],
        priority=r["priority"],
        risk=r["risk"],
        requirements=json.loads(r["requirements_json"] or "{}"),
        result=None,
        blockers=[],
        created_at=r["created_at"],
        updated_at=r["updated_at"]
    )

@router.get("/{task_id}", response_model=TaskModel)
async def get_task(task_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    r = cursor.fetchone()
    conn.close()

    if not r:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskModel(
        id=r["id"],
        title=r["title"],
        goal=r["goal"],
        created_by=r["created_by"],
        assigned_to=r["assigned_to"],
        status=r["status"],
        priority=r["priority"],
        risk=r["risk"],
        requirements=json.loads(r["requirements_json"] or "{}"),
        result=json.loads(r["result_json"]) if r["result_json"] else None,
        blockers=json.loads(r["blockers_json"] or "[]"),
        created_at=r["created_at"],
        updated_at=r["updated_at"]
    )


@router.post("/{task_id}/run")
async def run_task_now(task_id: str):
    """Immediately execute a task — used by the browser client to skip scheduler wait."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Task not found")

    reqs = json.loads(row["requirements_json"] or "{}")
    target_role = reqs.get("target_role", "developer")

    # Find or default agent
    conn2 = get_connection()
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT id FROM agents WHERE role = ? LIMIT 1", (target_role,))
    agent_row = cursor2.fetchone()
    if not agent_row:
        cursor2.execute("SELECT id FROM agents LIMIT 1")
        agent_row = cursor2.fetchone()

    agent_id = row["assigned_to"] or (agent_row["id"] if agent_row else "agent_dev_01")

    cursor2.execute("""
        UPDATE tasks SET status = 'RUNNING', assigned_to = ?, updated_at = datetime('now')
        WHERE id = ?
    """, (agent_id, task_id))
    conn2.commit()
    conn2.close()

    task_obj = TaskModel(
        id=row["id"],
        title=row["title"],
        goal=row["goal"],
        created_by=row["created_by"],
        assigned_to=agent_id,
        status="RUNNING",
        priority=row["priority"],
        risk=row["risk"],
        requirements=reqs,
        blockers=json.loads(row["blockers_json"] or "[]"),
        created_at=row["created_at"],
        updated_at=row["updated_at"]
    )

    from app.agents.registry import agent_registry as reg
    from app.core.scheduler import world_scheduler
    instance = reg.get_agent_instance(agent_id)
    if instance:
        import asyncio
        asyncio.create_task(world_scheduler._run_agent_task(instance, task_obj))

    return {"status": "running", "task_id": task_id, "agent_id": agent_id}

