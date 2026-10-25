import json
from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.models import TaskModel
from app.core.state_machine import AgentState
from app.llm.factory import get_llm_provider
from app.memory.memory_store import memory_store

class ResearcherAgent(BaseAgent):
    """
    Deni - Research Agent
    Gathers architectural knowledge, extracts repository patterns,
    and documents findings into semantic memory.
    """

    async def execute_task(self, task: TaskModel) -> Dict[str, Any]:
        self.set_status(AgentState.PLANNING)
        self.record_thought(f"Starting research on topic: {task.goal}")

        self.set_status(AgentState.EXECUTING)
        prompt = (
            f"You are Research Agent {self.name} in AI City.\n"
            f"Research topic: {task.goal}.\n"
            f"Provide structured analysis: (1) Core concepts, (2) Recommended patterns, (3) Potential pitfalls."
        )

        llm = get_llm_provider()
        findings = await llm.generate(prompt=prompt, system_prompt="You are a precise technical researcher in AI City.")

        # Store in semantic memory
        memory_store.record_memory(
            agent_id=self.id,
            mem_type="semantic",
            content=f"Research on '{task.goal}':\n{findings[:300]}...",
            importance=0.8,
            source="research_task"
        )

        self.set_status(AgentState.DONE)
        self.set_status(AgentState.IDLE)

        return {
            "status": "researched",
            "researcher": self.id,
            "findings_summary": findings[:200]
        }
