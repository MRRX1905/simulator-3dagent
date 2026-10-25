import asyncio
import shlex
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from app.config import settings

class CommandRunner:
    """
    Subprocess execution gateway with allowlist enforcement and boundary checks.
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        self.workspace_root = Path(workspace_root or settings.WORKSPACE_PATH).resolve()

    def validate_command(self, command: str) -> str:
        command_clean = command.strip()
        if not command_clean:
            raise ValueError("Empty command cannot be executed.")

        # Split into tokens
        tokens = shlex.split(command_clean, posix=False)
        base_cmd = Path(tokens[0]).name.lower().replace(".exe", "")

        # Check blocked commands
        for blocked in settings.BLOCKED_COMMANDS:
            if blocked in command_clean.lower():
                raise PermissionError(f"Security Violation: Command contains blocked keyword '{blocked}'")

        # Check allowed commands
        if base_cmd not in settings.ALLOWED_COMMANDS:
            raise PermissionError(
                f"Security Violation: Command '{base_cmd}' is not in the allowed commands list: {sorted(list(settings.ALLOWED_COMMANDS))}"
            )

        return command_clean

    async def run(
        self,
        command: str,
        cwd_relative: str = ".",
        timeout_seconds: float = 15.0,
        max_output_bytes: int = 32768
    ) -> Dict[str, Any]:
        valid_cmd = self.validate_command(command)
        
        # Verify execution directory is strictly inside workspace
        target_cwd = (self.workspace_root / cwd_relative.lstrip("/\\")).resolve()
        try:
            target_cwd.relative_to(self.workspace_root)
        except ValueError:
            raise PermissionError(f"CWD '{cwd_relative}' escapes workspace root '{self.workspace_root}'")

        if not target_cwd.exists():
            target_cwd.mkdir(parents=True, exist_ok=True)

        try:
            process = await asyncio.create_subprocess_shell(
                valid_cmd,
                cwd=str(target_cwd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout_seconds
            )

            stdout = stdout_bytes[:max_output_bytes].decode("utf-8", errors="replace")
            stderr = stderr_bytes[:max_output_bytes].decode("utf-8", errors="replace")

            return {
                "command": valid_cmd,
                "exit_code": process.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "success": process.returncode == 0
            }

        except asyncio.TimeoutError:
            try:
                process.kill()
            except Exception:
                pass
            return {
                "command": valid_cmd,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout_seconds} seconds.",
                "success": False
            }
        except Exception as e:
            return {
                "command": valid_cmd,
                "exit_code": -1,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }
