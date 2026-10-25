import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config import settings

class WorkspaceFileSystem:
    """
    Sandboxed file manager for agents.
    Agents can ONLY access files within settings.WORKSPACE_PATH.
    Any attempt to escape the workspace raises a PermissionError.
    """

    def __init__(self, workspace_root: Optional[Path] = None):
        self.root = Path(workspace_root or settings.WORKSPACE_PATH).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve_safe_path(self, relative_path: str) -> Path:
        """
        Resolves path and enforces sandbox jail boundary.
        """
        # Clean leading slashes
        clean_rel = relative_path.lstrip("/\\")
        target_path = (self.root / clean_rel).resolve()
        
        # Check boundary
        try:
            target_path.relative_to(self.root)
        except ValueError:
            raise PermissionError(
                f"Security Violation: Path '{relative_path}' escapes workspace boundary '{self.root}'"
            )
        return target_path

    def write_file(self, relative_path: str, content: str) -> str:
        target = self._resolve_safe_path(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return str(target.relative_to(self.root))

    def read_file(self, relative_path: str) -> str:
        target = self._resolve_safe_path(relative_path)
        if not target.exists():
            raise FileNotFoundError(f"File '{relative_path}' not found in workspace.")
        if not target.is_file():
            raise ValueError(f"Path '{relative_path}' is not a file.")
        return target.read_text(encoding="utf-8")

    def list_files(self, relative_path: str = ".") -> List[Dict[str, Any]]:
        target = self._resolve_safe_path(relative_path)
        if not target.exists():
            return []
        
        results = []
        for item in target.iterdir():
            results.append({
                "name": item.name,
                "is_dir": item.is_dir(),
                "size": item.stat().st_size if item.is_file() else 0,
                "relative_path": str(item.relative_to(self.root)).replace("\\", "/")
            })
        return results

    def exists(self, relative_path: str) -> bool:
        try:
            target = self._resolve_safe_path(relative_path)
            return target.exists()
        except PermissionError:
            return False

    def quarantine_file(self, relative_path: str) -> str:
        """Safe alternative to direct file deletion (quarantine/trash)."""
        target = self._resolve_safe_path(relative_path)
        if not target.exists():
            raise FileNotFoundError(f"File '{relative_path}' not found.")
        trash_dir = self.root / ".trash"
        trash_dir.mkdir(parents=True, exist_ok=True)
        trash_target = trash_dir / target.name
        target.rename(trash_target)
        return str(trash_target.relative_to(self.root))
