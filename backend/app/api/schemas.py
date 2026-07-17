"""Pydantic v2 request/response schemas for the daily-loop HTTP API."""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class StartSessionRequest(BaseModel):
    task_prompt: str = Field(min_length=1)
    year_level: str = "8"
    text_type: str = "analytical"


class SubmitRequest(BaseModel):
    text: str = Field(min_length=1)


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
    learning_intention: str | None
    turns: list[TurnOut]


class AdvanceOut(BaseModel):
    session_id: uuid.UUID
    stage: str
    turn: TurnOut


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


class SubmitOut(BaseModel):
    session_id: uuid.UUID
    stage: str
    ended: bool
    turns: list[TurnOut]
    feedback: FeedbackOut | None


class ProgressScoreOut(BaseModel):
    criterion_name: str
    level: str
    note: str | None
    scored_at: datetime
    session_id: uuid.UUID
    feedback_id: uuid.UUID


class ProgressOut(BaseModel):
    student_id: uuid.UUID
    scores: list[ProgressScoreOut]
