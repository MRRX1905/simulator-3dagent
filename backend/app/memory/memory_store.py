import uuid
import sqlite3
from typing import List, Dict, Any, Optional
from app.database import get_connection
from app.models import MemoryModel

class MemoryStore:
    """
    Manages episodic, semantic, and procedural memory for agents in SQLite.
    """

    def record_memory(
        self,
        agent_id: str,
        mem_type: str,
        content: str,
        importance: float = 0.5,
        source: Optional[str] = None
    ) -> MemoryModel:
        mem_id = f"mem_{uuid.uuid4().hex[:8]}"
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO memories (id, agent_id, type, content, importance, source, created_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (mem_id, agent_id, mem_type, content, importance, source))
        
        conn.commit()
        conn.close()

        return MemoryModel(
            id=mem_id,
            agent_id=agent_id,
            type=mem_type,
            content=content,
            importance=importance,
            source=source
        )

    def get_memories_for_agent(
        self,
        agent_id: str,
        mem_type: Optional[str] = None,
        limit: int = 10
    ) -> List[MemoryModel]:
        conn = get_connection()
        cursor = conn.cursor()
        
        if mem_type:
            cursor.execute("""
                SELECT * FROM memories 
                WHERE agent_id = ? AND type = ? 
                ORDER BY created_at DESC LIMIT ?
            """, (agent_id, mem_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM memories 
                WHERE agent_id = ? 
                ORDER BY created_at DESC LIMIT ?
            """, (agent_id, limit))

        rows = cursor.fetchall()
        conn.close()

        memories = []
        for r in rows:
            memories.append(MemoryModel(
                id=r["id"],
                agent_id=r["agent_id"],
                type=r["type"],
                content=r["content"],
                importance=r["importance"],
                source=r["source"],
                created_at=r["created_at"]
            ))
        return memories

    def search_memories(self, agent_id: str, query: str, limit: int = 5) -> List[MemoryModel]:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Simple substring search in SQLite
        cursor.execute("""
            SELECT * FROM memories 
            WHERE agent_id = ? AND content LIKE ?
            ORDER BY importance DESC, created_at DESC LIMIT ?
        """, (agent_id, f"%{query}%", limit))

        rows = cursor.fetchall()
        conn.close()

        return [
            MemoryModel(
                id=r["id"],
                agent_id=r["agent_id"],
                type=r["type"],
                content=r["content"],
                importance=r["importance"],
                source=r["source"],
                created_at=r["created_at"]
            )
            for r in rows
        ]

memory_store = MemoryStore()
