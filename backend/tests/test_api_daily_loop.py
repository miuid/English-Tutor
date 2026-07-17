"""End-to-end tests for the interactive daily-loop HTTP API."""

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

FEEDBACK_WITH_LEVELS = """## Per-criterion levels
- Understanding of text / ideas: **C** — a point exists but is vague.
- Analysis (how techniques create meaning): **D** — quote dropped in, effect not explained.
- Use of evidence: **C–** — relevant quote, loosely integrated.
- Structure & cohesion: **D+** — no link back.
- Language & vocabulary: **C** — clear but flat.

Strength: You chose a relevant simile.
Your 1–2 next steps to level up:
  1. Explain how the simile creates its effect — it lifts Analysis from D toward B.
Self-check: how would you rate yourself against these criteria?
"""

# One canned response per LLM call in a full loop:
# criteria, model, guided, guided follow-up, independent, diagnosis, coach, feedback.
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

    fake = FakeProvider(canned_responses=list(FULL_LOOP_RESPONSES))
    app.dependency_overrides[get_provider] = lambda: fake
    try:
        with TestClient(app) as client:
            yield client, fake
    finally:
        app.dependency_overrides.clear()
        get_engine().dispose()
        os.unlink(path)


def _start(client: TestClient) -> dict[str, Any]:
    response = client.post("/api/sessions", json={"task_prompt": "How does the poet present war?"})
    assert response.status_code == 201
    data: dict[str, Any] = response.json()
    return data


def _drive_full_loop(client: TestClient) -> dict[str, Any]:
    """start -> advances -> guided submit -> independent submit; return final submit body."""
    started = _start(client)
    assert started["stage"] == "start"
    assert started["ended"] is False
    assert len(started["turns"]) == 1
    opening_turn = started["turns"][0]
    assert opening_turn["kind"] == "tutor"
    assert opening_turn["skill"] == "set-success-criteria"
    assert opening_turn["text"] == "criteria output"
    session_id = started["id"]

    advance = client.post(f"/api/sessions/{session_id}/advance")
    assert advance.status_code == 200
    assert advance.json()["stage"] == "I do"
    assert advance.json()["turn"]["skill"] == "model-response"

    advance = client.post(f"/api/sessions/{session_id}/advance")
    assert advance.json()["stage"] == "we do"
    assert advance.json()["turn"]["skill"] == "guided-practice"

    guided = client.post(
        f"/api/sessions/{session_id}/submit", json={"text": "My guided attempt."}
    )
    assert guided.status_code == 200
    guided_body = guided.json()
    assert guided_body["stage"] == "we do"
    assert guided_body["ended"] is False
    assert guided_body["feedback"] is None
    assert [turn["kind"] for turn in guided_body["turns"]] == ["student", "tutor"]
    assert guided_body["turns"][0]["text"] == "My guided attempt."
    assert guided_body["turns"][1]["skill"] == "guided-practice"
    assert guided_body["turns"][1]["text"] == "guided coaching output"

    advance = client.post(f"/api/sessions/{session_id}/advance")
    assert advance.json()["stage"] == "you do"
    assert advance.json()["turn"]["skill"] == "independent-task"

    final = client.post(
        f"/api/sessions/{session_id}/submit", json={"text": "War is bad."}
    )
    assert final.status_code == 200
    data: dict[str, Any] = final.json()
    return data


def test_full_session_over_http(api_client: ApiClient) -> None:
    client, _ = api_client
    body = _drive_full_loop(client)

    assert body["stage"] == "ended"
    assert body["ended"] is True
    # submission + diagnosis + coach + feedback turns
    assert [turn["kind"] for turn in body["turns"]] == ["student", "tutor", "tutor", "tutor"]
    skills = [turn["skill"] for turn in body["turns"]]
    assert skills[1:] == ["diagnose-errors", "check-structure", "give-feedback"]

    feedback = body["feedback"]
    assert feedback is not None
    levels = {score["criterion_name"]: score["level"] for score in feedback["rubric_scores"]}
    assert len(levels) == 5
    assert levels["Understanding of text / ideas"] == "C"
    assert levels["Analysis (how techniques create meaning)"] == "D"
    assert levels["Use of evidence"] == "C-"  # en dash normalised
    assert levels["Structure & cohesion"] == "D+"
    assert levels["Language & vocabulary"] == "C"


def test_get_session_rebuilds_conversation(api_client: ApiClient) -> None:
    client, _ = api_client
    body = _drive_full_loop(client)
    session_id = body["session_id"]

    response = client.get(f"/api/sessions/{session_id}")
    assert response.status_code == 200
    state = response.json()
    assert state["stage"] == "ended"
    assert state["ended"] is True
    # criteria, model, guided, guided submission, guided follow-up,
    # independent, independent submission, diagnosis, coach, feedback
    assert len(state["turns"]) == 10
    kinds = [turn["kind"] for turn in state["turns"]]
    assert kinds == [
        "tutor",
        "tutor",
        "tutor",
        "student",
        "tutor",
        "tutor",
        "student",
        "tutor",
        "tutor",
        "tutor",
    ]
    task_types = [turn["task_type"] for turn in state["turns"]]
    assert task_types == [
        "criteria",
        "model",
        "guided",
        "submission",
        "guided",
        "independent",
        "submission",
        "diagnosis",
        "coach",
        "feedback",
    ]


def test_progress_endpoint_returns_rubric_rows(api_client: ApiClient) -> None:
    client, _ = api_client
    body = _drive_full_loop(client)
    session_id = body["session_id"]
    student_id = client.get(f"/api/sessions/{session_id}").json()["student_id"]

    response = client.get(f"/api/students/{student_id}/progress")
    assert response.status_code == 200
    progress = response.json()
    assert progress["student_id"] == student_id
    assert len(progress["scores"]) == 5
    by_name = {score["criterion_name"]: score for score in progress["scores"]}
    assert by_name["Language & vocabulary"]["note"] == "clear but flat."
    for score in progress["scores"]:
        assert score["session_id"] == body["session_id"]
        assert score["feedback_id"] == body["feedback"]["id"]
        assert score["scored_at"]


def test_openapi_schema_renders(api_client: ApiClient) -> None:
    client, _ = api_client
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    for expected in (
        "/api/sessions",
        "/api/sessions/{session_id}",
        "/api/sessions/{session_id}/advance",
        "/api/sessions/{session_id}/submit",
        "/api/students/{student_id}/progress",
    ):
        assert expected in paths


def test_unknown_ids_return_404(api_client: ApiClient) -> None:
    client, _ = api_client
    missing = uuid.uuid4()
    assert client.get(f"/api/sessions/{missing}").status_code == 404
    assert client.post(f"/api/sessions/{missing}/advance").status_code == 404
    assert (
        client.post(f"/api/sessions/{missing}/submit", json={"text": "hi"}).status_code == 404
    )
    assert client.get(f"/api/students/{missing}/progress").status_code == 404


def test_submit_before_guided_stage_conflicts(api_client: ApiClient) -> None:
    client, _ = api_client
    started = _start(client)
    session_id = started["id"]

    # stage "start": no student input expected yet
    response = client.post(f"/api/sessions/{session_id}/submit", json={"text": "too early"})
    assert response.status_code == 409

    # stage "I do": still no input expected
    assert client.post(f"/api/sessions/{session_id}/advance").status_code == 200
    response = client.post(f"/api/sessions/{session_id}/submit", json={"text": "still early"})
    assert response.status_code == 409


def test_advance_at_independent_stage_conflicts(api_client: ApiClient) -> None:
    client, _ = api_client
    started = _start(client)
    session_id = started["id"]
    for _ in range(3):
        assert client.post(f"/api/sessions/{session_id}/advance").status_code == 200

    # stage "you do": the tutor is waiting for the student's text
    response = client.post(f"/api/sessions/{session_id}/advance")
    assert response.status_code == 409


def test_ended_session_rejects_advance_and_submit(
    api_client: ApiClient,
) -> None:
    client, _ = api_client
    body = _drive_full_loop(client)
    session_id = body["session_id"]

    assert client.post(f"/api/sessions/{session_id}/advance").status_code == 409
    assert (
        client.post(f"/api/sessions/{session_id}/submit", json={"text": "more"}).status_code
        == 409
    )


def test_cors_allows_dev_origins(api_client: ApiClient) -> None:
    client, _ = api_client
    response = client.options(
        "/api/sessions",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_start_session_without_task_prompt(api_client: ApiClient) -> None:
    """The school-task field is optional: an empty body still starts the loop."""
    client, fake = api_client
    response = client.post("/api/sessions", json={})
    assert response.status_code == 201
    data = response.json()
    assert data["stage"] == "start"
    assert data["ended"] is False
    assert data["learning_intention"] is None
    assert len(data["turns"]) == 1
    assert data["turns"][0]["skill"] == "set-success-criteria"
    # The skill still received a usable fallback prompt.
    user_message = fake.calls[0][1][0]["content"]
    assert "task_prompt: General analytical writing practice" in user_message


def test_start_session_with_context(api_client: ApiClient) -> None:
    """Optional context is threaded into the set-success-criteria skill inputs."""
    client, fake = api_client
    response = client.post(
        "/api/sessions",
        json={"task_prompt": "Analyse a poem", "context": "Due Friday, one paragraph"},
    )
    assert response.status_code == 201
    user_message = fake.calls[0][1][0]["content"]
    assert "task_prompt: Analyse a poem" in user_message
    assert "context: Due Friday, one paragraph" in user_message
