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
# retrieval, criteria, model, guided, guided follow-up, independent, diagnosis,
# coach, feedback.
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
    # Retrieval opens the loop (step 1), then success criteria.
    assert len(started["turns"]) == 2
    opening_turn = started["turns"][0]
    assert opening_turn["kind"] == "tutor"
    assert opening_turn["skill"] == "spaced-review"
    assert opening_turn["task_type"] == "retrieval"
    assert opening_turn["text"] == "retrieval warm-up output"
    criteria_turn = started["turns"][1]
    assert criteria_turn["kind"] == "tutor"
    assert criteria_turn["skill"] == "set-success-criteria"
    assert criteria_turn["text"] == "criteria output"
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
    # retrieval, criteria, model, guided, guided submission, guided follow-up,
    # independent, independent submission, diagnosis, coach, feedback
    assert len(state["turns"]) == 11
    kinds = [turn["kind"] for turn in state["turns"]]
    assert kinds == [
        "tutor",
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
        "retrieval",
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


PERSUASIVE_FEEDBACK_WITH_LEVELS = """## Per-criterion levels
- Position & ideas: **C** — a position with relevant reasons.
- Argument & evidence: **D** — reasons listed, elaboration thin.
- Audience & voice: **C** — generally suits the audience.
- Structure & cohesion: **C** — functional intro/body/conclusion.
- Language & vocabulary: **D+** — vague, repetitive word choices.

Strength: You state a clear position early.
Your 1–2 next steps to level up:
  1. Develop one reason — why it holds and why your audience should care.
Self-check: how would you rate yourself against these criteria?
"""

# Persuasive loop: same shape as the analytical loop, but the diagnosis routes
# to the persuasive coaching skill (strengthen-argument, ISS-005).
PERSUASIVE_LOOP_RESPONSES = [
    "retrieval warm-up output",
    "criteria output",
    "model output",
    "guided output",
    "guided coaching output",
    "independent task output",
    "Route to: strengthen-argument",
    "argument coaching output",
    PERSUASIVE_FEEDBACK_WITH_LEVELS,
]


def test_year_9_session_runs_loop_and_persists_scores(api_client: ApiClient) -> None:
    """A year_level=9 student runs the full loop over HTTP with Year 9 packs."""
    client, fake = api_client

    created = client.post(
        "/api/students",
        json={"name": "Year 9 Student", "year_level": 9, "curriculum": "QCAA"},
    )
    assert created.status_code == 201
    student_id = created.json()["id"]

    started = client.post(
        "/api/sessions",
        json={
            "student_id": student_id,
            "task_prompt": "How does Shakespeare position the reader in Macbeth?",
        },
    )
    assert started.status_code == 201
    session_id = started.json()["id"]

    assert client.post(f"/api/sessions/{session_id}/advance").status_code == 200
    assert client.post(f"/api/sessions/{session_id}/advance").status_code == 200
    assert (
        client.post(
            f"/api/sessions/{session_id}/submit", json={"text": "My guided attempt."}
        ).status_code
        == 200
    )
    assert client.post(f"/api/sessions/{session_id}/advance").status_code == 200
    final = client.post(
        f"/api/sessions/{session_id}/submit", json={"text": "Macbeth is ambitious."}
    )
    assert final.status_code == 200
    body = final.json()
    assert body["ended"] is True

    # Rubric scores persist for the graded Year 9 attempt.
    feedback = body["feedback"]
    assert feedback is not None
    levels = {score["criterion_name"]: score["level"] for score in feedback["rubric_scores"]}
    assert len(levels) == 5
    assert levels["Analysis (how techniques create meaning)"] == "D"

    # The loop ran against the exact analytical/year-9-10 packs: Year 9
    # descriptors are cited in the pack-bearing prompts (criteria, independent,
    # diagnosis, coach, feedback) and the feedback prompt carries the Year 9
    # rubric language; no degradation note was appended to any tutor turn.
    # spaced-review (call 0) is shared-only by design, so it bears no pack.
    assert len(fake.calls) == 9
    for index in (1, 5, 6, 7, 8):
        assert "Year 9" in fake.calls[index][0]
    assert "discriminating thesis" in fake.calls[8][0]
    state = client.get(f"/api/sessions/{session_id}").json()
    tutor_turns = [turn for turn in state["turns"] if turn["kind"] == "tutor"]
    for turn in tutor_turns:
        assert "_Note: no dedicated references" not in turn["text"]


def test_persuasive_session_runs_loop_and_persists_scores(api_client: ApiClient) -> None:
    """A student with a persuasive focus runs the full loop over HTTP.

    The profile's focus_text_types[0] resolves text_type=persuasive on every
    stage, so every pack-bearing prompt cites the persuasive/year-8 packs; the
    diagnosis routes to strengthen-argument; rubric scores persist for the
    graded persuasive attempt.
    """
    client, fake = api_client
    fake.canned_responses = list(PERSUASIVE_LOOP_RESPONSES)

    created = client.post(
        "/api/students",
        json={
            "name": "Persuasive Student",
            "year_level": 8,
            "curriculum": "QCAA",
            "focus_text_types": ["persuasive"],
        },
    )
    assert created.status_code == 201
    student_id = created.json()["id"]

    started = client.post(
        "/api/sessions",
        json={
            "student_id": student_id,
            "task_prompt": "Should school uniforms be compulsory?",
        },
    )
    assert started.status_code == 201
    session_id = started.json()["id"]

    assert client.post(f"/api/sessions/{session_id}/advance").status_code == 200
    assert client.post(f"/api/sessions/{session_id}/advance").status_code == 200
    assert (
        client.post(
            f"/api/sessions/{session_id}/submit", json={"text": "My guided attempt."}
        ).status_code
        == 200
    )
    assert client.post(f"/api/sessions/{session_id}/advance").status_code == 200
    final = client.post(
        f"/api/sessions/{session_id}/submit",
        json={"text": "Uniforms are unfair. Everyone knows it."},
    )
    assert final.status_code == 200
    body = final.json()
    assert body["ended"] is True

    # The persuasive diagnosis routed to the persuasive coaching skill.
    skills = [turn["skill"] for turn in body["turns"]]
    assert skills[1:] == ["diagnose-errors", "strengthen-argument", "give-feedback"]
    assert body["turns"][2]["text"] == "argument coaching output"

    # Rubric scores persist for the graded persuasive attempt.
    feedback = body["feedback"]
    assert feedback is not None
    levels = {score["criterion_name"]: score["level"] for score in feedback["rubric_scores"]}
    assert len(levels) == 5
    assert levels["Position & ideas"] == "C"
    assert levels["Argument & evidence"] == "D"

    # The loop ran against the exact persuasive/year-8 packs: pack-bearing
    # prompts (criteria, independent, diagnosis, coach, feedback) cite the
    # persuasive references and the feedback prompt carries the persuasive
    # rubric language; no degradation note was appended to any tutor turn.
    # spaced-review (call 0) is shared-only by design, so it bears no pack.
    assert len(fake.calls) == 9
    for index in (1, 5, 6, 7, 8):
        assert "persuasive" in fake.calls[index][0]
    assert "Position & ideas" in fake.calls[8][0]
    state = client.get(f"/api/sessions/{session_id}").json()
    tutor_turns = [turn for turn in state["turns"] if turn["kind"] == "tutor"]
    for turn in tutor_turns:
        assert "_Note: no dedicated references" not in turn["text"]


IMAGINATIVE_FEEDBACK_WITH_LEVELS = """## Per-criterion levels
- Story & tension: **C** — a clear complication developed and resolved.
- Character & setting: **C** — character and setting established.
- Showing & voice: **D** — key moment told; emotions named.
- Language & vocabulary: **C** — clear, mostly appropriate choices.
- Structure & cohesion: **C** — functional beginning/middle/end.

Strength: Your opening hooks the reader.
Your 1–2 next steps to level up:
  1. Slow down the key moment and show it — one scene, concrete detail.
Self-check: how would you rate yourself against these criteria?
"""

# Imaginative loop: same shape as the persuasive loop, but the diagnosis
# routes to the imaginative coaching skill (craft-voice, ISS-008).
IMAGINATIVE_LOOP_RESPONSES = [
    "retrieval warm-up output",
    "criteria output",
    "model output",
    "guided output",
    "guided coaching output",
    "independent task output",
    "Route to: craft-voice",
    "voice coaching output",
    IMAGINATIVE_FEEDBACK_WITH_LEVELS,
]


def test_imaginative_session_runs_loop_and_persists_scores(api_client: ApiClient) -> None:
    """A student with an imaginative focus runs the full loop over HTTP.

    The profile's focus_text_types[0] resolves text_type=imaginative on every
    stage, so every pack-bearing prompt cites the imaginative/year-8 packs; the
    diagnosis routes to craft-voice; rubric scores persist for the graded
    imaginative attempt.
    """
    client, fake = api_client
    fake.canned_responses = list(IMAGINATIVE_LOOP_RESPONSES)

    created = client.post(
        "/api/students",
        json={
            "name": "Imaginative Student",
            "year_level": 8,
            "curriculum": "QCAA",
            "focus_text_types": ["imaginative"],
        },
    )
    assert created.status_code == 201
    student_id = created.json()["id"]

    started = client.post(
        "/api/sessions",
        json={
            "student_id": student_id,
            "task_prompt": "Write the opening of a story about a noise in the dark.",
        },
    )
    assert started.status_code == 201
    session_id = started.json()["id"]

    assert client.post(f"/api/sessions/{session_id}/advance").status_code == 200
    assert client.post(f"/api/sessions/{session_id}/advance").status_code == 200
    assert (
        client.post(
            f"/api/sessions/{session_id}/submit", json={"text": "My guided attempt."}
        ).status_code
        == 200
    )
    assert client.post(f"/api/sessions/{session_id}/advance").status_code == 200
    final = client.post(
        f"/api/sessions/{session_id}/submit",
        json={"text": "The noise was scary. I was very afraid."},
    )
    assert final.status_code == 200
    body = final.json()
    assert body["ended"] is True

    # The imaginative diagnosis routed to the imaginative coaching skill.
    skills = [turn["skill"] for turn in body["turns"]]
    assert skills[1:] == ["diagnose-errors", "craft-voice", "give-feedback"]
    assert body["turns"][2]["text"] == "voice coaching output"

    # Rubric scores persist for the graded imaginative attempt.
    feedback = body["feedback"]
    assert feedback is not None
    levels = {score["criterion_name"]: score["level"] for score in feedback["rubric_scores"]}
    assert len(levels) == 5
    assert levels["Story & tension"] == "C"
    assert levels["Showing & voice"] == "D"

    # The loop ran against the exact imaginative/year-8 packs: pack-bearing
    # prompts (criteria, independent, diagnosis, coach, feedback) cite the
    # imaginative references and the feedback prompt carries the imaginative
    # rubric language; no degradation note was appended to any tutor turn.
    # spaced-review (call 0) is shared-only by design, so it bears no pack.
    assert len(fake.calls) == 9
    for index in (1, 5, 6, 7, 8):
        assert "imaginative" in fake.calls[index][0]
    assert "Story & tension" in fake.calls[8][0]
    state = client.get(f"/api/sessions/{session_id}").json()
    tutor_turns = [turn for turn in state["turns"] if turn["kind"] == "tutor"]
    for turn in tutor_turns:
        assert "_Note: no dedicated references" not in turn["text"]


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
        "/api/sessions/{session_id}/pause",
        "/api/sessions/{session_id}/resume",
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
    assert len(data["turns"]) == 2
    assert data["turns"][0]["skill"] == "spaced-review"
    assert data["turns"][1]["skill"] == "set-success-criteria"
    # Both opening skills still received a usable fallback prompt.
    retrieval_message = fake.calls[0][1][0]["content"]
    assert "task_prompt: General analytical writing practice" in retrieval_message
    criteria_message = fake.calls[1][1][0]["content"]
    assert "task_prompt: General analytical writing practice" in criteria_message


def test_start_session_with_context(api_client: ApiClient) -> None:
    """Optional context is threaded into the opening skill inputs."""
    client, fake = api_client
    response = client.post(
        "/api/sessions",
        json={"task_prompt": "Analyse a poem", "context": "Due Friday, one paragraph"},
    )
    assert response.status_code == 201
    retrieval_message = fake.calls[0][1][0]["content"]
    assert "task_prompt: Analyse a poem" in retrieval_message
    assert "context: Due Friday, one paragraph" in retrieval_message
    criteria_message = fake.calls[1][1][0]["content"]
    assert "task_prompt: Analyse a poem" in criteria_message
    assert "context: Due Friday, one paragraph" in criteria_message


def test_retrieval_cold_start_when_no_history(api_client: ApiClient) -> None:
    """A first-ever session's retrieval call gets the cold-start digest."""
    client, fake = api_client
    started = _start(client)
    assert started["turns"][0]["skill"] == "spaced-review"
    retrieval_message = fake.calls[0][1][0]["content"]
    assert "review_history:" in retrieval_message
    assert "No prior sessions" in retrieval_message


def test_retrieval_uses_rubric_and_coach_history(api_client: ApiClient) -> None:
    """The next session's retrieval items are generated from real history.

    After one full loop, the student's rubric_score and coaching history feed
    the spaced-review digest: the retrieval call's user message carries the
    weakest-first criterion levels, the days-since counter, and the recently
    coached skill.
    """
    client, fake = api_client
    _drive_full_loop(client)
    calls_after_first_loop = len(fake.calls)

    started = _start(client)
    assert started["turns"][0]["skill"] == "spaced-review"

    retrieval_message = fake.calls[calls_after_first_loop][1][0]["content"]
    assert "review_history: Days since last session: 0" in retrieval_message
    # Latest criterion levels from the first loop's feedback, weakest first.
    assert "- Analysis (how techniques create meaning): D" in retrieval_message
    assert "- Structure & cohesion: D+" in retrieval_message
    # The first loop's coach turn (check-structure) is the recent coaching.
    assert "Recently coached: check-structure" in retrieval_message
