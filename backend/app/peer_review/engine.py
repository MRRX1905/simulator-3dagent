import json
import uuid
from typing import Dict, Any, List
from app.peer_review.protocol import ReviewRequest, ReviewResult, Finding
from app.tools.gateway import tool_gateway
from app.llm.factory import get_llm_provider
from app.memory.memory_store import memory_store
from app.database import get_connection

class PeerReviewEngine:
    """
    Orchestrates evidence-based peer review between agents.
    Prevents sycophancy by requiring concrete findings, severity, and evidence.
    """

    async def conduct_review(
        self,
        request: ReviewRequest,
        reviewer_agent_id: str
    ) -> ReviewResult:
        # Read artifact from workspace
        try:
            content = tool_gateway.fs.read_file(request.artifact_path)
        except Exception as e:
            return ReviewResult(
                artifact_id=request.artifact_id,
                author_agent=request.author_agent,
                reviewer_agent=reviewer_agent_id,
                status="rejected",
                score=0.0,
                criteria=request.criteria,
                findings=[Finding(
                    severity="critical",
                    missing="Artifact unreadable or missing from workspace",
                    recommendation=str(e)
                )],
                evidence=f"File read failed: {str(e)}"
            )

        prompt = (
            f"You are QA/Reviewer agent {reviewer_agent_id}. Review the following artifact written by {request.author_agent}.\n"
            f"Criteria: {', '.join(request.criteria)}\n"
            f"Task context: {request.context or 'General task'}\n\n"
            f"Artifact content:\n```\n{content}\n```\n\n"
            f"Evaluate objectively. Return JSON with keys: status ('approved' or 'needs_revision'), score (0.0 to 1.0), "
            f"findings (list of objects with severity, missing, recommendation), and evidence (specific description of evidence)."
        )

        llm = get_llm_provider()
        response_text = await llm.generate(prompt=prompt, system_prompt="You are a strict QA Reviewer in AI City.")

        try:
            data = json.loads(response_text)
            status = data.get("status", "needs_revision")
            score = float(data.get("score", 0.5))
            findings_raw = data.get("findings", [])
            evidence = data.get("evidence", "Review based on criteria inspection")

            findings = [
                Finding(
                    severity=f.get("severity", "medium"),
                    missing=f.get("missing", "Unspecified gap"),
                    recommendation=f.get("recommendation", "Address missing criteria")
                )
                for f in findings_raw
            ]
        except Exception:
            # Fallback parsing
            findings = []
            status = "approved" if "approved" in response_text.lower() else "needs_revision"
            score = 0.9 if status == "approved" else 0.6
            evidence = "Evaluated via fallback heuristics"

        review_result = ReviewResult(
            artifact_id=request.artifact_id,
            author_agent=request.author_agent,
            reviewer_agent=reviewer_agent_id,
            status=status,
            score=score,
            criteria=request.criteria,
            findings=findings,
            evidence=evidence
        )

        # Store in episodic memory for both author and reviewer
        memory_store.record_memory(
            agent_id=request.author_agent,
            mem_type="episodic",
            content=f"Received peer review from {reviewer_agent_id}: status={status}, score={score}. Findings: {len(findings)}",
            importance=0.7,
            source=reviewer_agent_id
        )

        memory_store.record_memory(
            agent_id=reviewer_agent_id,
            mem_type="episodic",
            content=f"Conducted peer review on {request.artifact_id} for {request.author_agent}: status={status}",
            importance=0.6,
            source=request.author_agent
        )

        # Record advice message in DB
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages (id, from_agent, to_agent, type, subject, payload_json, requires_response, created_at)
            VALUES (?, ?, ?, 'REVIEW', ?, ?, ?, datetime('now'))
        """, (
            f"msg_{uuid.uuid4().hex[:8]}",
            reviewer_agent_id,
            request.author_agent,
            f"Peer Review for {request.artifact_id}",
            json.dumps(review_result.model_dump()),
            1 if status == "needs_revision" else 0
        ))
        conn.commit()
        conn.close()

        return review_result

peer_review_engine = PeerReviewEngine()
