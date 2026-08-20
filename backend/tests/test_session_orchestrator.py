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
            "retrieval output",
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
        db_session.execute(
            select(Attempt)
            .where(Attempt.session_id == session.id)
            .order_by(Attempt.created_at)
        )
        .scalars()
        .all()
    )
    # The daily loop order is retrieval -> criteria -> I do -> we do -> you do
    # -> diagnosis -> coach -> feedback.
    assert [a.task_type for a in attempts] == [
        "retrieval",
        "criteria",
        "model",
        "guided",
        "independent",
        "diagnosis",
        "coach",
        "feedback",
    ]

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
            "retrieval output",
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

    # Existing behaviour is unchanged: 8 attempts, 1 feedback row.
    attempts = (
        db_session.execute(select(Attempt).where(Attempt.session_id == session.id)).scalars().all()
    )
    assert len(attempts) == 8


@pytest.mark.asyncio
async def test_run_daily_loop_year_9_cites_year_9_descriptors(
    db_session: SqlSession,
) -> None:
    """A year_level=9 loop runs end-to-end on the year-9-10 packs and persists scores."""
    sync_skills(db_session)

    student = Student(name="Year 9 Student", year_level=9, curriculum="QCAA")
    db_session.add(student)
    db_session.flush()

    skills = {s.name: s for s in load_skills(SKILLS_DIR)}
    fake = FakeProvider(
        canned_responses=[
            "retrieval output",
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
        year_level="9",
        text_type="analytical",
        task_prompt="How does Shakespeare construct the representation of ambition in Macbeth?",
        student_text="Macbeth is ambitious.",
    )

    assert session.ended_at is not None

    # Every pack-bearing tutor turn ran against the exact analytical/year-9-10
    # packs (packs mention "Year 9"); the feedback prompt cites the Year 9
    # descriptors ("discriminating thesis"), and no degradation note appears.
    # spaced-review (call 0) is shared-only by design, so it bears no pack.
    assert len(fake.calls) == 8
    pack_bearing_calls = [1, 4, 5, 6, 7]  # criteria, independent, diagnosis, coach, feedback
    for index in pack_bearing_calls:
        system_prompt = fake.calls[index][0]
        assert "Year 9" in system_prompt
    assert "discriminating thesis" in fake.calls[7][0]  # give-feedback rubric
    for attempt in session.attempts:
        assert "_Note: no dedicated references" not in attempt.student_text

    # Rubric scores persist for the graded Year 9 attempt.
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
    assert by_name["Analysis (how techniques create meaning)"].level == "D"
    assert by_name["Structure & cohesion"].level == "D+"


@pytest.mark.asyncio
async def test_run_daily_loop_strict_tone_changes_prompt_not_contract(
    db_session: SqlSession,
) -> None:
    """A strict-tone student gets strict-tone prompts; the teaching contract
    (rubric criteria, levels, bounded next steps) is identical to the default."""
    sync_skills(db_session)

    student = Student(
        name="Strict Tone Student",
        year_level=8,
        curriculum="QCAA",
        coach_tone="strict",
    )
    db_session.add(student)
    db_session.flush()

    skills = {s.name: s for s in load_skills(SKILLS_DIR)}
    fake = FakeProvider(
        canned_responses=[
            "retrieval output",
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

    assert session.ended_at is not None

    # Every tutor turn ran with the strict tone directive in the system
    # prompt, and none leaked the tone into the user message.
    assert len(fake.calls) == 8
    for system_prompt, messages in fake.calls:
        assert "--- Coach tone ---" in system_prompt
        assert "direct, no-nonsense tone" in system_prompt
        assert "never what you teach" in system_prompt
        assert "coach_tone" not in messages[0]["content"]

    # The output contract is tone-invariant: the same canned feedback parses
    # into the same five rubric scores as the default-tone loop.
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
