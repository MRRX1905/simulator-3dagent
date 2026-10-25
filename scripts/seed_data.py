import json
from pathlib import Path
from app.config import settings
from app.database import init_db
from app.agents.registry import agent_registry
from app.skills.registry import skill_registry
from app.models import SkillModel

def run_seed():
    init_db()
    agent_registry.seed_default_agents()

    # Load JSON skills into DB
    for skill_file in settings.SKILLS_DIR.glob("*.json"):
        try:
            data = json.loads(skill_file.read_text(encoding="utf-8"))
            skill = SkillModel(**data)
            skill_registry.register_skill(skill)
            print(f"Registered skill: {skill.name}")
        except Exception as e:
            print(f"Error loading {skill_file}: {e}")

    # Assign initial skills
    skill_registry.assign_skill_to_agent("agent_dev_01", "skill_python_basics", level=3, validated=True)
    skill_registry.assign_skill_to_agent("agent_dev_01", "skill_testing_pytest", level=2, validated=True)

    skill_registry.assign_skill_to_agent("agent_reviewer_01", "skill_peer_review", level=4, validated=True)
    skill_registry.assign_skill_to_agent("agent_reviewer_01", "skill_testing_pytest", level=4, validated=True)

    skill_registry.assign_skill_to_agent("agent_mentor_01", "skill_python_basics", level=5, validated=True)
    skill_registry.assign_skill_to_agent("agent_mentor_01", "skill_peer_review", level=5, validated=True)
    skill_registry.assign_skill_to_agent("agent_mentor_01", "skill_testing_pytest", level=5, validated=True)

    print("Initial seeding completed successfully.")

if __name__ == "__main__":
    run_seed()
