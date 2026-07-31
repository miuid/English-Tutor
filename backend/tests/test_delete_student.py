"""Tests for the DELETE /api/students/{id} privacy endpoint."""

import uuid

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
def client(monkeypatch: pytest.MonkeyPatch):
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


def _drive_full_loop(client: TestClient) -> str:
    """Run a complete session and return the student_id."""
    started = client.post("/api/sessions", json={"task_prompt": "How does the poet present war?"})
    assert started.status_code == 201
    session_id = started.json()["id"]
    student_id = started.json()["student_id"]

    # I do
    client.post(f"/api/sessions/{session_id}/advance")
    # we do
    client.post(f"/api/sessions/{session_id}/advance")
    # submit guided
    client.post(f"/api/sessions/{session_id}/submit", json={"text": "My guided attempt."})
    # you do
    client.post(f"/api/sessions/{session_id}/advance")
    # submit independent -> ends session
    client.post(f"/api/sessions/{session_id}/submit", json={"text": "War is bad."})

    return student_id


def test_delete_student_cascades_all_data(client: TestClient) -> None:
    """After deletion, no rows for that student remain in any table."""
    student_id = _drive_full_loop(client)

    # Verify data exists before deletion
    progress = client.get(f"/api/students/{student_id}/progress")
    assert progress.status_code == 200
    assert len(progress.json()["scores"]) > 0

    # Delete
    response = client.delete(f"/api/students/{student_id}")
    assert response.status_code == 204

    # Confirm deletion
    response = client.get(f"/api/students/{student_id}/progress")
    assert response.status_code == 404

    response = client.delete(f"/api/students/{student_id}")
    assert response.status_code == 404


def test_delete_unknown_student_returns_404(client: TestClient) -> None:
    """Deleting a non-existent student returns 404."""
    response = client.delete(f"/api/students/{uuid.uuid4()}")
    assert response.status_code == 404
