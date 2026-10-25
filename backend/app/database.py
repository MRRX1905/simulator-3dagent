import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config import settings

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.DATABASE_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout = 30000;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS agents (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        age INTEGER DEFAULT 25,
        personality_json TEXT NOT NULL,
        needs_json TEXT NOT NULL,
        goals_json TEXT NOT NULL,
        skills_json TEXT NOT NULL,
        location TEXT DEFAULT 'plaza',
        money REAL DEFAULT 1000.0,
        reputation INTEGER DEFAULT 50,
        memory_refs_json TEXT DEFAULT '[]',
        relationships_json TEXT DEFAULT '{}',
        status TEXT DEFAULT 'IDLE',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS memories (
        id TEXT PRIMARY KEY,
        agent_id TEXT NOT NULL,
        type TEXT NOT NULL,
        content TEXT NOT NULL,
        importance REAL DEFAULT 0.5,
        source TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS skills (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        level INTEGER DEFAULT 1,
        description TEXT NOT NULL,
        prerequisites_json TEXT DEFAULT '[]',
        procedures_json TEXT DEFAULT '[]',
        tests_json TEXT DEFAULT '[]',
        sources_json TEXT DEFAULT '[]',
        validated INTEGER DEFAULT 0,
        confidence REAL DEFAULT 0.5,
        version INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS agent_skills (
        agent_id TEXT NOT NULL,
        skill_id TEXT NOT NULL,
        level INTEGER DEFAULT 1,
        validated INTEGER DEFAULT 0,
        last_tested TEXT,
        PRIMARY KEY (agent_id, skill_id),
        FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE,
        FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        goal TEXT NOT NULL,
        created_by TEXT NOT NULL,
        assigned_to TEXT,
        status TEXT DEFAULT 'PENDING',
        priority REAL DEFAULT 0.5,
        risk TEXT DEFAULT 'low',
        requirements_json TEXT DEFAULT '{}',
        result_json TEXT,
        blockers_json TEXT DEFAULT '[]',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        from_agent TEXT NOT NULL,
        to_agent TEXT NOT NULL,
        type TEXT NOT NULL,
        subject TEXT NOT NULL,
        payload_json TEXT DEFAULT '{}',
        requires_response INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS artifacts (
        id TEXT PRIMARY KEY,
        task_id TEXT NOT NULL,
        author_agent TEXT NOT NULL,
        path TEXT NOT NULL,
        type TEXT NOT NULL,
        hash TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS buildings (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        owner_agent_id TEXT,
        x REAL DEFAULT 0.0,
        y REAL DEFAULT 0.0,
        z REAL DEFAULT 0.0,
        condition REAL DEFAULT 1.0,
        value REAL DEFAULT 10000.0
    );

    CREATE TABLE IF NOT EXISTS world_events (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        severity TEXT DEFAULT 'info',
        payload_json TEXT DEFAULT '{}',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS approvals (
        id TEXT PRIMARY KEY,
        task_id TEXT,
        agent_id TEXT NOT NULL,
        zone TEXT NOT NULL,
        action TEXT NOT NULL,
        details_json TEXT DEFAULT '{}',
        status TEXT DEFAULT 'PENDING',
        reviewed_by TEXT,
        created_at TEXT NOT NULL,
        resolved_at TEXT
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
