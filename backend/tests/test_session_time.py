"""Tests for the soft daily time budget, wrap-up, and pause/resume."""

import os
import tempfile
import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SqlSession

from app.api.deps import get_provider
from app.config import get_settings
from app.database import get_engine
from app.llm import FakeProvider
from app.main import app
from app.sessions.interactive import (
    IDLE_CAP_SECONDS,
    InteractiveLoop,
    StageConflictError,
)
from app.skills.executor import SkillExecutionService
from app.skills.loader import load_skills
from app.skills.sync import sync_skills


class FakeClock:
    """Mutable UTC clock for deterministic time-budget tests."""

    def __init__(self, start: datetime) -> None:
        self.t = start

    def __call__(self) -> datetime:
        return self.t

    def advance(self, **kwargs: float) -> None:
        self.t += timedelta(**kwargs)


# Far from any local midnight so small advances stay on the same local day in
# every plausible server timezone.
T0 = datetime(2026, 8, 10, 0, 0, tzinfo=UTC)


@pytest.fixture
def skills() -> dict:
    from pathlib import Path

    return {s.name: s for s in load_skills(Path(get_settings().skills_dir))}


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock(T0)


@pytest.fixture
def loop(db_session: SqlSession, skills: dict, clock: FakeClock) -> InteractiveLoop:
    """InteractiveLoop with a canned provider, fake clock, 15-minute budget."""
    sync_skills(db_session)
    provider = FakeProvider()
    executor = SkillExecutionService(provider=provider, model_name="fake-model")
    return InteractiveLoop(
        db=db_session,
        executor=executor,
        skills=skills,
        time_limit_seconds=15 * 60,
        now=clock,
    )


async def _start(loop: InteractiveLoop):
    return await loop.start(task_prompt="Test prompt", year_level="8", text_type="analytical")


@pytest.mark.asyncio
async def test_time_accumulates_between_interactions(loop, clock):
    session = await _start(loop)
    clock.advance(minutes=3)

    await loop.advance(session.id)

    assert session.time_spent_seconds == 3 * 60


@pytest.mark.asyncio
async def test_long_gap_is_capped(loop, clock):
    """Walking away without pausing counts at most the idle cap."""
    session = await _start(loop)
    clock.advance(minutes=45)

    await loop.advance(session.id)

    assert session.time_spent_seconds == IDLE_CAP_SECONDS


@pytest.mark.asyncio
async def test_day_rollover_resets_budget(loop, clock):
    session = await _start(loop)
    clock.advance(minutes=4)
    await loop.advance(session.id)
    assert session.time_spent_seconds == 4 * 60

    clock.advance(days=1)
    await loop.advance(session.id)

    assert session.time_spent_seconds == 0


@pytest.mark.asyncio
async def test_time_up_advance_wraps_up_and_pauses(loop, clock):
    session = await _start(loop)
    clock.advance(minutes=9)
    await loop.advance(session.id)  # -> I do, spent 540
    clock.advance(minutes=9)  # spent would reach 1080: over the 15-min budget

    result = await loop.advance(session.id)

    assert result.time_up is True
    assert result.turn.task_type == "wrap-up"
    assert result.turn.skill_id is None
    assert "15 minutes" in result.turn.student_text
    assert session.paused_at is not None
    assert session.stage == "I do"  # no new stage was started
    # Only set-success-criteria + model-response ran; wrap-up costs no LLM call.
    assert len(session.interaction_logs) == 2


@pytest.mark.asyncio
async def test_wrap_up_is_not_duplicated(loop, clock):
    session = await _start(loop)
    clock.advance(minutes=9)
    await loop.advance(session.id)
    clock.advance(minutes=9)
    first = await loop.advance(session.id)
    assert first.time_up is True

    # Same day, still over budget: resuming and advancing reuses the wrap-up.
    loop.resume(session.id)
    clock.advance(minutes=1)
    second = await loop.advance(session.id)

    assert second.time_up is True
    assert second.turn.id == first.turn.id


@pytest.mark.asyncio
async def test_we_do_submit_completes_then_wraps_up(loop, clock):
    session = await _start(loop)
    clock.advance(minutes=3)
    await loop.advance(session.id)  # -> I do (180)
    clock.advance(minutes=3)
    await loop.advance(session.id)  # -> we do (360)
    clock.advance(minutes=11)  # capped at 600 -> 960 total: over budget

    result = await loop.submit(session.id, "My guided attempt.")

    # The exchange finished (guided follow-up), then the loop wrapped up.
    assert [t.task_type for t in result.tutor_turns] == ["guided", "wrap-up"]
    assert result.time_up is True
    assert session.paused_at is not None
    assert session.stage == "we do"


@pytest.mark.asyncio
async def test_you_do_submit_always_completes_feedback(loop, clock):
    session = await _start(loop)
    for _ in range(3):
        clock.advance(minutes=3)
        await loop.advance(session.id)
    clock.advance(minutes=30)  # far over budget (capped), stage = you do

    result = await loop.submit(session.id, "War is bad.")

    assert result.feedback is not None
    assert result.time_up is True
    assert session.stage == "ended"
    assert session.ended_at is not None
    assert all(t.task_type != "wrap-up" for t in result.tutor_turns)


@pytest.mark.asyncio
async def test_paused_session_rejects_advance_and_submit(loop, clock):
    session = await _start(loop)
    clock.advance(minutes=1)
    await loop.advance(session.id)  # -> I do
    clock.advance(minutes=1)
    await loop.advance(session.id)  # -> we do
    loop.pause(session.id)

    with pytest.raises(StageConflictError, match="paused"):
        await loop.advance(session.id)
    with pytest.raises(StageConflictError, match="paused"):
        await loop.submit(session.id, "still here")


@pytest.mark.asyncio
async def test_pause_stops_the_clock(loop, clock):
    session = await _start(loop)
    clock.advance(minutes=2)
    await loop.advance(session.id)  # spent 120
    loop.pause(session.id)

    clock.advance(hours=3)  # paused time must not count
    loop.resume(session.id)
    clock.advance(minutes=1)
    await loop.advance(session.id)  # resume zeroes the delta; +60 here

    assert session.time_spent_seconds == 120 + 60
    assert session.paused_at is None


@pytest.mark.asyncio
async def test_resume_next_day_restores_budget(loop, clock):
    session = await _start(loop)
    clock.advance(minutes=9)
    await loop.advance(session.id)  # -> I do
    clock.advance(minutes=9)
    result = await loop.advance(session.id)
    assert result.time_up is True

    clock.advance(days=1)
    loop.resume(session.id)

    assert session.time_spent_seconds == 0
    result = await loop.advance(session.id)
    assert result.time_up is False
    assert result.turn.task_type == "guided"  # the loop continued where it stopped


# --- HTTP level -------------------------------------------------------------


@pytest.fixture
def api_client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_API_KEY", "")
    get_settings.cache_clear()
    get_engine.cache_clear()

    fake = FakeProvider(canned_responses=["resp"] * 20)
    app.dependency_overrides[get_provider] = lambda: fake
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        get_engine().dispose()
        os.unlink(path)


@pytest.fixture
def zero_limit_client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """API client whose daily budget is 0 minutes — time is always up."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("SESSION_TIME_LIMIT_MINUTES", "0")
    get_settings.cache_clear()
    get_engine.cache_clear()

    fake = FakeProvider(canned_responses=["resp"] * 20)
    app.dependency_overrides[get_provider] = lambda: fake
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        get_engine().dispose()
        os.unlink(path)


def _start_http(client: TestClient) -> dict:
    response = client.post("/api/sessions", json={})
    assert response.status_code == 201
    return response.json()


def test_session_out_carries_time_fields(api_client: TestClient) -> None:
    started = _start_http(api_client)

    assert started["paused"] is False
    assert started["time_limit_seconds"] == 15 * 60
    assert started["time_spent_seconds"] == 0
    assert started["time_up"] is False


def test_pause_and_resume_over_http(api_client: TestClient) -> None:
    session_id = _start_http(api_client)["id"]

    paused = api_client.post(f"/api/sessions/{session_id}/pause")
    assert paused.status_code == 200
    assert paused.json()["paused"] is True

    # A paused session refuses to move on.
    assert api_client.post(f"/api/sessions/{session_id}/advance").status_code == 409

    resumed = api_client.post(f"/api/sessions/{session_id}/resume")
    assert resumed.status_code == 200
    assert resumed.json()["paused"] is False

    advanced = api_client.post(f"/api/sessions/{session_id}/advance")
    assert advanced.status_code == 200
    assert advanced.json()["time_up"] is False


def test_pause_resume_unknown_or_ended(api_client: TestClient) -> None:
    missing = uuid.uuid4()
    assert api_client.post(f"/api/sessions/{missing}/pause").status_code == 404
    assert api_client.post(f"/api/sessions/{missing}/resume").status_code == 404


def test_time_up_wraps_up_over_http(zero_limit_client: TestClient) -> None:
    session_id = _start_http(zero_limit_client)["id"]

    advance = zero_limit_client.post(f"/api/sessions/{session_id}/advance")
    assert advance.status_code == 200
    body = advance.json()
    assert body["time_up"] is True
    assert body["paused"] is True
    assert body["turn"]["task_type"] == "wrap-up"
    assert body["turn"]["kind"] == "tutor"
    assert body["stage"] == "start"  # loop stayed put for tomorrow

    state = zero_limit_client.get(f"/api/sessions/{session_id}").json()
    assert state["paused"] is True
    assert state["time_up"] is True
