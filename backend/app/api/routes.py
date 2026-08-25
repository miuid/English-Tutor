"""HTTP API for the interactive daily loop."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.api.deps import get_db, get_loop
from app.api.schemas import (
    AdvanceOut,
    BaselineOut,
    BaselineRequest,
    CriterionTrendOut,
    FeedbackOut,
    LevelUpOut,
    LevelUpsOut,
    MockOut,
    MockRequest,
    MotivationOut,
    ParentReportOut,
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
    TrendPointOut,
    TurnOut,
)
from app.config import get_settings
from app.level_ups import build_level_ups
from app.models import Attempt, Feedback, RubricScore, Session, Student
from app.motivation import build_motivation
from app.parent_report import ParentReport, build_parent_report, render_parent_report_html
from app.sessions.interactive import InteractiveLoop, SessionNotFoundError, StageConflictError
from app.student_transfer import ExportImportError, export_student, import_student
from app.telemetry import build_feedback_package, build_telemetry

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
        weekly_goal=student.weekly_goal,
        coach_tone=student.coach_tone,
        shared_goal=student.shared_goal,
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
        weekly_goal=payload.weekly_goal,
        coach_tone=payload.coach_tone,
        shared_goal=(payload.shared_goal or "").strip() or None,
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


# NOTE: /students/import is declared before /students/{student_id} so the
# literal path wins over the UUID path parameter.
@router.post("/students/import", status_code=201)
async def import_student_data(
    payload: dict[str, Any],
    db: DBSession = Depends(get_db),
) -> StudentOut:
    """Restore a student export file as a new profile with all its data.

    The restore always creates fresh IDs (never overwrites an existing
    profile) and preserves timestamps so progress trends survive the
    round-trip. The payload is sensitive minor data and stays local.
    """
    try:
        student = import_student(db, payload)
    except ExportImportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    return _student_out(student)


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
    if payload.weekly_goal is not None:
        student.weekly_goal = payload.weekly_goal
    if payload.coach_tone is not None:
        student.coach_tone = payload.coach_tone
    if payload.shared_goal is not None:
        student.shared_goal = payload.shared_goal.strip() or None
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


@router.post("/students/{student_id}/baseline", status_code=201)
async def run_baseline_assessment(
    student_id: uuid.UUID,
    payload: BaselineRequest,
    loop: InteractiveLoop = Depends(get_loop),
) -> BaselineOut:
    """Run a first-use baseline from one timed write.

    Persists a short ended session holding the submission and the
    baseline-assessment report, writes the student's day-0 rubric scores
    (surfaced by the progress endpoint), and returns the report, which
    includes the ranked weaknesses and the recommended starting focus loop.
    The report is coaching-oriented, not a grade; the profile is never
    mutated by the recommendation.
    """
    try:
        result = await loop.run_baseline(
            student_id=student_id,
            text=payload.text,
            text_type=payload.text_type,
        )
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Student not found") from None
    return BaselineOut(
        session_id=result.session.id,
        feedback=_feedback_out(result.feedback),
        report=result.report_turn.student_text,
    )


@router.post("/students/{student_id}/mock", status_code=201)
async def run_weekly_mock(
    student_id: uuid.UUID,
    payload: MockRequest,
    loop: InteractiveLoop = Depends(get_loop),
) -> MockOut:
    """Run a weekly timed mock from one exam-conditions write.

    Persists a short ended session holding the submission
    (``attempt.mode='assessment'``) and the summative give-feedback turn
    (overall A–E attached), writes the rubric scores (surfaced by the
    progress endpoint, distinguished from daily practice points), and
    returns the bounded summative feedback: per-criterion levels, one
    strength, and 1–2 next steps.
    """
    try:
        result = await loop.run_mock(
            student_id=student_id,
            text=payload.text,
            text_type=payload.text_type,
        )
    except SessionNotFoundError:
        raise HTTPException(status_code=404, detail="Student not found") from None
    return MockOut(
        session_id=result.session.id,
        feedback=_feedback_out(result.feedback),
        report=result.feedback_turn.student_text,
    )


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


@router.get("/students/{student_id}/export")
async def export_student_data(
    student_id: uuid.UUID,
    db: DBSession = Depends(get_db),
) -> JSONResponse:
    """Download the student's full data as one local JSON file.

    Includes the profile, sessions, attempts, feedback, rubric scores,
    success criteria, and interaction logs. This is sensitive minor data:
    it is only ever served to the local app as a file download.
    """
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    document = export_student(db, student)
    safe_name = "".join(
        ch if ch.isalnum() else "-" for ch in student.name.strip().lower()
    ).strip("-") or "student"
    return JSONResponse(
        content=document,
        headers={
            "Content-Disposition": (
                f'attachment; filename="english-tutor-export-{safe_name}.json"'
            )
        },
    )


@router.get("/students/{student_id}/telemetry")
async def student_telemetry(
    student_id: uuid.UUID,
    db: DBSession = Depends(get_db),
) -> JSONResponse:
    """Aggregated usage metrics for one student (ISS-022).

    Counts, totals, and timestamps only — never student writing, task
    prompts, feedback prose, rubric notes, or LLM prompt/completion text.
    """
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return JSONResponse(
        content={
            "student_id": str(student_id),
            "telemetry": build_telemetry(db, student),
        }
    )


@router.get("/students/{student_id}/feedback-package")
async def student_feedback_package(
    student_id: uuid.UUID,
    db: DBSession = Depends(get_db),
) -> JSONResponse:
    """One-click feedback package download for beta families (ISS-022).

    Bundles aggregated telemetry, redacted non-secret config, environment
    metadata, and recent session/interaction *metadata* (lengths, not text)
    so a beta issue can be diagnosed without remote access. Safe to email:
    no student writing, no LLM content, no student name, no credentials.
    """
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    document = build_feedback_package(db, student, get_settings())
    return JSONResponse(
        content=document,
        headers={
            "Content-Disposition": (
                'attachment; filename="english-tutor-feedback-package.json"'
            )
        },
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
            select(RubricScore, Attempt.session_id, Attempt.mode)
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
                mode=attempt_mode,
            )
            for score, session_id_for_score, attempt_mode in rows
        ],
    )


@router.get("/students/{student_id}/motivation")
async def student_motivation(
    student_id: uuid.UUID,
    db: DBSession = Depends(get_db),
) -> MotivationOut:
    """Streak and weekly-goal state for one student.

    The streak is derived from session history (a practice day is any local
    date with at least one session — daily loop, baseline, or weekly mock).
    A lapsed streak is reported as ``streak_broken`` so the UI can answer
    with a recovery prompt, never a penalty.
    """
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    summary = build_motivation(db, student.id, student.weekly_goal)
    return MotivationOut(
        student_id=student_id,
        current_streak=summary.current_streak,
        streak_broken=summary.streak_broken,
        weekly_goal=summary.weekly_goal,
        sessions_this_week=summary.sessions_this_week,
        goal_met=summary.goal_met,
        last_activity_date=summary.last_activity_date,
    )


@router.get("/students/{student_id}/level-ups")
async def student_level_ups(
    student_id: uuid.UUID,
    db: DBSession = Depends(get_db),
) -> LevelUpsOut:
    """Criterion band crossings derived from rubric_score history, oldest first.

    A level-up fires when a criterion reaches a personal-best A–E band
    (modifiers ignored); the event carries the rubric note recorded with the
    new score so the celebration names the real improvement mechanism.
    """
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    events = build_level_ups(db, student.id)
    return LevelUpsOut(
        student_id=student_id,
        level_ups=[
            LevelUpOut(
                criterion_name=event.criterion_name,
                from_level=event.from_level,
                to_level=event.to_level,
                note=event.note,
                scored_at=event.scored_at,
                session_id=event.session_id,
                feedback_id=event.feedback_id,
            )
            for event in events
        ],
    )


def _parent_report_out(report: ParentReport) -> ParentReportOut:
    return ParentReportOut(
        student_id=report.student_id,
        student_name=report.student_name,
        year_level=report.year_level,
        curriculum=report.curriculum,
        week_start=report.week_start,
        week_end=report.week_end,
        sessions_this_week=report.sessions_this_week,
        practice_seconds_this_week=report.practice_seconds_this_week,
        weekly_goal=report.weekly_goal,
        goal_met=report.goal_met,
        shared_goal=report.shared_goal,
        trends=[
            CriterionTrendOut(
                criterion_name=trend.criterion_name,
                latest_level=trend.latest_level,
                previous_level=trend.previous_level,
                direction=trend.direction,
                points=[
                    TrendPointOut(scored_on=point.scored_on, level=point.level)
                    for point in trend.points
                ],
            )
            for trend in report.trends
        ],
        highlight=report.highlight,
        next_week_suggestion=report.next_week_suggestion,
    )


@router.get("/students/{student_id}/parent-report")
async def parent_report(
    student_id: uuid.UUID,
    db: DBSession = Depends(get_db),
) -> ParentReportOut:
    """Weekly parent report: sessions, time, criterion trends, highlight,
    and a next-week suggestion (ISS-019).

    D3 privacy boundary: the report carries trends, levels, time, and goals
    only — never the student's essay text, task prompts, rubric notes, or
    tutor feedback prose.
    """
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return _parent_report_out(build_parent_report(db, student))


@router.get("/students/{student_id}/parent-report/print")
async def parent_report_print(
    student_id: uuid.UUID,
    db: DBSession = Depends(get_db),
) -> HTMLResponse:
    """Printable one-page version of the weekly parent report.

    Rendered server-side from the same derived ``ParentReport`` value as
    the JSON endpoint, so the D3 privacy boundary is enforced in exactly
    one place. Parents print or save to PDF from the browser; nothing new
    is persisted.
    """
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return HTMLResponse(render_parent_report_html(build_parent_report(db, student)))
