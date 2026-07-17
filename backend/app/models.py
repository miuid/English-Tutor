"""SQLAlchemy models for the English Tutor data layer."""

import uuid
from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


def _now() -> datetime:
    return datetime.now(UTC)


class Student(Base):
    __tablename__ = "student"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(sa.String(255))
    year_level: Mapped[int]
    curriculum: Mapped[str] = mapped_column(sa.String(50))
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=_now,
    )

    sessions: Mapped[list["Session"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    attempts: Mapped[list["Attempt"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class CurriculumOutcome(Base):
    __tablename__ = "curriculum_outcome"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(sa.String(50), unique=True)
    strand: Mapped[str] = mapped_column(sa.String(50))
    year_level: Mapped[int]
    text_type: Mapped[str] = mapped_column(sa.String(50))
    curriculum: Mapped[str] = mapped_column(sa.String(50))
    descriptor: Mapped[str] = mapped_column(sa.Text)

    success_criteria: Mapped[list["SuccessCriterion"]] = relationship(
        back_populates="outcome",
        passive_deletes=True,
    )
    rubric_scores: Mapped[list["RubricScore"]] = relationship(
        back_populates="outcome",
        passive_deletes=True,
    )


class Skill(Base):
    __tablename__ = "skill"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(sa.String(100), unique=True)
    version: Mapped[str] = mapped_column(sa.String(20))
    loop_stage: Mapped[str] = mapped_column(sa.String(20))

    attempts: Mapped[list["Attempt"]] = relationship(
        back_populates="skill",
        passive_deletes=True,
    )
    interaction_logs: Mapped[list["InteractionLog"]] = relationship(
        back_populates="skill",
        passive_deletes=True,
    )


class Session(Base):
    __tablename__ = "session"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("student.id", ondelete="CASCADE"),
    )
    started_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=_now,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    learning_intention: Mapped[str | None] = mapped_column(
        sa.Text,
        nullable=True,
    )
    # Interactive-loop stage: start -> I do -> we do -> you do -> ended.
    stage: Mapped[str] = mapped_column(sa.String(20), default="start")

    student: Mapped["Student"] = relationship(back_populates="sessions")
    success_criteria: Mapped[list["SuccessCriterion"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    attempts: Mapped[list["Attempt"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    interaction_logs: Mapped[list["InteractionLog"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SuccessCriterion(Base):
    __tablename__ = "success_criterion"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("session.id", ondelete="CASCADE"),
    )
    outcome_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("curriculum_outcome.id", ondelete="SET NULL"),
        nullable=True,
    )
    text: Mapped[str] = mapped_column(sa.Text)
    self_rating: Mapped[str | None] = mapped_column(
        sa.String(10),
        nullable=True,
    )
    met: Mapped[bool | None] = mapped_column(
        sa.Boolean,
        nullable=True,
    )

    session: Mapped["Session"] = relationship(back_populates="success_criteria")
    outcome: Mapped["CurriculumOutcome | None"] = relationship(
        back_populates="success_criteria",
    )


class Attempt(Base):
    __tablename__ = "attempt"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("session.id", ondelete="CASCADE"),
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("student.id", ondelete="CASCADE"),
    )
    skill_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("skill.id", ondelete="SET NULL"),
        nullable=True,
    )
    task_type: Mapped[str] = mapped_column(sa.String(50))
    mode: Mapped[str] = mapped_column(sa.String(50))
    task_prompt: Mapped[str] = mapped_column(sa.Text)
    student_text: Mapped[str] = mapped_column(sa.Text)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=_now,
    )

    session: Mapped["Session"] = relationship(back_populates="attempts")
    student: Mapped["Student"] = relationship(back_populates="attempts")
    skill: Mapped["Skill | None"] = relationship(back_populates="attempts")
    feedback: Mapped["Feedback | None"] = relationship(
        back_populates="attempt",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class Feedback(Base):
    __tablename__ = "feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("attempt.id", ondelete="CASCADE"),
        unique=True,
    )
    strength: Mapped[str] = mapped_column(sa.Text)
    next_steps: Mapped[str] = mapped_column(sa.Text)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=_now,
    )

    attempt: Mapped["Attempt"] = relationship(back_populates="feedback")
    rubric_scores: Mapped[list["RubricScore"]] = relationship(
        back_populates="feedback",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class RubricScore(Base):
    __tablename__ = "rubric_score"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    feedback_id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("feedback.id", ondelete="CASCADE"),
    )
    outcome_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("curriculum_outcome.id", ondelete="SET NULL"),
        nullable=True,
    )
    criterion_name: Mapped[str] = mapped_column(sa.String(100))
    level: Mapped[str] = mapped_column(sa.String(5))
    note: Mapped[str | None] = mapped_column(
        sa.Text,
        nullable=True,
    )
    scored_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=_now,
    )

    feedback: Mapped["Feedback"] = relationship(back_populates="rubric_scores")
    outcome: Mapped["CurriculumOutcome | None"] = relationship(
        back_populates="rubric_scores",
    )


class InteractionLog(Base):
    __tablename__ = "interaction_log"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    session_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("session.id", ondelete="CASCADE"),
        nullable=True,
    )
    skill_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.Uuid,
        sa.ForeignKey("skill.id", ondelete="SET NULL"),
        nullable=True,
    )
    model: Mapped[str] = mapped_column(sa.String(100))
    input: Mapped[str] = mapped_column(sa.Text)
    output: Mapped[str] = mapped_column(sa.Text)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        default=_now,
    )

    session: Mapped["Session | None"] = relationship(back_populates="interaction_logs")
    skill: Mapped["Skill | None"] = relationship(back_populates="interaction_logs")
