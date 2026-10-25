import pytest
from app.peer_review.protocol import ReviewRequest
from app.peer_review.engine import peer_review_engine
from app.tools.gateway import tool_gateway

@pytest.mark.asyncio
async def test_peer_review_lifecycle():
    # 1. Author writes artifact
    artifact_path = "modules/auth.py"
    tool_gateway.fs.write_file(
        artifact_path,
        "def authenticate(user, pwd):\n    return True\n"
    )

    # 2. Review requested
    req = ReviewRequest(
        artifact_id="art_test_01",
        task_id="task_test_01",
        author_agent="agent_dev_01",
        artifact_path=artifact_path,
        criteria=["input validation", "security"],
        context="User authentication function"
    )

    # 3. Review conducted
    result = await peer_review_engine.conduct_review(req, reviewer_agent_id="agent_reviewer_01")
    assert result.artifact_id == "art_test_01"
    assert result.reviewer_agent == "agent_reviewer_01"
    assert result.status in ("approved", "needs_revision")
    assert result.evidence != ""
