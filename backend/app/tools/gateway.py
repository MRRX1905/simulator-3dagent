import uuid
from typing import Dict, Any, Optional
from app.tools.workspace_fs import WorkspaceFileSystem
from app.tools.command_runner import CommandRunner
from app.models import ApprovalModel
from app.database import get_connection
import json

class ToolGateway:
    """
    Central dispatcher for all agent tool executions.
    Enforces Zones A, B, C, D.
    """

    def __init__(self):
        self.fs = WorkspaceFileSystem()
        self.cmd = CommandRunner()

    async def execute_tool(
        self,
        agent_id: str,
        tool_name: str,
        args: Dict[str, Any],
        task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        
        # Zone A (Safe / Auto-approved)
        if tool_name == "fs.write_file":
            path = args.get("path")
            content = args.get("content", "")
            saved_path = self.fs.write_file(path, content)
            return {"status": "success", "saved_path": saved_path}

        elif tool_name == "fs.read_file":
            path = args.get("path")
            content = self.fs.read_file(path)
            return {"status": "success", "content": content}

        elif tool_name == "fs.list_files":
            path = args.get("path", ".")
            files = self.fs.list_files(path)
            return {"status": "success", "files": files}

        elif tool_name == "terminal.run":
            command = args.get("command")
            cwd = args.get("cwd", ".")
            result = await self.cmd.run(command, cwd_relative=cwd)
            return {"status": "success", "result": result}

        # Zone C / D (Requires Human Approval)
        elif tool_name in ("fs.quarantine", "git.push", "cloud.upload", "system.destructive"):
            approval_id = f"appr_{uuid.uuid4().hex[:8]}"
            zone = "C" if tool_name in ("git.push", "cloud.upload") else "D"
            
            # Save into DB approval queue
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO approvals (id, task_id, agent_id, zone, action, details_json, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'PENDING', datetime('now'))
            """, (approval_id, task_id, agent_id, zone, tool_name, json.dumps(args)))
            conn.commit()
            conn.close()

            return {
                "status": "pending_approval",
                "approval_id": approval_id,
                "zone": zone,
                "message": f"Action '{tool_name}' requires human approval (Zone {zone})."
            }

        else:
            raise ValueError(f"Unknown tool '{tool_name}' requested by agent {agent_id}.")

tool_gateway = ToolGateway()
