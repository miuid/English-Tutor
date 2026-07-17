"""Tests for the session orchestrator."""

from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session as SqlSession

from app.llm import FakeProvider
from app.models import Attempt, Feedback, RubricScore, Student
from app.sessions.orchestrator import SessionOrchestrator
from app.skills import load_skills
from app.skills.executor import SkillExecutionService
from app.skills.sync import sync_skills

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


@pytest.mark.asyncio
async def test_run_daily_loop_creates_session_with_attempts(db_session: SqlSession) -> None:
    sync_skills(db_session)

    student = Student(name="Test Student", year_level=8, curriculum="QCAA")
    db_session.add(student)
    db_session.flush()

    skills = {s.name: s for s in load_skills(SKILLS_DIR)}
    fake = FakeProvider(
        canned_responses=[
            "criteria output",
            "model output",
            "guided output",
            "independent task",
            "Route to: check-structure",
            "coaching output",
            "feedback output",
        ]
    )
    executor = SkillExecutionService(provider=fake)
    orchestrator = SessionOrchestrator(db_session, executor, skills)

    session = await orchestrator.run_daily_loop(
        student_id=student.id,
        year_level="8",
        text_type="analytical",
        task_prompt="How does the poet present war?",
        student_text="War is bad.",
    )

    assert session.student_id == student.id
    assert session.ended_at is not None

    attempts = (
        db_session.execute(select(Attempt).where(Attempt.session_id == session.id)).scalars().all()
    )
    assert len(attempts) == 7
    task_types = {a.task_type for a in attempts}
    assert task_types == {
        "criteria",
        "model",
        "guided",
        "independent",
        "diagnosis",
        "coach",
        "feedback",
    }

    feedback = (
        db_session.execute(
            select(Feedback).where(Feedback.attempt_id.in_([a.id for a in attempts]))
        )
        .scalars()
        .all()
    )
    assert len(feedback) == 1


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


@pytest.mark.asyncio
async def test_run_daily_loop_persists_rubric_scores(db_session: SqlSession) -> None:
    sync_skills(db_session)

    student = Student(name="Test Student", year_level=8, curriculum="QCAA")
    db_session.add(student)
    db_session.flush()

    skills = {s.name: s for s in load_skills(SKILLS_DIR)}
    fake = FakeProvider(
        canned_responses=[
            "criteria output",
            "model output",
            "guided output",
            "independent task",
            "Route to: check-structure",
            "coaching output",
            FEEDBACK_WITH_LEVELS,
        ]
    )
    executor = SkillExecutionService(provider=fake)
    orchestrator = SessionOrchestrator(db_session, executor, skills)

    session = await orchestrator.run_daily_loop(
        student_id=student.id,
        year_level="8",
        text_type="analytical",
        task_prompt="How does the poet present war?",
        student_text="War is bad.",
    )

    feedback = db_session.execute(
        select(Feedback).join(Attempt).where(Attempt.session_id == session.id)
    ).scalar_one()
    scores = (
        db_session.execute(select(RubricScore).where(RubricScore.feedback_id == feedback.id))
        .scalars()
        .all()
    )
    assert len(scores) == 5
    by_name = {score.criterion_name: score for score in scores}
    assert by_name["Understanding of text / ideas"].level == "C"
    assert by_name["Analysis (how techniques create meaning)"].level == "D"
    assert by_name["Use of evidence"].level == "C-"  # en dash normalised
    assert by_name["Structure & cohesion"].level == "D+"
    assert by_name["Language & vocabulary"].note == "clear but flat."
    for score in scores:
        assert len(score.level) <= 5
        assert score.outcome_id is None
        assert score.scored_at is not None

    # Existing behaviour is unchanged: 7 attempts, 1 feedback row.
    attempts = (
        db_session.execute(select(Attempt).where(Attempt.session_id == session.id)).scalars().all()
    )
    assert len(attempts) == 7
