import json
from typing import Dict, Any, List, Optional
from app.models import AgentModel, PersonalityModel, NeedsModel
from app.database import get_connection
from app.agents.base_agent import BaseAgent
from app.agents.manager import ManagerAgent
from app.agents.developer import DeveloperAgent
from app.agents.reviewer import ReviewerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.skill_mentor import SkillMentorAgent

class AgentRegistry:
    """
    Manages active agent instances in AI City.
    """

    def __init__(self):
        self._instances: Dict[str, BaseAgent] = {}

    def seed_default_agents(self):
        default_agents = [
            AgentModel(
                id="agent_manager_01",
                name="Citra",
                role="manager",
                personality=PersonalityModel(conscientiousness=0.9, social=0.8, openness=0.7),
                goals=["Coordinate city workforce", "Ensure high-quality project delivery"],
                location="city_hall",
                reputation=85
            ),
            AgentModel(
                id="agent_dev_01",
                name="Ari",
                role="developer",
                personality=PersonalityModel(conscientiousness=0.8, openness=0.9, social=0.4),
                goals=["Write clean Python code", "Fix all QA findings"],
                skills=["python", "debugging"],
                location="office_01",
                reputation=75
            ),
            AgentModel(
                id="agent_reviewer_01",
                name="Bima",
                role="reviewer",
                personality=PersonalityModel(conscientiousness=0.95, risk_tolerance=0.2),
                goals=["Maintain high software quality standards", "Verify test coverage"],
                skills=["testing", "peer_review"],
                location="qa_lab",
                reputation=90
            ),
            AgentModel(
                id="agent_research_01",
                name="Deni",
                role="researcher",
                personality=PersonalityModel(openness=0.95, social=0.5),
                goals=["Discover cutting-edge libraries", "Analyze architecture patterns"],
                skills=["web_research", "architecture"],
                location="library",
                reputation=80
            ),
            AgentModel(
                id="agent_mentor_01",
                name="Eka",
                role="skill_mentor",
                personality=PersonalityModel(social=0.9, openness=0.85, conscientiousness=0.8),
                goals=["Train agents in new capabilities", "Maintain certified skill catalog"],
                skills=["pedagogy", "skill_testing"],
                location="academy",
                reputation=88
            )
        ]

        conn = get_connection()
        cursor = conn.cursor()

        for a in default_agents:
            cursor.execute("""
                INSERT OR IGNORE INTO agents (
                    id, name, role, age, personality_json, needs_json, goals_json, 
                    skills_json, location, money, reputation, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'IDLE', datetime('now'), datetime('now'))
            """, (
                a.id, a.name, a.role, a.age,
                json.dumps(a.personality.model_dump()),
                json.dumps(a.needs.model_dump()),
                json.dumps(a.goals),
                json.dumps(a.skills),
                a.location, a.money, a.reputation
            ))

        conn.commit()
        conn.close()

    def get_agent_instance(self, agent_id: str) -> Optional[BaseAgent]:
        if agent_id in self._instances:
            return self._instances[agent_id]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE id = ?", (agent_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        agent_data = AgentModel(
            id=row["id"],
            name=row["name"],
            role=row["role"],
            age=row["age"],
            personality=PersonalityModel(**json.loads(row["personality_json"])),
            needs=NeedsModel(**json.loads(row["needs_json"])),
            goals=json.loads(row["goals_json"] or "[]"),
            skills=json.loads(row["skills_json"] or "[]"),
            location=row["location"],
            money=row["money"],
            reputation=row["reputation"],
            status=row["status"],
            created_at=row["created_at"],
            updated_at=row["updated_at"]
        )

        role = agent_data.role.lower()
        if role == "manager":
            instance = ManagerAgent(agent_data)
        elif role == "developer":
            instance = DeveloperAgent(agent_data)
        elif role == "reviewer":
            instance = ReviewerAgent(agent_data)
        elif role == "researcher":
            instance = ResearcherAgent(agent_data)
        elif role == "skill_mentor":
            instance = SkillMentorAgent(agent_data)
        else:
            instance = BaseAgent(agent_data)

        self._instances[agent_id] = instance
        return instance

    def get_all_agents(self) -> List[AgentModel]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM agents ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()

        agents = []
        for row in rows:
            agents.append(AgentModel(
                id=row["id"],
                name=row["name"],
                role=row["role"],
                age=row["age"],
                personality=PersonalityModel(**json.loads(row["personality_json"])),
                needs=NeedsModel(**json.loads(row["needs_json"])),
                goals=json.loads(row["goals_json"] or "[]"),
                skills=json.loads(row["skills_json"] or "[]"),
                location=row["location"],
                money=row["money"],
                reputation=row["reputation"],
                status=row["status"],
                created_at=row["created_at"],
                updated_at=row["updated_at"]
            ))
        return agents

agent_registry = AgentRegistry()
