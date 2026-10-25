from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.models import TaskModel
from app.core.state_machine import AgentState
from app.peer_review.protocol import ReviewRequest
from app.peer_review.engine import peer_review_engine

class ReviewerAgent(BaseAgent):
    """
    Bima - QA / Reviewer Agent
    Performs evidence-based quality assurance, boundary condition checks,
    and structured peer reviews.
    """

    async def execute_task(self, task: TaskModel) -> Dict[str, Any]:
        self.set_status(AgentState.REVIEWING)
        self.record_thought(f"Conducting quality assurance for task '{task.title}'")

        artifact_path = task.requirements.get("artifact_path", "solution.py")
        artifact_id = task.requirements.get("artifact_id", "art_unknown")

        request = ReviewRequest(
            artifact_id=artifact_id,
            task_id=task.id,
            author_agent=task.requirements.get("author_agent", "unknown"),
            artifact_path=artifact_path,
            criteria=["correctness", "security", "input validation"],
            context=task.goal
        )

        result = await peer_review_engine.conduct_review(request, reviewer_agent_id=self.id)

        self.set_status(AgentState.DONE)
        self.set_status(AgentState.IDLE)

        return {
            "status": "reviewed",
            "reviewer": self.id,
            "review_status": result.status,
            "findings_count": len(result.findings),
            "score": result.score
        }
