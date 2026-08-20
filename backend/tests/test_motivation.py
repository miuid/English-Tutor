"""Tests for ISS-016: streaks and weekly goal (gentle motivation layer)."""

import os
import tempfile
import uuid
from collections.abc import Generator
from datetime import UTC, date, datetime, time, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SqlSession

from app.config import get_settings
from app.database import get_engine
from app.main import app
from app.models import DEFAULT_WEEKLY_GOAL, Session, Student
from app.motivation import build_motivation
from app.student_transfer import export_student, import_student


def _make_student(db: SqlSession, weekly_goal: int = DEFAULT_WEEKLY_GOAL) -> Student:
    student = Student(
        name="Alex",
        year_level=8,
        curriculum="QCAA",
        weekly_goal=weekly_goal,
    )
    db.add(student)
    db.commit()
    return student


def _on_local_day(day: date, now: datetime) -> datetime:
    """A UTC instant guaranteed to fall on ``day`` (local noon, DST-safe)."""
    local_tz = now.astimezone().tzinfo
    return datetime.combine(day, time(12, 0), tzinfo=local_tz).astimezone(UTC)


def _add_session(db: SqlSession, student: Student, day: date, now: datetime) -> Session:
    session = Session(student_id=student.id, started_at=_on_local_day(day, now))
    db.add(session)
    db.commit()
    return session


def test_no_sessions_returns_cold_start(db_session: SqlSession) -> None:
    """A brand-new student has no streak and no recovery prompt."""
    student = _make_student(db_session)
    summary = build_motivation(db_session, student.id, student.weekly_goal)
    assert summary.current_streak == 0
    assert summary.streak_broken is False
    assert summary.weekly_goal == DEFAULT_WEEKLY_GOAL
    assert summary.sessions_this_week == 0
    assert summary.goal_met is False
    assert summary.last_activity_date is None


def test_consecutive_days_build_streak(db_session: SqlSession) -> None:
    """Sessions today + the two prior days make a 3-day streak."""
    now = datetime.now(UTC)
    today = now.astimezone().date()
    student = _make_student(db_session)
    for offset in (0, 1, 2):
        _add_session(db_session, student, today - timedelta(days=offset), now)
    summary = build_motivation(db_session, student.id, student.weekly_goal, now=now)
    assert summary.current_streak == 3
    assert summary.streak_broken is False
    assert summary.last_activity_date == today


def test_yesterday_only_keeps_streak_alive(db_session: SqlSession) -> None:
    """A session yesterday (none yet today) still counts as a live streak."""
    now = datetime.now(UTC)
    today = now.astimezone().date()
    student = _make_student(db_session)
    _add_session(db_session, student, today - timedelta(days=1), now)
    summary = build_motivation(db_session, student.id, student.weekly_goal, now=now)
    assert summary.current_streak == 1
    assert summary.streak_broken is False


def test_missed_day_breaks_streak_into_recovery(db_session: SqlSession) -> None:
    """A lapsed run reports streak 0 + recovery flag, never a penalty."""
    now = datetime.now(UTC)
    today = now.astimezone().date()
    student = _make_student(db_session)
    _add_session(db_session, student, today - timedelta(days=3), now)
    _add_session(db_session, student, today - timedelta(days=4), now)
    summary = build_motivation(db_session, student.id, student.weekly_goal, now=now)
    assert summary.current_streak == 0
    assert summary.streak_broken is True
    assert summary.last_activity_date == today - timedelta(days=3)


def test_week_counts_sessions_monday_to_today(db_session: SqlSession) -> None:
    """Weekly progress counts sessions (not days) from Monday to today."""
    now = datetime.now(UTC)
    today = now.astimezone().date()
    week_start = today - timedelta(days=today.weekday())  # Monday
    student = _make_student(db_session)
    _add_session(db_session, student, week_start, now)  # Monday of this week
    _add_session(db_session, student, today, now)  # today (counts even if Monday)
    _add_session(db_session, student, week_start - timedelta(days=1), now)  # last week
    summary = build_motivation(db_session, student.id, student.weekly_goal, now=now)
    assert summary.sessions_this_week == 2


def test_goal_met_only_at_or_above_weekly_goal(db_session: SqlSession) -> None:
    """goal_met follows the student's own persisted weekly goal."""
    now = datetime.now(UTC)
    today = now.astimezone().date()
    student = _make_student(db_session, weekly_goal=2)
    _add_session(db_session, student, today, now)
    summary = build_motivation(db_session, student.id, student.weekly_goal, now=now)
    assert summary.goal_met is False
    _add_session(db_session, student, today, now)
    summary = build_motivation(db_session, student.id, student.weekly_goal, now=now)
    assert summary.goal_met is True


def test_weekly_goal_round_trips_through_export_import(db_session: SqlSession) -> None:
    """Export preserves the weekly goal; older exports default to 4."""
    student = _make_student(db_session, weekly_goal=6)
    document = export_student(db_session, student)
    assert document["student"]["weekly_goal"] == 6
    restored = import_student(db_session, document)
    assert restored.id != student.id
    assert restored.weekly_goal == 6

    del document["student"]["weekly_goal"]  # pre-ISS-016 export shape
    restored_legacy = import_student(db_session, document)
    assert restored_legacy.weekly_goal == DEFAULT_WEEKLY_GOAL


@pytest.fixture
def api_client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """Boot the app against a temp SQLite DB (no LLM calls on these routes)."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_API_KEY", "")
    get_settings.cache_clear()
    get_engine.cache_clear()
    try:
        with TestClient(app) as client:
            yield client
    finally:
        get_engine().dispose()
        os.unlink(path)


def _create_student(client: TestClient, **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"name": "Alex", "year_level": 8, "curriculum": "QCAA"}
    payload.update(overrides)
    response = client.post("/api/students", json=payload)
    assert response.status_code == 201
    data: dict[str, Any] = response.json()
    return data


def test_motivation_endpoint_defaults(api_client: TestClient) -> None:
    """GET motivation returns the cold-start state with the default goal."""
    student = _create_student(api_client)
    response = api_client.get(f"/api/students/{student['id']}/motivation")
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == student["id"]
    assert data["current_streak"] == 0
    assert data["streak_broken"] is False
    assert data["weekly_goal"] == DEFAULT_WEEKLY_GOAL
    assert data["sessions_this_week"] == 0
    assert data["goal_met"] is False
    assert data["last_activity_date"] is None


def test_motivation_endpoint_404_for_unknown_student(api_client: TestClient) -> None:
    response = api_client.get(f"/api/students/{uuid.uuid4()}/motivation")
    assert response.status_code == 404


def test_motivation_counts_started_session(api_client: TestClient) -> None:
    """Starting a real session moves the streak and the weekly count."""
    student = _create_student(api_client)
    response = api_client.post("/api/sessions", json={"student_id": student["id"]})
    assert response.status_code == 201
    data = api_client.get(f"/api/students/{student['id']}/motivation").json()
    assert data["current_streak"] == 1
    assert data["sessions_this_week"] == 1
    assert data["goal_met"] is False
    assert data["last_activity_date"] is not None


def test_weekly_goal_patch_persists(api_client: TestClient) -> None:
    """PATCH weekly_goal persists and flows into the motivation response."""
    student = _create_student(api_client)
    assert student["weekly_goal"] == DEFAULT_WEEKLY_GOAL
    response = api_client.patch(f"/api/students/{student['id']}", json={"weekly_goal": 2})
    assert response.status_code == 200
    assert response.json()["weekly_goal"] == 2
    data = api_client.get(f"/api/students/{student['id']}/motivation").json()
    assert data["weekly_goal"] == 2
    # Two sessions now meet the lowered goal; one is not enough.
    api_client.post("/api/sessions", json={"student_id": student["id"]})
    data = api_client.get(f"/api/students/{student['id']}/motivation").json()
    assert data["goal_met"] is False
    api_client.post("/api/sessions", json={"student_id": student["id"]})
    data = api_client.get(f"/api/students/{student['id']}/motivation").json()
    assert data["goal_met"] is True


def test_weekly_goal_out_of_range_rejected(api_client: TestClient) -> None:
    student = _create_student(api_client)
    for bad in (0, 15, "many"):
        response = api_client.patch(
            f"/api/students/{student['id']}", json={"weekly_goal": bad}
        )
        assert response.status_code == 422
