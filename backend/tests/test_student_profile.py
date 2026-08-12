"""Tests for the Phase 2 student profile + session context feature (6.2)."""

import os
import tempfile
import uuid
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.api.deps import get_provider
from app.config import get_settings
from app.database import get_engine
from app.llm import FakeProvider
from app.main import app

CANNED_RESPONSES = [
    "criteria output",
    "model output",
    "guided output",
    "guided coaching output",
    "independent task output",
    "Route to: check-structure",
    "coaching output",
    (
        "## Per-criterion levels\n"
        "- Understanding of text / ideas: **C** — note.\n"
        "- Analysis (how techniques create meaning): **C** — note.\n"
        "- Use of evidence: **C** — note.\n"
        "- Structure & cohesion: **C** — note.\n"
        "- Language & vocabulary: **C** — note.\n\n"
        "Strength: Something.\n"
        "Your 1–2 next steps to level up:\n"
        "  1. Do the thing.\n"
        "Self-check: how would you rate yourself against these criteria?\n"
    ),
]

ApiClient = tuple[TestClient, FakeProvider]


@pytest.fixture
def api_client(monkeypatch: pytest.MonkeyPatch) -> Generator[ApiClient, None, None]:
    """Boot the app against a temp SQLite DB with a canned FakeProvider."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_API_KEY", "")
    get_settings.cache_clear()
    get_engine.cache_clear()

    fake = FakeProvider(canned_responses=list(CANNED_RESPONSES))
    app.dependency_overrides[get_provider] = lambda: fake
    try:
        with TestClient(app) as client:
            yield client, fake
    finally:
        app.dependency_overrides.clear()
        get_engine().dispose()
        os.unlink(path)


def test_create_student_returns_profile(api_client: ApiClient) -> None:
    """POST /api/students creates a profile with focus_text_types persisted."""
    client, _ = api_client
    response = client.post(
        "/api/students",
        json={
            "name": "Alex",
            "year_level": 9,
            "curriculum": "QCAA",
            "focus_text_types": ["analytical", "persuasive"],
        },
    )
    assert response.status_code == 201
    data: dict[str, Any] = response.json()
    assert data["name"] == "Alex"
    assert data["year_level"] == 9
    assert data["curriculum"] == "QCAA"
    assert data["focus_text_types"] == ["analytical", "persuasive"]
    assert uuid.UUID(data["id"])


def test_list_and_get_students(api_client: ApiClient) -> None:
    client, _ = api_client
    created = client.post(
        "/api/students",
        json={"name": "Sam", "year_level": 8},
    ).json()

    listing = client.get("/api/students").json()
    assert len(listing) == 1
    assert listing[0]["id"] == created["id"]

    fetched = client.get(f"/api/students/{created['id']}").json()
    assert fetched["name"] == "Sam"
    assert fetched["focus_text_types"] == []


def test_update_student_profile(api_client: ApiClient) -> None:
    client, _ = api_client
    created = client.post(
        "/api/students",
        json={"name": "Jo", "year_level": 8},
    ).json()

    response = client.patch(
        f"/api/students/{created['id']}",
        json={"name": "Jo M.", "year_level": 10, "focus_text_types": ["persuasive"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Jo M."
    assert data["year_level"] == 10
    assert data["focus_text_types"] == ["persuasive"]


def test_session_with_student_id_inherits_profile(api_client: ApiClient) -> None:
    """A session started with student_id uses the student's year_level + focus."""
    client, fake = api_client
    student = client.post(
        "/api/students",
        json={
            "name": "Year 9 student",
            "year_level": 9,
            "focus_text_types": ["persuasive"],
        },
    ).json()

    response = client.post(
        "/api/sessions",
        json={"student_id": student["id"], "task_prompt": "Write a speech"},
    )
    assert response.status_code == 201
    assert response.json()["student_id"] == student["id"]

    # The first LLM call was set-success-criteria; its inputs should carry the
    # student's year_level (9) and focus text type (persuasive), not the
    # request defaults (8 / analytical).
    _system_prompt, messages = fake.calls[0]
    user_message = messages[0]["content"]
    assert "year_level: 9" in user_message
    assert "text_type: persuasive" in user_message
    assert "task_prompt: Write a speech" in user_message


def test_session_without_student_id_falls_back_to_request_defaults(
    api_client: ApiClient,
) -> None:
    """Without a student_id, the loop uses the request's year_level/text_type."""
    client, fake = api_client
    response = client.post(
        "/api/sessions",
        json={"year_level": "10", "text_type": "imaginative"},
    )
    assert response.status_code == 201
    user_message = fake.calls[0][1][0]["content"]
    assert "year_level: 10" in user_message
    assert "text_type: imaginative" in user_message


def test_session_with_unknown_student_id_returns_404(api_client: ApiClient) -> None:
    client, _ = api_client
    missing = uuid.uuid4()
    response = client.post("/api/sessions", json={"student_id": str(missing)})
    assert response.status_code == 404


def test_get_student_404_for_unknown_id(api_client: ApiClient) -> None:
    client, _ = api_client
    missing = uuid.uuid4()
    assert client.get(f"/api/students/{missing}").status_code == 404


def test_update_student_404_for_unknown_id(api_client: ApiClient) -> None:
    client, _ = api_client
    missing = uuid.uuid4()
    response = client.patch(
        f"/api/students/{missing}",
        json={"name": "Nobody"},
    )
    assert response.status_code == 404


def test_openapi_schema_includes_student_routes(api_client: ApiClient) -> None:
    client, _ = api_client
    paths = client.get("/openapi.json").json()["paths"]
    for expected in (
        "/api/students",
        "/api/students/{student_id}",
    ):
        assert expected in paths
