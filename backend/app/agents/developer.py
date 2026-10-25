import json
import uuid
from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.models import TaskModel, ArtifactModel
from app.core.state_machine import AgentState
from app.tools.gateway import tool_gateway
from app.peer_review.protocol import ReviewRequest
from app.peer_review.engine import peer_review_engine
from app.llm.factory import get_llm_provider
from app.database import get_connection

class DeveloperAgent(BaseAgent):
    """
    Ari - Developer Agent
    Solves development tasks, writes files to workspace sandbox, runs tests,
    and iterates with QA/Reviewer agents through peer review.
    """

    async def execute_task(self, task: TaskModel) -> Dict[str, Any]:
        self.set_status(AgentState.PLANNING)
        self.record_thought(f"Planning implementation for '{task.title}'")

        # Step 1: Generate initial code
        self.set_status(AgentState.EXECUTING)
        llm = get_llm_provider()
        prompt = (
            f"Write a Python module to solve: {task.goal}.\n"
            f"Subject: {task.goal}\n"
            f"Include clean docstrings, robust error handling, and runnable main demonstration."
        )
        raw_code = await llm.generate(prompt=prompt, system_prompt="You are an expert Python Developer in AI City. Return ONLY valid runnable Python code without markdown codeblocks or conversational text.", max_tokens=600)
        
        # Strip markdown fences if present from real LLMs
        def extract_clean_code(content: str) -> str:
            content = content.strip()
            if "```python" in content:
                parts = content.split("```python", 1)[1].split("```", 1)
                return parts[0].strip()
            elif "```" in content:
                parts = content.split("```", 1)[1].split("```", 1)
                return parts[0].strip()
            return content

        code_content = extract_clean_code(raw_code)

        # Step 2: Write to workspace sandbox with descriptive name
        slug = "".join([c if c.isalnum() else "_" for c in task.goal.lower()]).strip("_")[:20]
        if not slug:
            slug = f"solution_{task.id[:8]}"
        file_name = f"{slug}.py"
        await tool_gateway.execute_tool(
            agent_id=self.id,
            tool_name="fs.write_file",
            args={"path": file_name, "content": code_content},
            task_id=task.id
        )

        artifact_id = f"art_{uuid.uuid4().hex[:8]}"
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM tasks WHERE id = ?", (task.id,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT OR IGNORE INTO tasks (id, title, goal, created_by, assigned_to, status, priority, risk, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, 'RUNNING', ?, ?, datetime('now'), datetime('now'))
                """, (task.id, task.title, task.goal, task.created_by, self.id, task.priority, task.risk))
            cursor.execute("""
                INSERT INTO artifacts (id, task_id, author_agent, path, type, created_at)
                VALUES (?, ?, ?, ?, 'py', datetime('now'))
            """, (artifact_id, task.id, self.id, file_name))
            conn.commit()
        finally:
            conn.close()

        # Step 3: Check if task involves building the city or recruiting agents
        goal_lower = task.goal.lower()
        new_building_info = None
        construction_keywords = [
            "bangun", "rumah", "kantor", "gedung", "ekspansi", "tambah agent", 
            "rekrut", "perluas", "arsitek", "penduduk", "warga", "tambah warga", 
            "tambah orang", "pekerja", "ruko", "fasilitas"
        ]
        if any(k in goal_lower for k in construction_keywords):
            from app.world.city_builder import city_builder
            b_type = "office" if any(w in goal_lower for w in ["kantor", "office", "gedung", "tower", "lab"]) else "house"
            new_building_info = city_builder.construct_building(building_type=b_type, owner_agent_id=self.id)

        # Step 4: Execute code for REAL in the sandbox terminal
        execution = await tool_gateway.execute_tool(
            agent_id=self.id,
            tool_name="terminal.run",
            args={"command": f"python {file_name}"},
            task_id=task.id
        )
        term_res = execution.get("result", {})
        stdout = term_res.get("stdout", "")
        stderr = term_res.get("stderr", "")

        # Step 5: Peer Review Cycle with real execution evidence
        self.set_status(AgentState.REVIEWING)
        review_request = ReviewRequest(
            artifact_id=artifact_id,
            task_id=task.id,
            author_agent=self.id,
            artifact_path=file_name,
            criteria=["correctness", "input validation", "error handling"],
            context=f"Goal: {task.goal}. Real Terminal Execution:\nSTDOUT:\n{stdout}\nSTDERR:\n{stderr}"
        )

        review_result = await peer_review_engine.conduct_review(
            request=review_request,
            reviewer_agent_id="agent_reviewer_01"
        )

        # Step 6: Iterative Revision Loop if review asks for revision
        iterations = 1
        if review_result.status == "needs_revision":
            self.record_thought(f"Peer review indicated revision needed: {review_result.findings}")
            self.set_status(AgentState.EXECUTING)
            
            # Incorporate reviewer's findings into revision
            fix_recommendations = "; ".join([f.recommendation for f in review_result.findings])
            revised_prompt = (
                f"Revise the following Python code based on peer review findings:\n"
                f"Findings: {fix_recommendations}\n\n"
                f"Original Code:\n{code_content}\n\n"
                f"Return the complete improved code with input validation and error handling."
            )
            revised_code = await llm.generate(prompt=revised_prompt, system_prompt="You are an expert Python Developer fixing QA issues.")

            # Overwrite workspace file
            await tool_gateway.execute_tool(
                agent_id=self.id,
                tool_name="fs.write_file",
                args={"path": file_name, "content": revised_code},
                task_id=task.id
            )

            # Re-review
            self.set_status(AgentState.REVIEWING)
            review_result = await peer_review_engine.conduct_review(
                request=review_request,
                reviewer_agent_id="agent_reviewer_01"
            )
            iterations += 1

        self.set_status(AgentState.DONE)
        self.set_status(AgentState.IDLE)

        final_code = revised_code if iterations > 1 else code_content
        return {
            "status": "completed",
            "artifact_id": artifact_id,
            "artifact_path": file_name,
            "review_status": review_result.status,
            "review_score": review_result.score,
            "iterations": iterations,
            "code": final_code,
            "stdout": stdout,
            "stderr": stderr,
            "new_building": new_building_info
        }
