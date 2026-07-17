"""Tests for SQLAlchemy models and cascade behavior."""

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlSession

from app.models import (
    Attempt,
    CurriculumOutcome,
    Feedback,
    RubricScore,
    Session,
    Student,
)


def test_create_and_delete_student_cascades(db_session: SqlSession) -> None:
    """Full student->session->attempt->feedback->rubric_score chain and delete cascade."""
    student = Student(name="Test Student", year_level=8, curriculum="QCAA")
    db_session.add(student)
    db_session.commit()

    session = Session(student=student, learning_intention="Test session")
    db_session.add(session)
    db_session.commit()

    outcome = CurriculumOutcome(
        code="QCAA-Y8-ANL-TEST",
        strand="Test",
        year_level=8,
        text_type="analytical",
        curriculum="QCAA",
        descriptor="Test outcome",
    )
    db_session.add(outcome)
    db_session.commit()

    attempt = Attempt(
        session=session,
        student=student,
        task_type="paragraph",
        mode="practice",
        task_prompt="Write a paragraph.",
        student_text="Test text.",
    )
    db_session.add(attempt)
    db_session.commit()

    feedback = Feedback(
        attempt=attempt,
        strength="Good start.",
        next_steps="Add more analysis.",
    )
    db_session.add(feedback)
    db_session.commit()

    score = RubricScore(
        feedback=feedback,
        outcome=outcome,
        criterion_name="Analysis",
        level="C",
    )
    db_session.add(score)
    db_session.commit()

    # Read back and verify relationships
    result = db_session.execute(
        select(Student).where(Student.id == student.id),
    ).scalar_one()
    assert result.name == "Test Student"
    assert len(result.sessions) == 1
    assert len(result.attempts) == 1

    # Delete student and verify no orphaned rows
    db_session.delete(student)
    db_session.commit()

    assert db_session.execute(select(Student)).scalar_one_or_none() is None
    assert db_session.execute(select(Session)).scalar_one_or_none() is None
    assert db_session.execute(select(Attempt)).scalar_one_or_none() is None
    assert db_session.execute(select(Feedback)).scalar_one_or_none() is None
    assert db_session.execute(select(RubricScore)).scalar_one_or_none() is None
    # Reference data should remain
    assert db_session.execute(select(CurriculumOutcome)).scalar_one_or_none() is not None
