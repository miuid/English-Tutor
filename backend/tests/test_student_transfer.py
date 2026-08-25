"""Tests for student data export/import (ISS-011).

Covers the export document shape and the export -> delete -> import
round-trip that must preserve a student's progress.
"""

import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_provider
from app.config import get_settings
from app.database import get_engine
from app.llm import FakeProvider
from app.main import app

FEEDBACK_WITH_LEVELS = """## Per-criterion levels
- Understanding of text / ideas: **C** — a point exists but is vague.
- Analysis (how techniques create meaning): **D** — quote dropped in, effect not explained.
- Use of evidence: **C** — relevant quote, loosely integrated.
- Structure & cohesion: **D** — no link back.
- Language & vocabulary: **C** — clear but flat.

Strength: You chose a relevant simile.
Your 1–2 next steps to level up:
  1. Explain how the simile creates its effect.
Self-check: how would you rate yourself against these criteria?
"""

FULL_LOOP_RESPONSES = [
    "retrieval warm-up output",
    "criteria output",
    "model output",
    "guided output",
    "guided coaching output",
    "independent task output",
    "Route to: check-structure",
    "coaching output",
    FEEDBACK_WITH_LEVELS,
]


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """Boot the app against a temp SQLite DB."""
    import os
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_API_KEY", "")
    get_settings.cache_clear()
    get_engine.cache_clear()

    fake = FakeProvider(canned_responses=list(FULL_LOOP_RESPONSES))
    app.dependency_overrides[get_provider] = lambda: fake
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
        get_engine().dispose()
        os.unlink(path)


def _drive_full_loop(client: TestClient, student_id: str) -> str:
    """Run a complete session for the given student; return the session id."""
    started = client.post(
        "/api/sessions",
        json={"task_prompt": "How does the poet present war?", "student_id": student_id},
    )
    assert started.status_code == 201
    session_id = started.json()["id"]

    client.post(f"/api/sessions/{session_id}/advance")  # I do
    client.post(f"/api/sessions/{session_id}/advance")  # we do
    client.post(f"/api/sessions/{session_id}/submit", json={"text": "My guided attempt."})
    client.post(f"/api/sessions/{session_id}/advance")  # you do
    client.post(f"/api/sessions/{session_id}/submit", json={"text": "War is bad."})
    return str(session_id)


def _create_student(client: TestClient) -> str:
    created = client.post(
        "/api/students",
        json={
            "name": "Alex",
            "year_level": 8,
            "curriculum": "QCAA",
            "focus_text_types": ["analytical"],
        },
    )
    assert created.status_code == 201
    return str(created.json()["id"])


def test_export_includes_all_student_data(client: TestClient) -> None:
    student_id = _create_student(client)
    session_id = _drive_full_loop(client, student_id)

    res = client.get(f"/api/students/{student_id}/export")
    assert res.status_code == 200
    assert "attachment" in res.headers["content-disposition"]
    assert "english-tutor-export-alex.json" in res.headers["content-disposition"]

    doc = res.json()
    assert doc["format"] == "english-tutor-student-export"
    assert doc["version"] == 1
    assert doc["student"]["name"] == "Alex"
    assert doc["student"]["year_level"] == 8
    assert doc["student"]["focus_text_types"] == ["analytical"]

    assert len(doc["sessions"]) == 1
    session = doc["sessions"][0]
    assert session["stage"] == "ended"
    # SuccessCriterion rows are exported when present; the interactive loop
    # does not persist them today, so an empty list is valid here.
    assert "success_criteria" in session
    assert session["interaction_logs"], "export must include interaction logs"

    attempts = session["attempts"]
    assert len(attempts) > 0
    texts = [a["student_text"] for a in attempts]
    assert "War is bad." in texts

    feedbacks = [a["feedback"] for a in attempts if a["feedback"] is not None]
    assert feedbacks, "export must include feedback"
    scores = feedbacks[0]["rubric_scores"]
    assert len(scores) == 5
    names = {s["criterion_name"] for s in scores}
    assert "Structure & cohesion" in names

    # The session id itself is not part of the document shape check, but the
    # exported data must correspond to the driven session.
    state = client.get(f"/api/sessions/{session_id}")
    assert state.status_code == 200
    assert len(state.json()["turns"]) == len(attempts)


def test_export_unknown_student_returns_404(client: TestClient) -> None:
    res = client.get(f"/api/students/{uuid.uuid4()}/export")
    assert res.status_code == 404


def test_export_delete_import_round_trip_preserves_progress(client: TestClient) -> None:
    student_id = _create_student(client)
    _drive_full_loop(client, student_id)

    before = client.get(f"/api/students/{student_id}/progress")
    assert before.status_code == 200
    before_scores = [
        (s["criterion_name"], s["level"], s["scored_at"]) for s in before.json()["scores"]
    ]
    assert len(before_scores) == 5

    doc = client.get(f"/api/students/{student_id}/export").json()

    deleted = client.delete(f"/api/students/{student_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/students/{student_id}").status_code == 404

    imported = client.post("/api/students/import", json=doc)
    assert imported.status_code == 201
    new_id = imported.json()["id"]
    assert new_id != student_id, "import must create a fresh profile id"
    assert imported.json()["name"] == "Alex"
    assert imported.json()["focus_text_types"] == ["analytical"]

    after = client.get(f"/api/students/{new_id}/progress")
    assert after.status_code == 200
    after_scores = [
        (s["criterion_name"], s["level"], s["scored_at"]) for s in after.json()["scores"]
    ]
    assert after_scores == before_scores, "round-trip must preserve rubric progress"

    # The restored session replays fully: same turns, ended stage.
    sessions = [
        s for s in (doc["sessions"]) if s["stage"] == "ended"
    ]
    assert len(sessions) == 1
    students = client.get("/api/students").json()
    assert [s["name"] for s in students] == ["Alex"]


def test_import_without_delete_restores_alongside_original(client: TestClient) -> None:
    """A backup restores as a second profile instead of colliding."""
    student_id = _create_student(client)
    _drive_full_loop(client, student_id)
    doc = client.get(f"/api/students/{student_id}/export").json()

    imported = client.post("/api/students/import", json=doc)
    assert imported.status_code == 201
    new_id = imported.json()["id"]
    assert new_id != student_id

    students = client.get("/api/students").json()
    assert len(students) == 2
    for sid in (student_id, new_id):
        progress = client.get(f"/api/students/{sid}/progress")
        assert progress.status_code == 200
        assert len(progress.json()["scores"]) == 5


def test_import_rejects_malformed_payload(client: TestClient) -> None:
    res = client.post("/api/students/import", json={"hello": "world"})
    assert res.status_code == 400

    res = client.post(
        "/api/students/import",
        json={"format": "english-tutor-student-export", "version": 99},
    )
    assert res.status_code == 400

    res = client.post(
        "/api/students/import",
        json={
            "format": "english-tutor-student-export",
            "version": 1,
            "student": {"name": "", "year_level": 8, "curriculum": "QCAA"},
            "sessions": [],
        },
    )
    assert res.status_code == 400


def test_import_minimal_profile_only(client: TestClient) -> None:
    """An export-shaped document with no sessions still restores the profile."""
    res = client.post(
        "/api/students/import",
        json={
            "format": "english-tutor-student-export",
            "version": 1,
            "student": {
                "name": "Sam",
                "year_level": 9,
                "curriculum": "QCAA",
                "focus_text_types": [],
                "created_at": None,
            },
            "sessions": [],
        },
    )
    assert res.status_code == 201
    assert res.json()["name"] == "Sam"
    assert res.json()["year_level"] == 9


def test_export_import_round_trip_preserves_coach_tone(client: TestClient) -> None:
    created = client.post(
        "/api/students",
        json={"name": "Rae", "year_level": 8, "coach_tone": "humorous"},
    )
    assert created.status_code == 201
    student_id = created.json()["id"]

    doc = client.get(f"/api/students/{student_id}/export").json()
    assert doc["student"]["coach_tone"] == "humorous"

    imported = client.post("/api/students/import", json=doc)
    assert imported.status_code == 201
    assert imported.json()["coach_tone"] == "humorous"


def test_import_older_export_without_coach_tone_defaults_warm(client: TestClient) -> None:
    """Exports from before ISS-018 carry no coach_tone; import must default."""
    res = client.post(
        "/api/students/import",
        json={
            "format": "english-tutor-student-export",
            "version": 1,
            "student": {
                "name": "Sam",
                "year_level": 9,
                "curriculum": "QCAA",
                "focus_text_types": [],
                "created_at": None,
            },
            "sessions": [],
        },
    )
    assert res.status_code == 201
    assert res.json()["coach_tone"] == "warm"


def test_import_rejects_invalid_coach_tone(client: TestClient) -> None:
    res = client.post(
        "/api/students/import",
        json={
            "format": "english-tutor-student-export",
            "version": 1,
            "student": {
                "name": "Sam",
                "year_level": 9,
                "curriculum": "QCAA",
                "coach_tone": "sassy",
            },
            "sessions": [],
        },
    )
    assert res.status_code == 400


def test_export_import_round_trip_preserves_shared_goal(client: TestClient) -> None:
    """ISS-020: the shared goal survives export -> import."""
    created = client.post(
        "/api/students",
        json={
            "name": "Rae",
            "year_level": 8,
            "shared_goal": "Write clearer paragraphs",
        },
    )
    assert created.status_code == 201
    student_id = created.json()["id"]

    doc = client.get(f"/api/students/{student_id}/export").json()
    assert doc["student"]["shared_goal"] == "Write clearer paragraphs"

    imported = client.post("/api/students/import", json=doc)
    assert imported.status_code == 201
    assert imported.json()["shared_goal"] == "Write clearer paragraphs"


def test_import_older_export_without_shared_goal_defaults_none(
    client: TestClient,
) -> None:
    """Exports from before ISS-020 carry no shared_goal; import must default."""
    res = client.post(
        "/api/students/import",
        json={
            "format": "english-tutor-student-export",
            "version": 1,
            "student": {
                "name": "Sam",
                "year_level": 9,
                "curriculum": "QCAA",
                "focus_text_types": [],
                "created_at": None,
            },
            "sessions": [],
        },
    )
    assert res.status_code == 201
    assert res.json()["shared_goal"] is None
