from typing import List, Dict, Any, Optional
from app.skills.registry import skill_registry
from app.database import get_connection

class CapabilityDetector:
    """
    Detects capability gaps between tasks and agents,
    and pairs learners with qualified mentors (Level >= 3).
    """

    def check_agent_capability(self, agent_id: str, required_skills: List[str], min_level: int = 2) -> Dict[str, Any]:
        agent_skills = {s["skill_id"]: s for s in skill_registry.get_agent_skills(agent_id)}
        
        missing_skills = []
        underlevel_skills = []

        for req in required_skills:
            if req not in agent_skills:
                missing_skills.append(req)
            elif agent_skills[req]["level"] < min_level:
                underlevel_skills.append({
                    "skill_id": req,
                    "current_level": agent_skills[req]["level"],
                    "required_level": min_level
                })

        has_gap = len(missing_skills) > 0 or len(underlevel_skills) > 0
        return {
            "has_gap": has_gap,
            "missing_skills": missing_skills,
            "underlevel_skills": underlevel_skills,
            "can_execute": not has_gap
        }

    def find_mentors_for_skill(self, skill_id: str, min_mentor_level: int = 3) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.id, a.name, a.role, a.reputation, ask.level as skill_level
            FROM agent_skills ask
            JOIN agents a ON ask.agent_id = a.id
            WHERE ask.skill_id = ? AND ask.level >= ? AND ask.validated = 1
            ORDER BY ask.level DESC, a.reputation DESC
        """, (skill_id, min_mentor_level))

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "agent_id": r["id"],
                "name": r["name"],
                "role": r["role"],
                "reputation": r["reputation"],
                "skill_level": r["skill_level"]
            }
            for r in rows
        ]

capability_detector = CapabilityDetector()
