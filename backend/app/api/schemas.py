"""Pydantic v2 request/response schemas for the daily-loop HTTP API."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field

from app.models import DEFAULT_WEEKLY_GOAL, MAX_WEEKLY_GOAL


class StudentCreate(BaseModel):
    """Create or register a student profile."""

    name: str = Field(min_length=1, max_length=255)
    year_level: int = Field(ge=8, le=12)
    curriculum: str = Field(default="QCAA", min_length=1)
    focus_text_types: list[str] = Field(default_factory=list)
    weekly_goal: int = Field(default=DEFAULT_WEEKLY_GOAL, ge=1, le=MAX_WEEKLY_GOAL)


class StudentUpdate(BaseModel):
    """Partial update of a student profile."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    year_level: int | None = Field(default=None, ge=8, le=12)
    curriculum: str | None = Field(default=None, min_length=1)
    focus_text_types: list[str] | None = None
    weekly_goal: int | None = Field(default=None, ge=1, le=MAX_WEEKLY_GOAL)


class StudentOut(BaseModel):
    id: uuid.UUID
    name: str
    year_level: int
    curriculum: str
    focus_text_types: list[str]
    weekly_goal: int
    created_at: datetime


class StartSessionRequest(BaseModel):
    task_prompt: str | None = Field(default=None, min_length=1)
    context: str | None = Field(default=None, min_length=1)
    student_id: uuid.UUID | None = None
    year_level: str = "8"
    text_type: str = "analytical"


class SubmitRequest(BaseModel):
    text: str = Field(min_length=1)


class BaselineRequest(BaseModel):
    """One timed write to baseline a new (or new-to-this-text-type) student."""

    text: str = Field(min_length=1)
    text_type: str | None = Field(default=None, min_length=1)


class MockRequest(BaseModel):
    """One exam-conditions write for the weekly timed mock."""

    text: str = Field(min_length=1)
    text_type: str | None = Field(default=None, min_length=1)


class TurnOut(BaseModel):
    """One conversation turn: a tutor skill output or a student submission."""

    id: uuid.UUID
    kind: str  # "tutor" | "student"
    skill: str | None
    task_type: str
    mode: str
    text: str
    prompt: str
    created_at: datetime


class SessionOut(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    stage: str
    ended: bool
    paused: bool
    learning_intention: str | None
    time_limit_seconds: int
    time_spent_seconds: int
    time_up: bool
    turns: list[TurnOut]


class AdvanceOut(BaseModel):
    session_id: uuid.UUID
    stage: str
    turn: TurnOut
    time_up: bool = False
    paused: bool = False


class RubricScoreOut(BaseModel):
    criterion_name: str
    level: str
    note: str | None
    scored_at: datetime


class FeedbackOut(BaseModel):
    id: uuid.UUID
    strength: str
    next_steps: str
    rubric_scores: list[RubricScoreOut]


class BaselineOut(BaseModel):
    """The persisted baseline: session, day-0 rubric scores, and the report."""

    session_id: uuid.UUID
    feedback: FeedbackOut
    report: str


class MockOut(BaseModel):
    """The persisted weekly mock: session and the summative A–E feedback."""

    session_id: uuid.UUID
    feedback: FeedbackOut
    report: str


class SubmitOut(BaseModel):
    session_id: uuid.UUID
    stage: str
    ended: bool
    turns: list[TurnOut]
    feedback: FeedbackOut | None
    time_up: bool = False
    paused: bool = False


class ProgressScoreOut(BaseModel):
    criterion_name: str
    level: str
    note: str | None
    scored_at: datetime
    session_id: uuid.UUID
    feedback_id: uuid.UUID
    mode: str  # attempt mode: daily loop stage, "baseline", or "assessment" (weekly mock)


class ProgressOut(BaseModel):
    student_id: uuid.UUID
    scores: list[ProgressScoreOut]


class MotivationOut(BaseModel):
    """Streak + weekly-goal state for the progress view (ISS-016).

    ``streak_broken`` means the student practised before but the run lapsed;
    the UI answers with a recovery prompt, never a penalty.
    """

    student_id: uuid.UUID
    current_streak: int
    streak_broken: bool
    weekly_goal: int
    sessions_this_week: int
    goal_met: bool
    last_activity_date: date | None
