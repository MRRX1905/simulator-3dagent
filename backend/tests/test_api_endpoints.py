import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "ok"
        assert "world_time" in data

@pytest.mark.asyncio
async def test_agents_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/agents")
        assert res.status_code == 200
        agents = res.json()
        assert len(agents) >= 5
        assert any(a["name"] == "Ari" for a in agents)

        # Single agent details
        res_single = await client.get("/agents/agent_dev_01")
        assert res_single.status_code == 200
        assert res_single.json()["id"] == "agent_dev_01"

@pytest.mark.asyncio
async def test_tasks_lifecycle_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create task
        payload = {
            "title": "API Test Task",
            "goal": "Test task submission via API",
            "priority": 0.9,
            "target_role": "manager"
        }
        res = await client.post("/tasks", json=payload)
        assert res.status_code == 200
        created = res.json()
        assert created["status"] == "PENDING"
        task_id = created["id"]

        # Fetch task
        res_get = await client.get(f"/tasks/{task_id}")
        assert res_get.status_code == 200
        assert res_get.json()["id"] == task_id

@pytest.mark.asyncio
async def test_world_and_skills_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # World status
        res_world = await client.get("/world")
        assert res_world.status_code == 200
        assert "population" in res_world.json()

        # Skills list
        res_skills = await client.get("/skills")
        assert res_skills.status_code == 200
        skills = res_skills.json()
        assert len(skills) > 0
