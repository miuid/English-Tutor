"""Tests for InteractionLog persistence in the daily loop."""

import pytest
from sqlalchemy import select

from app.models import InteractionLog
from app.sessions.interactive import InteractiveLoop
from app.skills.executor import SkillExecutionService
from app.skills.loader import load_skills
from app.skills.sync import sync_skills
from tests.test_llm import FakeProvider


def _load_skills():
    from pathlib import Path

    from app.config import get_settings
    return {skill.name: skill for skill in load_skills(Path(get_settings().skills_dir))}


@pytest.fixture
def skills():
    """Load the real skill packages."""
    return _load_skills()


@pytest.fixture
def loop(db_session, skills):
    """An InteractiveLoop wired to a FakeProvider with skills synced to DB."""
    sync_skills(db_session)
    provider = FakeProvider()
    executor = SkillExecutionService(provider=provider, model_name="fake-model")
    return InteractiveLoop(db=db_session, executor=executor, skills=skills)


@pytest.mark.asyncio
async def test_start_creates_one_interaction_log(loop, db_session):
    """Starting a session runs one skill and writes one InteractionLog."""
    session = await loop.start(task_prompt="Test prompt", year_level="8", text_type="analytical")

    logs = db_session.execute(
        select(InteractionLog).where(InteractionLog.session_id == session.id)
    ).scalars().all()

    assert len(logs) == 1
    log = logs[0]
    assert log.model == "fake-model"
    assert log.skill is not None
    assert log.skill.name == "set-success-criteria"
    assert log.output == "fake response"


@pytest.mark.asyncio
async def test_advance_creates_interaction_log(loop, db_session):
    """Advancing a stage runs a skill and writes an InteractionLog."""
    session = await loop.start(task_prompt="Test prompt", year_level="8", text_type="analytical")
    db_session.commit()

    await loop.advance(session.id)

    logs = db_session.execute(
        select(InteractionLog).where(InteractionLog.session_id == session.id)
    ).scalars().all()

    # start (set-success-criteria) + advance (model-response) = 2 logs
    assert len(logs) == 2
    log_names = {log.skill.name for log in logs}
    assert log_names == {"set-success-criteria", "model-response"}
