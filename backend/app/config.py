import os
from pathlib import Path
from typing import List, Set
from pydantic import BaseModel
from dotenv import load_dotenv

# Load .env file
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

class Settings(BaseModel):
    APP_NAME: str = os.getenv("APP_NAME", "AI City Core")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("true", "1", "yes")

    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))

    DATABASE_PATH: Path = Path(os.getenv("DATABASE_PATH", "C:/AI_CITY/backend/data/ai_city.db"))
    WORKSPACE_PATH: Path = Path(os.getenv("WORKSPACE_PATH", "C:/AI_CITY/backend/workspace"))
    SKILLS_DIR: Path = Path(os.getenv("SKILLS_DIR", "C:/AI_CITY/skills/registry"))

    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
    LMSTUDIO_BASE_URL: str = os.getenv("LMSTUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
    LMSTUDIO_MODEL: str = os.getenv("LMSTUDIO_MODEL", "local-model")

    TICK_INTERVAL_SECONDS: float = float(os.getenv("TICK_INTERVAL_SECONDS", "5.0"))
    SIMULATION_SPEED: float = float(os.getenv("SIMULATION_SPEED", "1.0"))
    AUTO_TICK_ENABLED: bool = os.getenv("AUTO_TICK_ENABLED", "true").lower() in ("true", "1", "yes")

    # Command Gateway Allowlist (Commands agents can execute without explicit human approval)
    ALLOWED_COMMANDS: Set[str] = {
        "python",
        "pytest",
        "git",
        "node",
        "npm",
        "echo",
        "dir",
        "ls",
        "cat",
        "type"
    }

    # Commands strictly prohibited (Zone D or system destructive)
    BLOCKED_COMMANDS: Set[str] = {
        "format",
        "shutdown",
        "diskpart",
        "rmdir",
        "del",
        "reg",
        "regedit",
        "powershell -command remove-item",
        "mkfs",
        "dd"
    }

settings = Settings()

# Ensure directories exist
settings.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
settings.WORKSPACE_PATH.mkdir(parents=True, exist_ok=True)
settings.SKILLS_DIR.mkdir(parents=True, exist_ok=True)
