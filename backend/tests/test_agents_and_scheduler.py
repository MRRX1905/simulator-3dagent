import pytest
from app.core.state_machine import AgentState, can_transition
from app.agents.registry import agent_registry
from app.models import TaskModel
from app.core.scheduler import world_scheduler

def test_state_machine_transitions():
    assert can_transition(AgentState.IDLE, AgentState.PLANNING) is True
    assert can_transition(AgentState.PLANNING, AgentState.EXECUTING) is True
    assert can_transition(AgentState.EXECUTING, AgentState.REVIEWING) is True
    assert can_transition(AgentState.DONE, AgentState.IDLE) is True
    # Invalid jump
    assert can_transition(AgentState.DONE, AgentState.EXECUTING) is False

@pytest.mark.asyncio
async def test_developer_agent_execution():
    dev = agent_registry.get_agent_instance("agent_dev_01")
    assert dev is not None
    assert dev.role == "developer"

    task = TaskModel(
        id="task_test_dev_01",
        title="Create validation helper",
        goal="Buat fungsi validasi payload JSON",
        created_by="user",
        assigned_to="agent_dev_01"
    )

    result = await dev.execute_task(task)
    assert result["status"] == "completed"
    assert "artifact_path" in result
    assert result["iterations"] >= 1

@pytest.mark.asyncio
async def test_world_scheduler_tick():
    world_scheduler.stop()
    initial_minute = world_scheduler.minute
    tick_result = await world_scheduler.tick()
    
    assert tick_result["tick"] > 0
    assert "world_time" in tick_result
    assert world_scheduler.minute != initial_minute or world_scheduler.hour != 8
