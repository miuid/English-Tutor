"""Tests for the session orchestrator."""

from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session as SqlSession

from app.llm import FakeProvider
from app.models import Attempt, Feedback, Student
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
