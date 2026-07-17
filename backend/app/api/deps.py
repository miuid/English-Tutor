"""FastAPI dependencies: DB session, LLM provider, skills, loop service."""

from collections.abc import Generator
from functools import lru_cache
from pathlib import Path

from fastapi import Depends
from sqlalchemy.orm import Session as DBSession

from app.config import Settings, get_settings
from app.database import get_session_maker
from app.llm.factory import create_llm_provider
from app.llm.provider import LLMProvider
from app.sessions.interactive import InteractiveLoop
from app.skills.executor import SkillExecutionService
from app.skills.loader import Skill, load_skills


def get_db() -> Generator[DBSession, None, None]:
    """Yield one SQLAlchemy session per request."""
    session = get_session_maker()()
    try:
        yield session
    finally:
        session.close()


def get_provider(settings: Settings = Depends(get_settings)) -> LLMProvider:
    """Build the configured LLM provider for this request."""
    return create_llm_provider(settings)


def get_executor(provider: LLMProvider = Depends(get_provider)) -> SkillExecutionService:
    return SkillExecutionService(provider=provider)


@lru_cache
def _load_skills_cached(skills_dir: str) -> dict[str, Skill]:
    return {skill.name: skill for skill in load_skills(Path(skills_dir))}


def get_skills(settings: Settings = Depends(get_settings)) -> dict[str, Skill]:
    """Loaded skill packages, cached per skills_dir (Skill objects are immutable)."""
    return _load_skills_cached(settings.skills_dir)


def get_loop(
    db: DBSession = Depends(get_db),
    executor: SkillExecutionService = Depends(get_executor),
    skills: dict[str, Skill] = Depends(get_skills),
) -> InteractiveLoop:
    return InteractiveLoop(db=db, executor=executor, skills=skills)
