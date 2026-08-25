"""Tests for ISS-017: criterion level-up celebration (derived band crossings)."""

import os
import tempfile
import uuid
from collections.abc import Generator
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SqlSession
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.database import get_engine
from app.level_ups import band_of, build_level_ups
from app.main import app
from app.models import Attempt, Feedback, RubricScore, Session, Student

_BASE_TIME = datetime(2026, 8, 1, 12, 0, tzinfo=UTC)


def _make_student(db: SqlSession) -> Student:
    student = Student(name="Alex", year_level=8, curriculum="QCAA")
    db.add(student)
    db.commit()
    return student


def _add_score(
    db: SqlSession,
    student: Student,
    criterion: str,
    level: str,
    *,
    day_offset: int,
    note: str | None = None,
) -> RubricScore:
    """Persist one graded attempt chain ending in a single rubric score."""
    session = Session(student_id=student.id, started_at=_BASE_TIME + timedelta(days=day_offset))
    db.add(session)
    db.commit()
    attempt = Attempt(
        session=session,
        student=student,
        task_type="paragraph",
        mode="practice",
        task_prompt="Write a paragraph.",
        student_text="Test text.",
    )
    db.add(attempt)
    db.commit()
    feedback = Feedback(attempt=attempt, strength="Good start.", next_steps="Keep going.")
    db.add(feedback)
    db.commit()
    score = RubricScore(
        feedback=feedback,
        criterion_name=criterion,
        level=level,
        note=note,
        scored_at=_BASE_TIME + timedelta(days=day_offset),
    )
    db.add(score)
    db.commit()
    return score


def test_band_of_normalises_modifiers() -> None:
    assert band_of("C+") == "C"
    assert band_of("b–") == "B"
    assert band_of(" A ") == "A"
    assert band_of("E-") == "E"
    assert band_of("") is None
    assert band_of("?") is None


def test_no_scores_returns_no_level_ups(db_session: SqlSession) -> None:
    student = _make_student(db_session)
    assert build_level_ups(db_session, student.id) == []


def test_single_score_is_not_a_level_up(db_session: SqlSession) -> None:
    """A first-ever score has no previous band to cross."""
    student = _make_student(db_session)
    _add_score(db_session, student, "Analysis & effect", "D", day_offset=0)
    assert build_level_ups(db_session, student.id) == []


def test_band_crossing_is_detected_with_mechanism_note(db_session: SqlSession) -> None:
    """D → C fires one event carrying the new score's note and identifiers."""
    student = _make_student(db_session)
    _add_score(db_session, student, "Analysis & effect", "D", day_offset=0)
    crossed = _add_score(
        db_session,
        student,
        "Analysis & effect",
        "C",
        day_offset=1,
        note="Now explains how the metaphor creates the effect.",
    )
    events = build_level_ups(db_session, student.id)
    assert len(events) == 1
    event = events[0]
    assert event.criterion_name == "Analysis & effect"
    assert event.from_level == "D"
    assert event.to_level == "C"
    assert event.note == "Now explains how the metaphor creates the effect."
    assert event.scored_at == crossed.scored_at
    assert event.feedback_id == crossed.feedback_id


def test_modifier_crossing_counts_as_band_crossing(db_session: SqlSession) -> None:
    """C+ → B– crosses the C/B boundary even though both levels carry modifiers."""
    student = _make_student(db_session)
    _add_score(db_session, student, "Structure", "C+", day_offset=0)
    _add_score(db_session, student, "Structure", "B–", day_offset=1)
    events = build_level_ups(db_session, student.id)
    assert [(e.from_level, e.to_level) for e in events] == [("C+", "B–")]


def test_within_band_move_is_not_a_level_up(db_session: SqlSession) -> None:
    """C → C+ improves the modifier but does not cross a band."""
    student = _make_student(db_session)
    _add_score(db_session, student, "Structure", "C", day_offset=0)
    _add_score(db_session, student, "Structure", "C+", day_offset=1)
    assert build_level_ups(db_session, student.id) == []


def test_dip_and_recovery_does_not_re_celebrate(db_session: SqlSession) -> None:
    """C → B → C → B fires once: only the first arrival at a best band counts."""
    student = _make_student(db_session)
    _add_score(db_session, student, "Analysis & effect", "C", day_offset=0)
    _add_score(db_session, student, "Analysis & effect", "B", day_offset=1)
    _add_score(db_session, student, "Analysis & effect", "C", day_offset=2)
    _add_score(db_session, student, "Analysis & effect", "B", day_offset=3)
    events = build_level_ups(db_session, student.id)
    assert [(e.from_level, e.to_level) for e in events] == [("C", "B")]


def test_unparseable_levels_are_skipped(db_session: SqlSession) -> None:
    student = _make_student(db_session)
    _add_score(db_session, student, "Analysis & effect", "?", day_offset=0)
    _add_score(db_session, student, "Analysis & effect", "C", day_offset=1)
    assert build_level_ups(db_session, student.id) == []


def test_crossings_tracked_per_criterion(db_session: SqlSession) -> None:
    """Each criterion keeps its own best band; events arrive oldest first."""
    student = _make_student(db_session)
    _add_score(db_session, student, "Analysis & effect", "D", day_offset=0)
    _add_score(db_session, student, "Structure", "C", day_offset=1)
    _add_score(db_session, student, "Structure", "B", day_offset=2)
    _add_score(db_session, student, "Analysis & effect", "C", day_offset=3)
    events = build_level_ups(db_session, student.id)
    assert [(e.criterion_name, e.from_level, e.to_level) for e in events] == [
        ("Structure", "C", "B"),
        ("Analysis & effect", "D", "C"),
    ]


@pytest.fixture
def api_client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """Boot the app against a temp SQLite DB (no LLM calls on this route)."""
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


def _create_student(client: TestClient) -> dict[str, Any]:
    response = client.post(
        "/api/students", json={"name": "Alex", "year_level": 8, "curriculum": "QCAA"}
    )
    assert response.status_code == 201
    data: dict[str, Any] = response.json()
    return data


def test_level_ups_endpoint_cold_start(api_client: TestClient) -> None:
    student = _create_student(api_client)
    response = api_client.get(f"/api/students/{student['id']}/level-ups")
    assert response.status_code == 200
    assert response.json() == {"student_id": student["id"], "level_ups": []}


def test_level_ups_endpoint_404_for_unknown_student(api_client: TestClient) -> None:
    response = api_client.get(f"/api/students/{uuid.uuid4()}/level-ups")
    assert response.status_code == 404


def test_level_ups_endpoint_surfaces_crossing(api_client: TestClient) -> None:
    """A crossing written to the same DB is served by the endpoint."""
    student = _create_student(api_client)
    session_factory = sessionmaker(bind=get_engine())
    with session_factory() as db:
        row = db.get(Student, uuid.UUID(student["id"]))
        assert row is not None
        _add_score(db, row, "Analysis & effect", "D", day_offset=0)
        _add_score(
            db,
            row,
            "Analysis & effect",
            "C",
            day_offset=1,
            note="Now explains how the metaphor creates the effect.",
        )
    response = api_client.get(f"/api/students/{student['id']}/level-ups")
    assert response.status_code == 200
    events = response.json()["level_ups"]
    assert len(events) == 1
    event = events[0]
    assert event["criterion_name"] == "Analysis & effect"
    assert event["from_level"] == "D"
    assert event["to_level"] == "C"
    assert event["note"] == "Now explains how the metaphor creates the effect."
    assert event["session_id"]
    assert event["feedback_id"]
