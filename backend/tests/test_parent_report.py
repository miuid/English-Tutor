"""Tests for ISS-019: weekly parent report with the D3 privacy boundary."""

import os
import tempfile
import uuid
from collections.abc import Generator
from datetime import UTC, date, datetime, time, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SqlSession
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.database import get_engine
from app.main import app
from app.models import Attempt, Feedback, RubricScore, Session, Student
from app.parent_report import build_parent_report

SECRET_ESSAY = "SECRET-ESSAY-MARKER full student writing must never leak"
SECRET_FEEDBACK = "SECRET-FEEDBACK-MARKER tutor prose must never leak"
SECRET_NOTE = "SECRET-NOTE-MARKER rubric note must never leak"
SECRET_PROMPT = "SECRET-PROMPT-MARKER task prompt must never leak"


def _make_student(db: SqlSession, weekly_goal: int = 4) -> Student:
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


def _add_session(
    db: SqlSession,
    student: Student,
    day: date,
    now: datetime,
    *,
    time_spent_seconds: int = 0,
) -> Session:
    session = Session(
        student_id=student.id,
        started_at=_on_local_day(day, now),
        time_spent_seconds=time_spent_seconds,
    )
    db.add(session)
    db.commit()
    return session


def _add_score(
    db: SqlSession,
    student: Student,
    criterion: str,
    level: str,
    day: date,
    now: datetime,
    *,
    note: str | None = None,
    session: Session | None = None,
) -> RubricScore:
    """Persist one graded attempt chain ending in a single rubric score."""
    if session is None:
        session = _add_session(db, student, day, now)
    attempt = Attempt(
        session=session,
        student=student,
        task_type="paragraph",
        mode="practice",
        task_prompt=SECRET_PROMPT,
        student_text=SECRET_ESSAY,
    )
    db.add(attempt)
    db.commit()
    feedback = Feedback(
        attempt=attempt,
        strength=SECRET_FEEDBACK,
        next_steps=SECRET_FEEDBACK,
    )
    db.add(feedback)
    db.commit()
    score = RubricScore(
        feedback=feedback,
        criterion_name=criterion,
        level=level,
        note=note,
        scored_at=_on_local_day(day, now),
    )
    db.add(score)
    db.commit()
    return score


def test_new_student_reports_cold_start(db_session: SqlSession) -> None:
    """No activity: zero sessions, no trends, no highlight, goal nudge."""
    student = _make_student(db_session)
    report = build_parent_report(db_session, student)
    assert report.sessions_this_week == 0
    assert report.practice_seconds_this_week == 0
    assert report.weekly_goal == 4
    assert report.goal_met is False
    assert report.trends == []
    assert report.highlight is None
    assert "4 sessions" in report.next_week_suggestion


def test_week_counts_sessions_and_time_monday_to_today(db_session: SqlSession) -> None:
    """Sessions/time from last week are excluded from the weekly counts."""
    now = datetime.now(UTC)
    today = now.astimezone().date()
    week_start = today - timedelta(days=today.weekday())  # Monday
    student = _make_student(db_session)
    _add_session(db_session, student, week_start, now, time_spent_seconds=600)
    _add_session(db_session, student, today, now, time_spent_seconds=300)
    _add_session(db_session, student, week_start - timedelta(days=1), now)
    report = build_parent_report(db_session, student, now=now)
    assert report.week_start == week_start
    assert report.week_end == today
    assert report.sessions_this_week == 2
    assert report.practice_seconds_this_week == 900
    assert report.goal_met is False  # 2 < 4


def test_trends_track_latest_previous_and_direction(db_session: SqlSession) -> None:
    """Trends cover full history; direction compares the last two scores."""
    now = datetime.now(UTC)
    today = now.astimezone().date()
    student = _make_student(db_session)
    _add_score(db_session, student, "Story & tension", "C", today - timedelta(days=9), now)
    _add_score(db_session, student, "Story & tension", "B", today, now)
    _add_score(db_session, student, "Showing & voice", "C+", today, now)
    report = build_parent_report(db_session, student, now=now)
    trends = {trend.criterion_name: trend for trend in report.trends}
    story = trends["Story & tension"]
    assert story.latest_level == "B"
    assert story.previous_level == "C"
    assert story.direction == "up"
    assert [point.level for point in story.points] == ["C", "B"]
    voice = trends["Showing & voice"]
    assert voice.direction == "new"
    assert voice.previous_level is None


def test_highlight_prefers_this_weeks_level_up(db_session: SqlSession) -> None:
    """A level-up inside the week becomes the highlight; older ones do not."""
    now = datetime.now(UTC)
    today = now.astimezone().date()
    student = _make_student(db_session)
    _add_score(db_session, student, "Story & tension", "C", today - timedelta(days=9), now)
    _add_score(db_session, student, "Story & tension", "B", today - timedelta(days=8), now)
    report_old = build_parent_report(db_session, student, now=now)
    # The C → B crossing happened last week; no sessions/goal-met this week.
    assert report_old.highlight is None

    _add_score(db_session, student, "Story & tension", "A", today, now)
    report = build_parent_report(db_session, student, now=now)
    assert report.highlight == "Story & tension lifted B → A this week."


def test_highlight_falls_back_to_goal_met(db_session: SqlSession) -> None:
    now = datetime.now(UTC)
    today = now.astimezone().date()
    student = _make_student(db_session, weekly_goal=2)
    _add_session(db_session, student, today, now)
    _add_session(db_session, student, today, now)
    report = build_parent_report(db_session, student, now=now)
    assert report.highlight == "Alex met the weekly goal — 2 sessions this week."


def test_suggestion_targets_dip_once_goal_met(db_session: SqlSession) -> None:
    """Goal met + a dipping criterion → revisit suggestion names the move."""
    now = datetime.now(UTC)
    today = now.astimezone().date()
    student = _make_student(db_session, weekly_goal=1)
    _add_score(db_session, student, "Story & tension", "B", today - timedelta(days=2), now)
    _add_score(db_session, student, "Story & tension", "C", today, now)
    report = build_parent_report(db_session, student, now=now)
    assert report.goal_met is True
    assert report.next_week_suggestion.startswith("Revisit Story & tension")
    assert "B → C" in report.next_week_suggestion


def test_suggestion_targets_weakest_criterion_when_no_dip(db_session: SqlSession) -> None:
    now = datetime.now(UTC)
    today = now.astimezone().date()
    student = _make_student(db_session, weekly_goal=1)
    session = _add_session(db_session, student, today, now)
    _add_score(db_session, student, "Story & tension", "A", today, now, session=session)
    _add_score(db_session, student, "Showing & voice", "C", today, now, session=session)
    report = build_parent_report(db_session, student, now=now)
    assert report.goal_met is True
    assert "Next growth area: Showing & voice (currently C)." in (
        report.next_week_suggestion
    )


def test_report_never_contains_student_or_tutor_text(db_session: SqlSession) -> None:
    """D3 boundary at the builder level: no essay/feedback/note/prompt text."""
    now = datetime.now(UTC)
    today = now.astimezone().date()
    student = _make_student(db_session, weekly_goal=1)
    _add_score(db_session, student, "Story & tension", "B", today, now, note=SECRET_NOTE)
    report = build_parent_report(db_session, student, now=now)
    rendered = repr(report)
    for secret in (SECRET_ESSAY, SECRET_FEEDBACK, SECRET_NOTE, SECRET_PROMPT):
        assert secret not in rendered


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


def _seed_graded_week(api_client: TestClient) -> dict[str, object]:
    """Create a student with one graded session this week, via the ORM."""
    response = api_client.post(
        "/api/students",
        json={"name": "Alex", "year_level": 8, "curriculum": "QCAA", "weekly_goal": 1},
    )
    assert response.status_code == 201
    student_data: dict[str, object] = response.json()

    now = datetime.now(UTC)
    today = now.astimezone().date()
    session_factory = sessionmaker(bind=get_engine())
    with session_factory() as db:
        student = db.get(Student, uuid.UUID(str(student_data["id"])))
        assert student is not None
        _add_score(
            db,
            student,
            "Story & tension",
            "C",
            today - timedelta(days=2),
            now,
            note=SECRET_NOTE,
        )
        _add_score(db, student, "Story & tension", "B", today, now)
    return student_data


def test_parent_report_endpoint_shape(api_client: TestClient) -> None:
    student = _seed_graded_week(api_client)
    response = api_client.get(f"/api/students/{student['id']}/parent-report")
    assert response.status_code == 200
    data = response.json()
    assert data["student_id"] == student["id"]
    assert data["student_name"] == "Alex"
    assert data["sessions_this_week"] == 2
    assert data["weekly_goal"] == 1
    assert data["goal_met"] is True
    assert data["highlight"] == "Story & tension lifted C → B this week."
    assert len(data["trends"]) == 1
    trend = data["trends"][0]
    assert trend["criterion_name"] == "Story & tension"
    assert trend["latest_level"] == "B"
    assert trend["previous_level"] == "C"
    assert trend["direction"] == "up"
    assert len(trend["points"]) == 2
    assert data["next_week_suggestion"]


def test_parent_report_endpoint_404_for_unknown_student(api_client: TestClient) -> None:
    assert api_client.get(f"/api/students/{uuid.uuid4()}/parent-report").status_code == 404
    assert (
        api_client.get(f"/api/students/{uuid.uuid4()}/parent-report/print").status_code
        == 404
    )


def test_parent_report_json_enforces_privacy_boundary(api_client: TestClient) -> None:
    """The JSON report must contain no essay, feedback, note, or prompt text."""
    student = _seed_graded_week(api_client)
    response = api_client.get(f"/api/students/{student['id']}/parent-report")
    assert response.status_code == 200
    for secret in (SECRET_ESSAY, SECRET_FEEDBACK, SECRET_NOTE, SECRET_PROMPT):
        assert secret not in response.text


def test_parent_report_print_generates_from_same_data(api_client: TestClient) -> None:
    """The printable page carries the same trends — and the same boundary."""
    student = _seed_graded_week(api_client)
    response = api_client.get(f"/api/students/{student['id']}/parent-report/print")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    html = response.text
    assert "Weekly report — Alex" in html
    assert "Story &amp; tension" in html
    assert "lifted C → B this week" in html
    assert "Suggested focus for next week" in html
    assert "window.print()" in html  # print-to-PDF path
    for secret in (SECRET_ESSAY, SECRET_FEEDBACK, SECRET_NOTE, SECRET_PROMPT):
        assert secret not in html
