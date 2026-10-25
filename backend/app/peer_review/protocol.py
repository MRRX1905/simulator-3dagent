from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class Finding(BaseModel):
    severity: str  # low, medium, high, critical
    missing: str   # description of what is missing or incorrect
    recommendation: str  # actionable fix

class ReviewResult(BaseModel):
    artifact_id: str
    author_agent: str
    reviewer_agent: str
    status: str  # approved, needs_revision, rejected
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    criteria: List[str] = Field(default_factory=list)
    findings: List[Finding] = Field(default_factory=list)
    evidence: str
    created_at: str = Field(default_factory=utc_now)

class ReviewRequest(BaseModel):
    artifact_id: str
    task_id: str
    author_agent: str
    artifact_path: str
    criteria: List[str]
    context: Optional[str] = None
