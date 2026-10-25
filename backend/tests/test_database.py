import pytest
from app.database import get_connection, init_db
from app.memory.memory_store import memory_store

def test_database_init_and_tables():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {r["name"] for r in cursor.fetchall()}
    conn.close()

    expected = {"agents", "memories", "skills", "agent_skills", "tasks", "messages", "artifacts", "buildings", "world_events", "approvals"}
    assert expected.issubset(tables)

def test_memory_store_operations():
    mem = memory_store.record_memory(
        agent_id="agent_dev_01",
        mem_type="episodic",
        content="Test memory insertion",
        importance=0.8,
        source="unit_test"
    )
    assert mem.id.startswith("mem_")
    assert mem.agent_id == "agent_dev_01"

    retrieved = memory_store.get_memories_for_agent("agent_dev_01", mem_type="episodic", limit=5)
    assert any(m.id == mem.id for m in retrieved)
