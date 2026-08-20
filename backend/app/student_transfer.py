"""One-click local export/import of a student's full data.

The export is a single JSON document containing the profile plus every
session, attempt, feedback row, rubric score, success criterion, and
interaction log belonging to the student. Import restores the payload as a
NEW student (fresh UUIDs, references remapped) so a backup can be restored
onto a machine that still holds the original profile without primary-key
collisions; timestamps are preserved so progress trends survive the
round-trip.

This is sensitive minor data (PRD §6): export stays a local file download,
import only writes to the local database. Nothing leaves the machine beyond
the existing cloud-LLM processing of student writing during sessions.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models import (
    Attempt,
    CurriculumOutcome,
    Feedback,
    InteractionLog,
    RubricScore,
    Session,
    Skill,
    Student,
    SuccessCriterion,
)

EXPORT_FORMAT = "english-tutor-student-export"
EXPORT_VERSION = 1


class ExportImportError(ValueError):
    """Raised when an import payload is not a valid export document."""


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _parse_dt(value: Any, field: str) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ExportImportError(f"{field}: expected ISO datetime string or null")
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise ExportImportError(f"{field}: invalid ISO datetime {value!r}") from exc


def _parse_uuid(value: Any) -> uuid.UUID | None:
    if value is None:
        return None
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError, TypeError):
        return None


def export_student(db: DBSession, student: Student) -> dict[str, Any]:
    """Serialize the student and all their data into an export document."""
    sessions = db.execute(
        select(Session)
        .where(Session.student_id == student.id)
        .order_by(Session.started_at)
    ).scalars().all()

    session_docs: list[dict[str, Any]] = []
    for session in sessions:
        attempts = db.execute(
            select(Attempt)
            .where(Attempt.session_id == session.id)
            .order_by(Attempt.created_at)
        ).scalars().all()
        criteria = db.execute(
            select(SuccessCriterion).where(SuccessCriterion.session_id == session.id)
        ).scalars().all()
        logs = db.execute(
            select(InteractionLog)
            .where(InteractionLog.session_id == session.id)
            .order_by(InteractionLog.created_at)
        ).scalars().all()

        attempt_docs: list[dict[str, Any]] = []
        for attempt in attempts:
            feedback_doc: dict[str, Any] | None = None
            if attempt.feedback is not None:
                feedback = attempt.feedback
                scores = db.execute(
                    select(RubricScore)
                    .where(RubricScore.feedback_id == feedback.id)
                    .order_by(RubricScore.scored_at)
                ).scalars().all()
                feedback_doc = {
                    "strength": feedback.strength,
                    "next_steps": feedback.next_steps,
                    "created_at": _iso(feedback.created_at),
                    "rubric_scores": [
                        {
                            "criterion_name": score.criterion_name,
                            "level": score.level,
                            "note": score.note,
                            "scored_at": _iso(score.scored_at),
                            "outcome_id": str(score.outcome_id)
                            if score.outcome_id
                            else None,
                        }
                        for score in scores
                    ],
                }
            attempt_docs.append(
                {
                    "task_type": attempt.task_type,
                    "mode": attempt.mode,
                    "task_prompt": attempt.task_prompt,
                    "student_text": attempt.student_text,
                    "created_at": _iso(attempt.created_at),
                    "skill_id": str(attempt.skill_id) if attempt.skill_id else None,
                    "feedback": feedback_doc,
                }
            )

        session_docs.append(
            {
                "started_at": _iso(session.started_at),
                "ended_at": _iso(session.ended_at),
                "learning_intention": session.learning_intention,
                "stage": session.stage,
                "time_spent_seconds": session.time_spent_seconds,
                "last_activity_at": _iso(session.last_activity_at),
                "paused_at": _iso(session.paused_at),
                "success_criteria": [
                    {
                        "text": criterion.text,
                        "self_rating": criterion.self_rating,
                        "met": criterion.met,
                        "outcome_id": str(criterion.outcome_id)
                        if criterion.outcome_id
                        else None,
                    }
                    for criterion in criteria
                ],
                "attempts": attempt_docs,
                "interaction_logs": [
                    {
                        "model": log.model,
                        "input": log.input,
                        "output": log.output,
                        "created_at": _iso(log.created_at),
                        "skill_id": str(log.skill_id) if log.skill_id else None,
                    }
                    for log in logs
                ],
            }
        )

    return {
        "format": EXPORT_FORMAT,
        "version": EXPORT_VERSION,
        "exported_at": datetime.now(UTC).isoformat(),
        "student": {
            "name": student.name,
            "year_level": student.year_level,
            "curriculum": student.curriculum,
            "focus_text_types": list(student.focus_text_types or []),
            "created_at": _iso(student.created_at),
        },
        "sessions": session_docs,
    }


def _resolve_fk(
    db: DBSession,
    model: type[Skill] | type[CurriculumOutcome],
    raw: Any,
) -> uuid.UUID | None:
    """Keep a registry reference only when the target row exists locally.

    Skill and curriculum-outcome rows are global registry data (synced/seeded
    on startup), not student data, so they are referenced rather than
    exported. If the target is missing on this install the column falls back
    to NULL, matching its ON DELETE SET NULL semantics.
    """
    ref = _parse_uuid(raw)
    if ref is None:
        return None
    return ref if db.get(model, ref) is not None else None


def import_student(db: DBSession, payload: Any) -> Student:
    """Restore an export document as a new student; returns the new profile."""
    if not isinstance(payload, dict):
        raise ExportImportError("Import payload must be a JSON object.")
    if payload.get("format") != EXPORT_FORMAT:
        raise ExportImportError("Not an English Tutor student export file.")
    if payload.get("version") != EXPORT_VERSION:
        raise ExportImportError(
            f"Unsupported export version {payload.get('version')!r}."
        )
    student_doc = payload.get("student")
    if not isinstance(student_doc, dict):
        raise ExportImportError("Export is missing the student profile.")
    name = student_doc.get("name")
    year_level = student_doc.get("year_level")
    curriculum = student_doc.get("curriculum")
    if not isinstance(name, str) or not name.strip():
        raise ExportImportError("Student profile is missing a name.")
    if not isinstance(year_level, int) or not 8 <= year_level <= 12:
        raise ExportImportError("Student profile has an invalid year level.")
    if not isinstance(curriculum, str) or not curriculum.strip():
        raise ExportImportError("Student profile is missing a curriculum.")
    focus = student_doc.get("focus_text_types") or []
    if not isinstance(focus, list) or not all(isinstance(t, str) for t in focus):
        raise ExportImportError("Student focus_text_types must be a list of strings.")
    sessions_doc = payload.get("sessions")
    if not isinstance(sessions_doc, list):
        raise ExportImportError("Export is missing the sessions list.")

    student = Student(
        name=name,
        year_level=year_level,
        curriculum=curriculum,
        focus_text_types=focus,
        created_at=_parse_dt(student_doc.get("created_at"), "student.created_at")
        or datetime.now(UTC),
    )
    db.add(student)
    db.flush()  # assign student.id for the child rows

    for i, session_doc in enumerate(sessions_doc):
        if not isinstance(session_doc, dict):
            raise ExportImportError(f"sessions[{i}] must be an object.")
        session = Session(
            student_id=student.id,
            started_at=_parse_dt(session_doc.get("started_at"), f"sessions[{i}].started_at")
            or datetime.now(UTC),
            ended_at=_parse_dt(session_doc.get("ended_at"), f"sessions[{i}].ended_at"),
            learning_intention=session_doc.get("learning_intention"),
            stage=str(session_doc.get("stage") or "start"),
            time_spent_seconds=int(session_doc.get("time_spent_seconds") or 0),
            last_activity_at=_parse_dt(
                session_doc.get("last_activity_at"), f"sessions[{i}].last_activity_at"
            ),
            paused_at=_parse_dt(session_doc.get("paused_at"), f"sessions[{i}].paused_at"),
        )
        db.add(session)
        db.flush()

        for criterion_doc in session_doc.get("success_criteria") or []:
            db.add(
                SuccessCriterion(
                    session_id=session.id,
                    outcome_id=_resolve_fk(
                        db, CurriculumOutcome, criterion_doc.get("outcome_id")
                    ),
                    text=str(criterion_doc.get("text") or ""),
                    self_rating=criterion_doc.get("self_rating"),
                    met=criterion_doc.get("met"),
                )
            )

        for attempt_doc in session_doc.get("attempts") or []:
            attempt = Attempt(
                session_id=session.id,
                student_id=student.id,
                skill_id=_resolve_fk(db, Skill, attempt_doc.get("skill_id")),
                task_type=str(attempt_doc.get("task_type") or ""),
                mode=str(attempt_doc.get("mode") or "practice"),
                task_prompt=str(attempt_doc.get("task_prompt") or ""),
                student_text=str(attempt_doc.get("student_text") or ""),
                created_at=_parse_dt(attempt_doc.get("created_at"), "attempt.created_at")
                or datetime.now(UTC),
            )
            db.add(attempt)
            db.flush()

            feedback_doc = attempt_doc.get("feedback")
            if isinstance(feedback_doc, dict):
                feedback = Feedback(
                    attempt_id=attempt.id,
                    strength=str(feedback_doc.get("strength") or ""),
                    next_steps=str(feedback_doc.get("next_steps") or ""),
                    created_at=_parse_dt(
                        feedback_doc.get("created_at"), "feedback.created_at"
                    )
                    or datetime.now(UTC),
                )
                db.add(feedback)
                db.flush()
                for score_doc in feedback_doc.get("rubric_scores") or []:
                    db.add(
                        RubricScore(
                            feedback_id=feedback.id,
                            outcome_id=_resolve_fk(
                                db, CurriculumOutcome, score_doc.get("outcome_id")
                            ),
                            criterion_name=str(score_doc.get("criterion_name") or ""),
                            level=str(score_doc.get("level") or ""),
                            note=score_doc.get("note"),
                            scored_at=_parse_dt(
                                score_doc.get("scored_at"), "rubric_score.scored_at"
                            )
                            or datetime.now(UTC),
                        )
                    )

        for log_doc in session_doc.get("interaction_logs") or []:
            db.add(
                InteractionLog(
                    session_id=session.id,
                    skill_id=_resolve_fk(db, Skill, log_doc.get("skill_id")),
                    model=str(log_doc.get("model") or ""),
                    input=str(log_doc.get("input") or ""),
                    output=str(log_doc.get("output") or ""),
                    created_at=_parse_dt(log_doc.get("created_at"), "log.created_at")
                    or datetime.now(UTC),
                )
            )

    db.commit()
    db.refresh(student)
    return student
