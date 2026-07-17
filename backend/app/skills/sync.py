"""Sync agent skills from skills/ into the skill registry table."""

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Skill as SkillRow
from app.skills.loader import load_skills

VERSION = "1.0"


def sync_skills(session: Session) -> list[SkillRow]:
    """Upsert all loaded skills into the skill table."""
    loaded = load_skills(Path(get_settings().skills_dir))
    db_skills: list[SkillRow] = []
    for skill in loaded:
        existing = session.execute(
            select(SkillRow).where(SkillRow.name == skill.name),
        ).scalar_one_or_none()
        if existing:
            existing.version = VERSION
            existing.loop_stage = skill.loop_stage
            db_skills.append(existing)
        else:
            db_skill = SkillRow(
                name=skill.name,
                version=VERSION,
                loop_stage=skill.loop_stage,
            )
            session.add(db_skill)
            db_skills.append(db_skill)
    session.commit()
    return db_skills
