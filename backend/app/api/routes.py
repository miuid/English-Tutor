"""HTTP API for the interactive daily loop."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_db, get_loop
from app.api.schemas import (
    AdvanceOut,
    FeedbackOut,
    ProgressOut,
    ProgressScoreOut,
    RubricScoreOut,
    SessionOut,
    StartSessionRequest,
    SubmitOut,
    SubmitRequest,
    TurnOut,
)
from app.models import Attempt, Feedback, RubricScore, Session, Student
from app.sessions.interactive import InteractiveLoop, SessionNotFoundError, StageConflictError

router = APIRouter(prefix="/api")


def _turn_out(attempt: Attempt) -> TurnOut:
    return TurnOut(
        id=attempt.id,
        kind="tutor" if attempt.skill_id is not None else "student",
        skill=attempt.skill.name if attempt.skill is not None else None,
        task_type=attempt.task_type,
        mode=attempt.mode,
        text=attempt.student_text,
        prompt=attempt.task_prompt,
        created_at=attempt.created_at,
    )


def _session_out(session: Session, attempts: list[Attempt]) -> SessionOut:
    return SessionOut(
        id=session.id,
        student_id=session.student_id,
        stage=session.stage,
        ended=session.ended_at is not None,
        learning_intention=session.learning_intention,
        turns=[_turn_out(attempt) for attempt in attempts],
    )


def _feedback_out(feedback: Feedback) -> FeedbackOut:
    return FeedbackOut(
        id=feedback.id,
        strength=feedback.strength,
        next_steps=feedback.next_steps,
        rubric_scores=[
            RubricScoreOut(
                criterion_name=score.criterion_name,
                level=score.level,
                note=score.note,
                scored_at=score.scored_at,
            )
            for score in feedback.rubric_scores
        ],
    )


@router.post("/sessions", status_code=201)
async def start_session(
    payload: StartSessionRequest,
    loop: InteractiveLoop = Depends(get_loop),
) -> SessionOut:
    """Start a session: create it and return the set-success-criteria turn."""
    session = await loop.start(
        task_prompt=payload.task_prompt,
        year_level=payload.year_level,
        text_type=payload.text_type,
    )
    session, attempts = loop.get_state(session.id)
    return _session_out(session, attempts)


@router.get("/sessions/{session_id}")
async def get_session_state(
    session_id: uuid.UUID,
    loop: InteractiveLoop = Depends(get_loop),
) -> SessionOut:
    """Full session state: all turns in order, current stage, ended flag."""
    try:
        session, attempts = loop.get_state(session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    return _session_out(session, attempts)


@router.post("/sessions/{session_id}/advance")
async def advance_session(
    session_id: uuid.UUID,
    loop: InteractiveLoop = Depends(get_loop),
) -> AdvanceOut:
    """Run the next tutor stage and return its turn."""
    try:
        turn = await loop.advance(session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    except StageConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    session = loop.get_session(session_id)
    return AdvanceOut(session_id=session_id, stage=session.stage, turn=_turn_out(turn))


@router.post("/sessions/{session_id}/submit")
async def submit_student_text(
    session_id: uuid.UUID,
    payload: SubmitRequest,
    loop: InteractiveLoop = Depends(get_loop),
) -> SubmitOut:
    """Submit student text; at 'you do' this completes the loop with feedback."""
    try:
        result = await loop.submit(session_id, payload.text)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    except StageConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    session = loop.get_session(session_id)
    turns = [result.submission, *result.tutor_turns]
    return SubmitOut(
        session_id=session.id,
        stage=session.stage,
        ended=session.ended_at is not None,
        turns=[_turn_out(turn) for turn in turns],
        feedback=_feedback_out(result.feedback) if result.feedback is not None else None,
    )


@router.get("/students/{student_id}/progress")
async def student_progress(
    student_id: uuid.UUID,
    db: DBSession = Depends(get_db),
) -> ProgressOut:
    """All rubric scores for a student, oldest first (feeds the progress view)."""
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    rows = (
        db.execute(
            select(RubricScore, Attempt.session_id)
            .join(Feedback, RubricScore.feedback_id == Feedback.id)
            .join(Attempt, Feedback.attempt_id == Attempt.id)
            .where(Attempt.student_id == student_id)
            .order_by(RubricScore.scored_at)
        )
        .all()
    )
    return ProgressOut(
        student_id=student_id,
        scores=[
            ProgressScoreOut(
                criterion_name=score.criterion_name,
                level=score.level,
                note=score.note,
                scored_at=score.scored_at,
                session_id=session_id_for_score,
                feedback_id=score.feedback_id,
            )
            for score, session_id_for_score in rows
        ],
    )
