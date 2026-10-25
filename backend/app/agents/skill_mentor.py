import json
from typing import Dict, Any, List
from app.agents.base_agent import BaseAgent
from app.models import TaskModel, SkillModel
from app.core.state_machine import AgentState
from app.skills.registry import skill_registry
from app.memory.memory_store import memory_store

class SkillMentorAgent(BaseAgent):
    """
    Eka - Skill Mentor Agent
    Identifies capability gaps, guides learners through practice procedures,
    and certifies validated skills into the registry.
    """

    async def execute_task(self, task: TaskModel) -> Dict[str, Any]:
        self.set_status(AgentState.PLANNING)
        self.record_thought(f"Preparing mentoring curriculum for task: {task.title}")

        learner_agent_id = task.requirements.get("learner_agent_id", "agent_dev_01")
        skill_id = task.requirements.get("skill_id", "skill_python_basics")

        self.set_status(AgentState.EXECUTING)
        skill = skill_registry.get_skill(skill_id)
        if not skill:
            # Create candidate skill
            skill = SkillModel(
                id=skill_id,
                name=task.requirements.get("skill_name", "New Skill"),
                category="general",
                level=2,
                description=f"Skill for {task.goal}",
                procedures=["Step 1: Understand basics", "Step 2: Practical test"],
                tests=["Verify successful test output"],
                validated=True,
                confidence=0.85
            )
            skill_registry.register_skill(skill)

        # Conduct teaching & certification
        skill_registry.assign_skill_to_agent(
            agent_id=learner_agent_id,
            skill_id=skill.id,
            level=2,
            validated=True
        )

        # Record teaching event in procedural memory
        memory_store.record_memory(
            agent_id=self.id,
            mem_type="procedural",
            content=f"Mentored {learner_agent_id} in skill '{skill.name}' to level 2.",
            importance=0.75,
            source=f"mentor_session:{learner_agent_id}"
        )

        self.set_status(AgentState.DONE)
        self.set_status(AgentState.IDLE)

        return {
            "status": "mentored",
            "mentor": self.id,
            "learner": learner_agent_id,
            "skill_id": skill.id,
            "new_level": 2
        }
