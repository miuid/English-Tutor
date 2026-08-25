"""Tests for privacy-safe telemetry and the feedback package (ISS-022).

The core guarantee under test: the feedback package is safe to email — it
must never contain student writing, task prompts, feedback prose, rubric
notes, LLM prompt/completion text, the student's name, or credentials.
"""

import json
import uuid
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_provider
from app.config import Settings, get_settings
from app.database import get_engine
from app.llm import FakeProvider
from app.main import app
from app.models import (
    Attempt,
    Feedback,
    InteractionLog,
    RubricScore,
    Session,
    Skill,
    Student,
)
from app.telemetry import (
    PACKAGE_FORMAT,
    PACKAGE_VERSION,
    build_feedback_package,
    build_telemetry,
)

# Distinctive markers planted in every content-bearing field. If any of
# these shows up in the serialized package, the privacy boundary broke.
MARKER_NAME = "Zoeprivate-Name"
MARKER_ESSAY = "SECRET-ESSAY-TEXT about my dog"
MARKER_PROMPT = "SECRET-TASK-PROMPT stimulus"
MARKER_FEEDBACK = "SECRET-FEEDBACK-PROSE strength"
MARKER_NOTE = "SECRET-RUBRIC-NOTE detail"
MARKER_LOG_INPUT = "SECRET-LLM-INPUT prompt body"
MARKER_LOG_OUTPUT = "SECRET-LLM-OUTPUT completion body"
MARKER_INTENTION = "SECRET-LEARNING-INTENTION"
ALL_MARKERS = [
    MARKER_NAME,
    MARKER_ESSAY,
    MARKER_PROMPT,
    MARKER_FEEDBACK,
    MARKER_NOTE,
    MARKER_LOG_INPUT,
    MARKER_LOG_OUTPUT,
    MARKER_INTENTION,
]


def _seed_student_with_content(db: DBSession) -> Student:
    """Create one student with content planted in every sensitive field."""
    student = Student(
        name=MARKER_NAME,
        year_level=8,
        curriculum="QCAA",
        focus_text_types=["analytical"],
        weekly_goal=4,
        coach_tone="warm",
    )
    db.add(student)
    db.flush()

    skill = Skill(name="give-feedback", version="1.0.0", loop_stage="end")
    db.add(skill)
    db.flush()

    session = Session(
        student_id=student.id,
        stage="ended",
        learning_intention=MARKER_INTENTION,
        time_spent_seconds=600,
    )
    db.add(session)
    db.flush()

    attempt = Attempt(
        session_id=session.id,
        student_id=student.id,
        skill_id=skill.id,
        task_type="independent",
        mode="practice",
        task_prompt=MARKER_PROMPT,
        student_text=MARKER_ESSAY,
    )
    db.add(attempt)
    db.flush()

    feedback = Feedback(
        attempt_id=attempt.id,
        strength=MARKER_FEEDBACK,
        next_steps="next steps",
    )
    db.add(feedback)
    db.flush()

    db.add(
        RubricScore(
            feedback_id=feedback.id,
            criterion_name="Analysis",
            level="C",
            note=MARKER_NOTE,
        )
    )
    db.add(
        InteractionLog(
            session_id=session.id,
            skill_id=skill.id,
            model="fake-model",
            input=MARKER_LOG_INPUT,
            output=MARKER_LOG_OUTPUT,
        )
    )
    # A second call with an empty completion — the classic beta symptom.
    db.add(
        InteractionLog(
            session_id=session.id,
            skill_id=skill.id,
            model="fake-model",
            input="prompt",
            output="",
        )
    )
    db.commit()
    db.refresh(student)
    return student


def _settings() -> Settings:
    return Settings(
        llm_provider="fake",
        llm_model="kimi-k3",
        llm_stage_models={"end": "kimi-k3-mini"},
        database_url="sqlite:///./english_tutor.db",
        session_time_limit_minutes=15,
    )


def test_telemetry_aggregates_counts_only(db_session: DBSession) -> None:
    student = _seed_student_with_content(db_session)
    telemetry = build_telemetry(db_session, student)

    assert telemetry["sessions_total"] == 1
    assert telemetry["sessions_completed"] == 0  # ended_at not set
    assert telemetry["practice_seconds_total"] == 600
    assert telemetry["attempts_total"] == 1
    assert telemetry["attempts_by_mode"] == {"practice": 1}
    assert telemetry["attempts_by_skill"] == {"give-feedback": 1}
    assert telemetry["feedback_total"] == 1
    assert telemetry["rubric_scores_total"] == 1
    assert telemetry["llm_calls_total"] == 2
    assert telemetry["llm_calls_by_model"] == {"fake-model": 2}
    assert telemetry["llm_calls_by_skill"] == {"give-feedback": 2}
    assert telemetry["llm_empty_output_calls"] == 1
    assert telemetry["first_activity_at"] is not None
    assert telemetry["last_activity_at"] is not None


def test_telemetry_empty_student(db_session: DBSession) -> None:
    student = Student(name="New", year_level=9, curriculum="QCAA")
    db_session.add(student)
    db_session.commit()
    telemetry = build_telemetry(db_session, student)
    assert telemetry["sessions_total"] == 0
    assert telemetry["attempts_total"] == 0
    assert telemetry["llm_calls_total"] == 0
    assert telemetry["first_activity_at"] is None
    assert telemetry["last_activity_at"] is None


def test_feedback_package_shape_and_metadata(db_session: DBSession) -> None:
    student = _seed_student_with_content(db_session)
    package = build_feedback_package(db_session, student, _settings())

    assert package["format"] == PACKAGE_FORMAT
    assert package["version"] == PACKAGE_VERSION
    assert package["generated_at"]

    config = package["config"]
    assert config["llm_provider"] == "fake"
    assert config["llm_model"] == "kimi-k3"
    assert config["llm_stage_models"] == {"end": "kimi-k3-mini"}
    assert config["session_time_limit_minutes"] == 15
    assert config["database"] == "sqlite"

    context = package["student_context"]
    assert context["year_level"] == 8
    assert context["curriculum"] == "QCAA"
    assert context["focus_text_types"] == ["analytical"]

    env = package["environment"]
    assert env["skills_loaded"] == 1
    assert env["skill_names"] == ["give-feedback"]

    assert package["telemetry"]["llm_empty_output_calls"] == 1

    assert len(package["recent_sessions"]) == 1
    recent_session = package["recent_sessions"][0]
    assert recent_session["stage"] == "ended"
    assert recent_session["time_spent_seconds"] == 600
    assert "learning_intention" not in recent_session

    assert len(package["recent_interactions"]) == 2
    for entry in package["recent_interactions"]:
        assert entry["model"] == "fake-model"
        assert entry["skill"] == "give-feedback"
        assert set(entry) == {"created_at", "model", "skill", "input_chars", "output_chars"}
    # Lengths are reported, content is not.
    lengths = sorted(
        (e["input_chars"], e["output_chars"]) for e in package["recent_interactions"]
    )
    assert lengths == [(len("prompt"), 0), (len(MARKER_LOG_INPUT), len(MARKER_LOG_OUTPUT))]


def test_feedback_package_never_contains_student_content(
    db_session: DBSession,
) -> None:
    """Privacy regression: no marker string may survive serialization."""
    student = _seed_student_with_content(db_session)
    package = build_feedback_package(db_session, student, _settings())
    blob = json.dumps(package)
    for marker in ALL_MARKERS:
        assert marker not in blob, f"privacy leak: {marker!r} found in package"
    # No credential or secret-bearing keys anywhere.
    assert "llm_api_key" not in blob
    assert "api_key" not in blob
    # The student's full name is excluded even though other profile
    # context (year level, curriculum) is present.
    assert student.name not in blob


def test_feedback_package_has_no_student_name_in_telemetry_endpoint_shape(
    db_session: DBSession,
) -> None:
    """Telemetry alone is also free of all content markers."""
    student = _seed_student_with_content(db_session)
    blob = json.dumps(build_telemetry(db_session, student))
    for marker in ALL_MARKERS:
        assert marker not in blob


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    """Boot the app against a temp SQLite DB with the fake provider."""
    import os
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{path}")
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_API_KEY", "")
    get_settings.cache_clear()
    get_engine.cache_clear()

    app.dependency_overrides[get_provider] = lambda: FakeProvider(
        canned_responses=["ok"]
    )
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    os.unlink(path)


def _create_student(client: TestClient) -> str:
    response = client.post(
        "/api/students",
        json={"name": "Alex", "year_level": 8, "curriculum": "QCAA"},
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def test_telemetry_endpoint(client: TestClient) -> None:
    student_id = _create_student(client)
    response = client.get(f"/api/students/{student_id}/telemetry")
    assert response.status_code == 200
    body = response.json()
    assert body["student_id"] == student_id
    telemetry = body["telemetry"]
    assert telemetry["sessions_total"] == 0
    assert telemetry["attempts_total"] == 0


def test_telemetry_endpoint_404(client: TestClient) -> None:
    response = client.get(f"/api/students/{uuid.uuid4()}/telemetry")
    assert response.status_code == 404


def test_feedback_package_endpoint_downloads_json(client: TestClient) -> None:
    student_id = _create_student(client)
    response = client.get(f"/api/students/{student_id}/feedback-package")
    assert response.status_code == 200
    disposition = response.headers["content-disposition"]
    assert "attachment" in disposition
    assert "feedback-package" in disposition
    body = response.json()
    assert body["format"] == PACKAGE_FORMAT
    assert body["config"]["llm_provider"] == "fake"
    assert body["student_context"]["year_level"] == 8
    # New profile: name never leaves the machine in the package.
    assert "Alex" not in response.text


def test_feedback_package_endpoint_404(client: TestClient) -> None:
    response = client.get(f"/api/students/{uuid.uuid4()}/feedback-package")
    assert response.status_code == 404
