from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from app.models import SkillModel
from app.skills.registry import skill_registry

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.get("", response_model=List[SkillModel])
async def list_skills():
    return skill_registry.list_skills()

@router.get("/{skill_id}", response_model=SkillModel)
async def get_skill(skill_id: str):
    skill = skill_registry.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@router.post("/propose", response_model=SkillModel)
async def propose_skill(skill: SkillModel):
    # Registered initially as candidate (validated=False)
    skill.validated = False
    return skill_registry.register_skill(skill)
