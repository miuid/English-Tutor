"""Tests for InteractionLog persistence in the daily loop."""

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.config import Settings
from app.llm import StageProviderRouter
from app.models import InteractionLog
from app.sessions.interactive import InteractiveLoop
from app.skills.executor import SkillExecutionService
from app.skills.loader import Skill, load_skills
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
async def test_start_creates_interaction_logs(loop, db_session):
    """Starting a session runs the two opening skills and logs both."""
    session = await loop.start(task_prompt="Test prompt", year_level="8", text_type="analytical")

    logs = (
        db_session.execute(
            select(InteractionLog)
            .where(InteractionLog.session_id == session.id)
            .order_by(InteractionLog.created_at)
        )
        .scalars()
        .all()
    )

    assert len(logs) == 2
    assert [log.skill.name for log in logs] == ["spaced-review", "set-success-criteria"]
    for log in logs:
        assert log.model == "fake-model"
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

    # start (spaced-review + set-success-criteria) + advance (model-response)
    assert len(logs) == 3
    log_names = {log.skill.name for log in logs}
    assert log_names == {"spaced-review", "set-success-criteria", "model-response"}


@pytest.mark.asyncio
async def test_interaction_logs_record_the_stage_routed_model(
    db_session: DBSession, skills: dict[str, Skill]
) -> None:
    """With per-stage routing, each log row records the model actually used
    for that skill's loop stage (ISS-021)."""
    sync_skills(db_session)
    settings = Settings(
        llm_provider="fake",
        llm_model="fake-base",
        llm_api_key="",
        llm_stage_models={"retrieval": "fake-light"},
    )
    executor = SkillExecutionService(
        provider=FakeProvider(),
        model_name="fake-base",
        stage_router=StageProviderRouter(settings),
    )
    loop = InteractiveLoop(db=db_session, executor=executor, skills=skills)

    session = await loop.start(
        task_prompt="Test prompt", year_level="8", text_type="analytical"
    )

    logs = (
        db_session.execute(
            select(InteractionLog)
            .where(InteractionLog.session_id == session.id)
            .order_by(InteractionLog.created_at)
        )
        .scalars()
        .all()
    )
    models = {log.skill.name: log.model for log in logs if log.skill is not None}
    assert models == {
        "spaced-review": "fake-light",  # retrieval stage override
        "set-success-criteria": "fake-base",  # start stage: default model
    }
