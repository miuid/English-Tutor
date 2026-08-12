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
    StudentCreate,
    StudentOut,
    StudentUpdate,
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
        kind="student" if attempt.task_type == "submission" else "tutor",
        skill=attempt.skill.name if attempt.skill is not None else None,
        task_type=attempt.task_type,
        mode=attempt.mode,
        text=attempt.student_text,
        prompt=attempt.task_prompt,
        created_at=attempt.created_at,
    )


def _session_out(session: Session, attempts: list[Attempt], loop: InteractiveLoop) -> SessionOut:
    spent, time_up = loop.time_state(session)
    return SessionOut(
        id=session.id,
        student_id=session.student_id,
        stage=session.stage,
        ended=session.ended_at is not None,
        paused=session.paused_at is not None,
        learning_intention=session.learning_intention,
        time_limit_seconds=loop.time_limit_seconds,
        time_spent_seconds=spent,
        time_up=time_up,
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


def _student_out(student: Student) -> StudentOut:
    return StudentOut(
        id=student.id,
        name=student.name,
        year_level=student.year_level,
        curriculum=student.curriculum,
        focus_text_types=student.focus_text_types or [],
        created_at=student.created_at,
    )


@router.post("/students", status_code=201)
async def create_student(
    payload: StudentCreate,
    db: DBSession = Depends(get_db),
) -> StudentOut:
    """Create a student profile (year, curriculum, focus text types)."""
    student = Student(
        name=payload.name,
        year_level=payload.year_level,
        curriculum=payload.curriculum,
        focus_text_types=payload.focus_text_types,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return _student_out(student)


@router.get("/students")
async def list_students(db: DBSession = Depends(get_db)) -> list[StudentOut]:
    """List all students (Beta: per-family install has few profiles)."""
    rows = db.execute(select(Student).order_by(Student.created_at)).scalars().all()
    return [_student_out(s) for s in rows]


@router.get("/students/{student_id}")
async def get_student(
    student_id: uuid.UUID,
    db: DBSession = Depends(get_db),
) -> StudentOut:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return _student_out(student)


@router.patch("/students/{student_id}")
async def update_student(
    student_id: uuid.UUID,
    payload: StudentUpdate,
    db: DBSession = Depends(get_db),
) -> StudentOut:
    """Update a student profile (name / year / curriculum / focus text types)."""
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    if payload.name is not None:
        student.name = payload.name
    if payload.year_level is not None:
        student.year_level = payload.year_level
    if payload.curriculum is not None:
        student.curriculum = payload.curriculum
    if payload.focus_text_types is not None:
        student.focus_text_types = payload.focus_text_types
    db.commit()
    db.refresh(student)
    return _student_out(student)


@router.post("/sessions", status_code=201)
async def start_session(
    payload: StartSessionRequest,
    loop: InteractiveLoop = Depends(get_loop),
) -> SessionOut:
    """Start a session: create it and return the set-success-criteria turn.

    If ``student_id`` is provided, the session attaches to that profile and
    the skill inputs inherit the student's ``year_level`` / ``focus_text_types``.
    Otherwise the loop falls back to the legacy single-user student (the first
    or a newly created one) with the request's ``year_level`` / ``text_type``.
    """
    try:
        session = await loop.start(
            task_prompt=payload.task_prompt,
            context=payload.context,
            student_id=payload.student_id,
            year_level=payload.year_level,
            text_type=payload.text_type,
        )
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Student not found") from None
    session, attempts = loop.get_state(session.id)
    return _session_out(session, attempts, loop)


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
    return _session_out(session, attempts, loop)


@router.post("/sessions/{session_id}/advance")
async def advance_session(
    session_id: uuid.UUID,
    loop: InteractiveLoop = Depends(get_loop),
) -> AdvanceOut:
    """Run the next tutor stage and return its turn.

    When the daily time budget is spent this returns a wrap-up turn with
    ``time_up=True`` and the session auto-pauses until tomorrow.
    """
    try:
        result = await loop.advance(session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    except StageConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    session = loop.get_session(session_id)
    return AdvanceOut(
        session_id=session_id,
        stage=session.stage,
        turn=_turn_out(result.turn),
        time_up=result.time_up,
        paused=session.paused_at is not None,
    )


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
        time_up=result.time_up,
        paused=session.paused_at is not None,
    )


@router.post("/sessions/{session_id}/pause")
async def pause_session(
    session_id: uuid.UUID,
    loop: InteractiveLoop = Depends(get_loop),
) -> SessionOut:
    """Pause a running session so the student can continue tomorrow."""
    try:
        loop.pause(session_id)
        session, attempts = loop.get_state(session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    except StageConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    return _session_out(session, attempts, loop)


@router.post("/sessions/{session_id}/resume")
async def resume_session(
    session_id: uuid.UUID,
    loop: InteractiveLoop = Depends(get_loop),
) -> SessionOut:
    """Resume a paused session; a new day restores the full time budget."""
    try:
        loop.resume(session_id)
        session, attempts = loop.get_state(session_id)
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found") from None
    except StageConflictError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    return _session_out(session, attempts, loop)


@router.delete("/students/{student_id}", status_code=204)
async def delete_student(
    student_id: uuid.UUID,
    db: DBSession = Depends(get_db),
) -> None:
    """Delete a student and all their data (privacy requirement).

    Cascades through sessions, attempts, feedback, rubric scores,
    success criteria, and interaction logs.
    """
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()


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
