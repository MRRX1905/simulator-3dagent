import pytest
from app.skills.registry import skill_registry
from app.skills.capability_detector import capability_detector
from app.models import SkillModel

def test_skill_registration_and_agent_assignment():
    skill = SkillModel(
        id="skill_docker_basics",
        name="Docker Containerization",
        category="devops",
        level=2,
        description="Build and run docker containers",
        procedures=["Write Dockerfile", "Build image"],
        tests=["Container runs properly"],
        validated=True,
        confidence=0.9
    )
    skill_registry.register_skill(skill)
    
    retrieved = skill_registry.get_skill("skill_docker_basics")
    assert retrieved is not None
    assert retrieved.name == "Docker Containerization"

    # Assign to agent
    skill_registry.assign_skill_to_agent("agent_dev_01", "skill_docker_basics", level=2, validated=True)
    agent_skills = skill_registry.get_agent_skills("agent_dev_01")
    assert any(s["skill_id"] == "skill_docker_basics" for s in agent_skills)

def test_capability_gap_and_mentor_matching():
    # Check gap for an unlearned skill
    gap_result = capability_detector.check_agent_capability(
        agent_id="agent_dev_01",
        required_skills=["skill_quantum_computing"],
        min_level=2
    )
    assert gap_result["has_gap"] is True
    assert "skill_quantum_computing" in gap_result["missing_skills"]

    # Mentor matching for python basics (Eka is level 5 mentor)
    mentors = capability_detector.find_mentors_for_skill("skill_python_basics", min_mentor_level=3)
    assert len(mentors) > 0
    assert any(m["name"] == "Eka" for m in mentors)
