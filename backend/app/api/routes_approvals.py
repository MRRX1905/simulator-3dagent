from fastapi import APIRouter, HTTPException
from typing import List
from app.models import ApprovalModel
from app.safety.approval_manager import approval_manager

router = APIRouter(prefix="/approvals", tags=["Approvals (Safety Gateway)"])

@router.get("", response_model=List[ApprovalModel])
async def list_pending_approvals():
    return approval_manager.list_pending_approvals()

@router.post("/{approval_id}/approve", response_model=ApprovalModel)
async def approve_request(approval_id: str):
    res = approval_manager.resolve_approval(approval_id, approved=True)
    if not res:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return res

@router.post("/{approval_id}/reject", response_model=ApprovalModel)
async def reject_request(approval_id: str):
    res = approval_manager.resolve_approval(approval_id, approved=False)
    if not res:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return res
