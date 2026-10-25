import uuid
import json
import random
from typing import Dict, Any, List, Optional
from app.database import get_connection
from app.models import BuildingModel, AgentModel, PersonalityModel, NeedsModel
from app.agents.registry import agent_registry

# Available roles for newly recruited citizens
NEW_ROLES = [
    ("architect", "Arsitek Perencana Tata Kota"),
    ("constructor", "Mandor Konstruksi Bangunan"),
    ("data_analyst", "Analis Data & Ekonomi"),
    ("designer", "Desainer Grafis & UI/UX"),
    ("security_agent", "Pengawas Keamanan & Safety")
]

NAMES = ["Fajar", "Gita", "Hadi", "Indah", "Joko", "Kartika", "Lestari", "Maulana", "Nadia", "Oki"]

class CityBuilder:
    """
    Handles physical city expansion, constructing new buildings,
    and recruiting new agents into the population.
    """

    def get_building_count(self) -> int:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM buildings")
        cnt = cursor.fetchone()["cnt"]
        conn.close()
        return cnt

    def construct_building(self, building_type: str = "house", owner_agent_id: Optional[str] = None) -> Dict[str, Any]:
        count = self.get_building_count()
        building_id = f"bld_{uuid.uuid4().hex[:8]}"

        # Calculate position based on grid
        if building_type == "house":
            row = (count // 4)
            col = (count % 4)
            x = -12 + (col * 8)
            z = 24 + (row * 8)
        else:
            x = 26 if (count % 2 == 0) else -26
            z = 10 + (count * 6)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO buildings (id, type, owner_agent_id, x, y, z, condition, value)
            VALUES (?, ?, ?, ?, 0.0, ?, 1.0, 15000.0)
        """, (building_id, building_type, owner_agent_id, x, z))

        # Record world construction event
        cursor.execute("""
            INSERT INTO world_events (id, type, severity, payload_json, created_at)
            VALUES (?, 'construction', 'info', ?, datetime('now'))
        """, (f"evt_{uuid.uuid4().hex[:8]}", json.dumps({
            "action": "build",
            "building_id": building_id,
            "type": building_type,
            "position": {"x": x, "y": 0, "z": z}
        })))
        conn.commit()
        conn.close()

        # Automatically recruit a new citizen to inhabit the new building!
        new_agent = self.recruit_new_citizen(home_building_id=building_id)

        return {
            "building_id": building_id,
            "type": building_type,
            "position": {"x": x, "y": 0, "z": z},
            "new_agent": new_agent
        }

    def recruit_new_citizen(self, home_building_id: Optional[str] = None) -> Dict[str, Any]:
        all_agents = agent_registry.get_all_agents()
        agent_idx = len(all_agents) + 1
        agent_id = f"agent_{agent_idx:03d}"

        role_tuple = random.choice(NEW_ROLES)
        name = random.choice(NAMES) + f" #{agent_idx}"

        new_agent_data = AgentModel(
            id=agent_id,
            name=name,
            role=role_tuple[0],
            age=random.randint(22, 38),
            personality=PersonalityModel(
                openness=round(random.uniform(0.6, 0.95), 2),
                conscientiousness=round(random.uniform(0.7, 0.95), 2),
                social=round(random.uniform(0.5, 0.9), 2)
            ),
            needs=NeedsModel(food=1.0, energy=1.0, money=1.0, social=1.0),
            goals=[f"Bekerja sebagai {role_tuple[1]}", "Membantu pembangunan kota AI"],
            location=home_building_id or "residential",
            money=1200.0,
            reputation=60,
            status="IDLE"
        )

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO agents (
                id, name, role, age, personality_json, needs_json, goals_json, 
                skills_json, location, money, reputation, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, '[]', ?, ?, ?, 'IDLE', datetime('now'), datetime('now'))
        """, (
            new_agent_data.id, new_agent_data.name, new_agent_data.role, new_agent_data.age,
            json.dumps(new_agent_data.personality.model_dump()),
            json.dumps(new_agent_data.needs.model_dump()),
            json.dumps(new_agent_data.goals),
            new_agent_data.location, new_agent_data.money, new_agent_data.reputation
        ))

        cursor.execute("""
            INSERT INTO world_events (id, type, severity, payload_json, created_at)
            VALUES (?, 'recruitment', 'info', ?, datetime('now'))
        """, (f"evt_{uuid.uuid4().hex[:8]}", json.dumps({
            "action": "new_agent_recruited",
            "agent_id": new_agent_data.id,
            "name": new_agent_data.name,
            "role": new_agent_data.role
        })))

        conn.commit()
        conn.close()

        return new_agent_data.model_dump()

city_builder = CityBuilder()
