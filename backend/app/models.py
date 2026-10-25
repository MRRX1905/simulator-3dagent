from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

class PersonalityModel(BaseModel):
    openness: float = 0.5
    conscientiousness: float = 0.5
    social: float = 0.5
    risk_tolerance: float = 0.5

class NeedsModel(BaseModel):
    food: float = 1.0       # 0.0 to 1.0 (1.0 = satisfied)
    energy: float = 1.0     # 0.0 to 1.0 (1.0 = fully rested)
    money: float = 1.0      # satisfaction with funds
    social: float = 1.0     # satisfaction with interaction

class AgentModel(BaseModel):
    id: str
    name: str
    role: str
    age: int = 25
    personality: PersonalityModel = Field(default_factory=PersonalityModel)
    needs: NeedsModel = Field(default_factory=NeedsModel)
    goals: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    location: str = "plaza"
    money: float = 1000.0
    reputation: int = 50
    memory_refs: List[str] = Field(default_factory=list)
    relationships: Dict[str, Any] = Field(default_factory=dict)
    status: str = "IDLE"  # IDLE, PLANNING, EXECUTING, WAITING_TOOL, REVIEWING, LEARNING, DONE
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)

class MemoryModel(BaseModel):
    id: str
    agent_id: str
    type: str  # episodic, semantic, procedural
    content: str
    importance: float = 0.5  # 0.0 to 1.0
    source: Optional[str] = None
    created_at: str = Field(default_factory=utc_now)

class SkillModel(BaseModel):
    id: str
    name: str
    category: str
    level: int = 1  # 0: untrained, 1: beginner, 2: procedural, 3: autonomous, 4: expert, 5: mentor
    description: str
    prerequisites: List[str] = Field(default_factory=list)
    procedures: List[str] = Field(default_factory=list)
    tests: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    validated: bool = False
    confidence: float = 0.5
    version: int = 1

class TaskModel(BaseModel):
    id: str
    title: str
    goal: str
    created_by: str  # user or agent_id
    assigned_to: Optional[str] = None
    status: str = "PENDING"  # PENDING, RUNNING, REVIEW, BLOCKED, PASSED, FAILED, CANCELLED
    priority: float = 0.5
    risk: str = "low"  # low, medium, high, critical (Zone A, B, C, D)
    requirements: Dict[str, Any] = Field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    blockers: List[str] = Field(default_factory=list)
    created_at: str = Field(default_factory=utc_now)
    updated_at: str = Field(default_factory=utc_now)

class MessageModel(BaseModel):
    id: str
    from_agent: str
    to_agent: str
    type: str  # TASK, ADVICE, REVIEW, REQUEST_HELP, OFFER_SKILL, KNOWLEDGE_SHARE, ALERT
    subject: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    requires_response: bool = False
    created_at: str = Field(default_factory=utc_now)

class ArtifactModel(BaseModel):
    id: str
    task_id: str
    author_agent: str
    path: str
    type: str  # py, docx, json, md, test, report
    hash: Optional[str] = None
    created_at: str = Field(default_factory=utc_now)

class BuildingModel(BaseModel):
    id: str
    type: str  # house, apartment, office, shop, road, park, construction_site
    owner_agent_id: Optional[str] = None
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    condition: float = 1.0
    value: float = 10000.0

class WorldEventModel(BaseModel):
    id: str
    type: str
    severity: str = "info"  # info, warning, alert, emergency
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=utc_now)

class ApprovalModel(BaseModel):
    id: str
    task_id: Optional[str] = None
    agent_id: str
    zone: str  # C (High Risk) or D (Critical)
    action: str
    details: Dict[str, Any] = Field(default_factory=dict)
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED
    reviewed_by: Optional[str] = None
    created_at: str = Field(default_factory=utc_now)
    resolved_at: Optional[str] = None
