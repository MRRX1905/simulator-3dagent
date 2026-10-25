import json
from typing import List, Dict, Any, Optional
from app.database import get_connection
from app.models import ApprovalModel

class ApprovalManager:
    """
    Manages human authorization for Zone C (High Risk) and Zone D (Critical) actions.
    """

    def list_pending_approvals(self) -> List[ApprovalModel]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM approvals WHERE status = 'PENDING' ORDER BY created_at ASC")
        rows = cursor.fetchall()
        conn.close()

        approvals = []
        for r in rows:
            approvals.append(ApprovalModel(
                id=r["id"],
                task_id=r["task_id"],
                agent_id=r["agent_id"],
                zone=r["zone"],
                action=r["action"],
                details=json.loads(r["details_json"] or "{}"),
                status=r["status"],
                reviewed_by=r["reviewed_by"],
                created_at=r["created_at"],
                resolved_at=r["resolved_at"]
            ))
        return approvals

    def resolve_approval(self, approval_id: str, approved: bool, reviewer: str = "human_admin") -> Optional[ApprovalModel]:
        status = "APPROVED" if approved else "REJECTED"
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE approvals 
            SET status = ?, reviewed_by = ?, resolved_at = datetime('now')
            WHERE id = ?
        """, (status, reviewer, approval_id))
        
        cursor.execute("SELECT * FROM approvals WHERE id = ?", (approval_id,))
        r = cursor.fetchone()
        conn.commit()
        conn.close()

        if not r:
            return None

        return ApprovalModel(
            id=r["id"],
            task_id=r["task_id"],
            agent_id=r["agent_id"],
            zone=r["zone"],
            action=r["action"],
            details=json.loads(r["details_json"] or "{}"),
            status=r["status"],
            reviewed_by=r["reviewed_by"],
            created_at=r["created_at"],
            resolved_at=r["resolved_at"]
        )

approval_manager = ApprovalManager()
