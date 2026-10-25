import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config import settings
from app.database import get_connection
from app.models import SkillModel

class SkillRegistry:
    """
    Central catalog of all validated and candidate skills in AI City.
    """

    def __init__(self):
        self.skills_dir = settings.SKILLS_DIR
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def register_skill(self, skill: SkillModel) -> SkillModel:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO skills (
                id, name, category, level, description, 
                prerequisites_json, procedures_json, tests_json, sources_json, 
                validated, confidence, version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            skill.id, skill.name, skill.category, skill.level, skill.description,
            json.dumps(skill.prerequisites), json.dumps(skill.procedures),
            json.dumps(skill.tests), json.dumps(skill.sources),
            1 if skill.validated else 0, skill.confidence, skill.version
        ))

        conn.commit()
        conn.close()

        # Also save JSON copy to registry directory
        file_path = self.skills_dir / f"{skill.id}.json"
        file_path.write_text(json.dumps(skill.model_dump(), indent=2), encoding="utf-8")
        return skill

    def get_skill(self, skill_id: str) -> Optional[SkillModel]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM skills WHERE id = ?", (skill_id,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return SkillModel(
            id=row["id"],
            name=row["name"],
            category=row["category"],
            level=row["level"],
            description=row["description"],
            prerequisites=json.loads(row["prerequisites_json"] or "[]"),
            procedures=json.loads(row["procedures_json"] or "[]"),
            tests=json.loads(row["tests_json"] or "[]"),
            sources=json.loads(row["sources_json"] or "[]"),
            validated=bool(row["validated"]),
            confidence=row["confidence"],
            version=row["version"]
        )

    def list_skills(self) -> List[SkillModel]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM skills ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()

        skills = []
        for row in rows:
            skills.append(SkillModel(
                id=row["id"],
                name=row["name"],
                category=row["category"],
                level=row["level"],
                description=row["description"],
                prerequisites=json.loads(row["prerequisites_json"] or "[]"),
                procedures=json.loads(row["procedures_json"] or "[]"),
                tests=json.loads(row["tests_json"] or "[]"),
                sources=json.loads(row["sources_json"] or "[]"),
                validated=bool(row["validated"]),
                confidence=row["confidence"],
                version=row["version"]
            ))
        return skills

    def assign_skill_to_agent(self, agent_id: str, skill_id: str, level: int = 1, validated: bool = False):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO agent_skills (agent_id, skill_id, level, validated, last_tested)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (agent_id, skill_id, level, 1 if validated else 0))
        conn.commit()
        conn.close()

    def get_agent_skills(self, agent_id: str) -> List[Dict[str, Any]]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.*, ask.level as agent_level, ask.validated as agent_validated, ask.last_tested
            FROM agent_skills ask
            JOIN skills s ON ask.skill_id = s.id
            WHERE ask.agent_id = ?
        """, (agent_id,))
        rows = cursor.fetchall()
        conn.close()

        result = []
        for r in rows:
            result.append({
                "skill_id": r["id"],
                "name": r["name"],
                "category": r["category"],
                "level": r["agent_level"],
                "validated": bool(r["agent_validated"]),
                "last_tested": r["last_tested"]
            })
        return result

skill_registry = SkillRegistry()
