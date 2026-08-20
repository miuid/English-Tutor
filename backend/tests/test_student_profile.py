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
    "retrieval warm-up output",
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


BASELINE_REPORT = (
    "## Per-criterion levels\n"
    "- Understanding of text / ideas: **C** — sound literal understanding of the character.\n"
    "- Analysis (how techniques create meaning): **D** — asserts bravery, never explains how.\n"
    "- Use of evidence: **D** — one vague gesture at technique, no embedded quote.\n"
    "- Structure & cohesion: **C** — functional intro/body/conclusion.\n"
    "- Language & vocabulary: **C-** — clear but flat and repetitive.\n\n"
    "Starting strength: He picked one genuine reason — bravery — and stayed on it.\n\n"
    "## Ranked weaknesses\n"
    "1. Thin analysis — says what, never how the writing does it.\n"
    "2. Evidence is waved at, not used.\n\n"
    "## Recommended focus loop\n"
    "Start with: check-structure on analytical writing — the how is the fastest lever.\n"
    "First session: tomorrow we'll watch how a strong paragraph explains a quote.\n"
)


@pytest.fixture
def baseline_client(monkeypatch: pytest.MonkeyPatch) -> Generator[ApiClient, None, None]:
    """Boot the app with a canned baseline-assessment report."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_API_KEY", "")
    get_settings.cache_clear()
    get_engine.cache_clear()

    fake = FakeProvider(canned_responses=[BASELINE_REPORT])
    app.dependency_overrides[get_provider] = lambda: fake
    try:
        with TestClient(app) as client:
            yield client, fake
    finally:
        app.dependency_overrides.clear()
        get_engine().dispose()
        os.unlink(path)


def test_baseline_writes_day0_rubric_scores(baseline_client: ApiClient) -> None:
    """POST /baseline runs the skill and persists day-0 rubric scores."""
    client, _ = baseline_client
    student = client.post(
        "/api/students",
        json={"name": "New starter", "year_level": 8},
    ).json()

    response = client.post(
        f"/api/students/{student['id']}/baseline",
        json={"text": "Harry Potter is memorable because he is brave..."},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["session_id"]
    assert "Ranked weaknesses" in data["report"]
    assert "Recommended focus loop" in data["report"]
    assert "check-structure" in data["report"]

    scores = data["feedback"]["rubric_scores"]
    assert len(scores) == 5
    assert scores[0]["criterion_name"] == "Understanding of text / ideas"
    assert scores[0]["level"] == "C"
    assert scores[1]["criterion_name"] == "Analysis (how techniques create meaning)"
    assert scores[1]["level"] == "D"

    # Day-0 rows are visible to the progress endpoint under the new student.
    progress = client.get(f"/api/students/{student['id']}/progress").json()
    assert len(progress["scores"]) == 5
    assert [s["criterion_name"] for s in progress["scores"]] == [
        s["criterion_name"] for s in scores
    ]


def test_baseline_uses_profile_and_shared_pack(baseline_client: ApiClient) -> None:
    """The baseline prompt inherits the profile and cites the shared guide."""
    client, fake = baseline_client
    student = client.post(
        "/api/students",
        json={"name": "Year 9 starter", "year_level": 9, "focus_text_types": ["persuasive"]},
    ).json()

    response = client.post(
        f"/api/students/{student['id']}/baseline",
        json={"text": "School should start later because..."},
    )
    assert response.status_code == 201

    system_prompt, messages = fake.calls[0]
    assert "baseline-guide.md" in system_prompt
    user_message = messages[0]["content"]
    assert "year_level: 9" in user_message
    assert "text_type: persuasive" in user_message  # profile focus wins

    # The baseline session is a short, already-ended record — not a live loop.
    session = client.get(f"/api/sessions/{response.json()['session_id']}").json()
    assert session["ended"] is True
    kinds = {(turn["kind"], turn["task_type"]) for turn in session["turns"]}
    assert ("student", "submission") in kinds
    assert ("tutor", "baseline") in kinds


def test_baseline_unknown_student_returns_404(baseline_client: ApiClient) -> None:
    client, _ = baseline_client
    response = client.post(
        f"/api/students/{uuid.uuid4()}/baseline",
        json={"text": "Some writing."},
    )
    assert response.status_code == 404


def test_create_student_defaults_coach_tone_to_warm(api_client: ApiClient) -> None:
    client, _ = api_client
    response = client.post("/api/students", json={"name": "Kai", "year_level": 8})

    assert response.status_code == 201
    assert response.json()["coach_tone"] == "warm"


def test_create_and_update_coach_tone(api_client: ApiClient) -> None:
    client, _ = api_client
    created = client.post(
        "/api/students",
        json={"name": "Kai", "year_level": 8, "coach_tone": "strict"},
    )
    assert created.status_code == 201
    assert created.json()["coach_tone"] == "strict"

    updated = client.patch(
        f"/api/students/{created.json()['id']}",
        json={"coach_tone": "humorous"},
    )
    assert updated.status_code == 200
    data = updated.json()
    assert data["coach_tone"] == "humorous"
    assert data["name"] == "Kai"  # untouched fields preserved

    fetched = client.get(f"/api/students/{data['id']}")
    assert fetched.json()["coach_tone"] == "humorous"


def test_coach_tone_rejects_invalid_value(api_client: ApiClient) -> None:
    client, _ = api_client
    created = client.post(
        "/api/students",
        json={"name": "Kai", "year_level": 8, "coach_tone": "sassy"},
    )
    assert created.status_code == 422

    valid = client.post("/api/students", json={"name": "Kai", "year_level": 8})
    assert valid.status_code == 201
    updated = client.patch(
        f"/api/students/{valid.json()['id']}",
        json={"coach_tone": "sassy"},
    )
    assert updated.status_code == 422
