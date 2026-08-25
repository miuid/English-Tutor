"""Privacy-safe usage telemetry and the beta feedback package (ISS-022).

Two artifacts are built here:

- **Telemetry** — aggregated usage metrics for one student: counts, totals,
  and timestamps only. Never the student's writing, task prompts, feedback
  prose, rubric notes, or LLM input/output text (PRD §6: no third-party
  analytics on student content; everything stays local).
- **Feedback package** — a one-click JSON download a beta family can email
  when something goes wrong. It bundles the telemetry plus redacted config
  and environment metadata so a beta issue can be diagnosed without remote
  access to the family's machine.

Privacy boundary (enforced by tests in tests/test_telemetry.py):

- The student's name is deliberately excluded — the package is meant to be
  shared, so it carries year level / curriculum / focus text types only.
- Interaction logs contribute model, skill, timestamps, and character
  *lengths* — enough to spot empty or truncated LLM responses — never the
  logged prompt or completion text.
- The LLM API key and any database credentials are never included; only
  non-secret config (provider, model names, budgets) is reported.
"""

from __future__ import annotations

import platform
from datetime import UTC, datetime
from typing import Any

import fastapi
import sqlalchemy
from sqlalchemy import func, select
from sqlalchemy.orm import Session as DBSession

from app.config import Settings
from app.models import (
    Attempt,
    Feedback,
    InteractionLog,
    RubricScore,
    Session,
    Skill,
    Student,
)

PACKAGE_FORMAT = "english-tutor-feedback-package"
PACKAGE_VERSION = 1

# How much recent-history metadata the package carries for diagnosis.
RECENT_SESSION_LIMIT = 10
RECENT_INTERACTION_LIMIT = 20


def _iso(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def _skill_names(db: DBSession) -> dict[Any, str]:
    return {skill.id: skill.name for skill in db.execute(select(Skill)).scalars().all()}


def build_telemetry(db: DBSession, student: Student) -> dict[str, Any]:
    """Aggregate usage metrics for one student. Counts and totals only."""
    sessions = db.execute(
        select(Session)
        .where(Session.student_id == student.id)
        .order_by(Session.started_at)
    ).scalars().all()
    attempts = db.execute(
        select(Attempt)
        .where(Attempt.student_id == student.id)
        .order_by(Attempt.created_at)
    ).scalars().all()
    skill_names = _skill_names(db)

    attempts_by_mode: dict[str, int] = {}
    attempts_by_skill: dict[str, int] = {}
    for attempt in attempts:
        attempts_by_mode[attempt.mode] = attempts_by_mode.get(attempt.mode, 0) + 1
        if attempt.skill_id is not None:
            name = skill_names.get(attempt.skill_id, str(attempt.skill_id))
            attempts_by_skill[name] = attempts_by_skill.get(name, 0) + 1

    feedback_count = (
        db.execute(
            select(func.count(Feedback.id))
            .join(Attempt, Feedback.attempt_id == Attempt.id)
            .where(Attempt.student_id == student.id)
        ).scalar_one()
    )
    rubric_score_count = (
        db.execute(
            select(func.count(RubricScore.id))
            .join(Feedback, RubricScore.feedback_id == Feedback.id)
            .join(Attempt, Feedback.attempt_id == Attempt.id)
            .where(Attempt.student_id == student.id)
        ).scalar_one()
    )

    logs = db.execute(
        select(InteractionLog)
        .join(Session, InteractionLog.session_id == Session.id)
        .where(Session.student_id == student.id)
    ).scalars().all()
    llm_calls_by_model: dict[str, int] = {}
    llm_calls_by_skill: dict[str, int] = {}
    empty_output_calls = 0
    for log in logs:
        llm_calls_by_model[log.model] = llm_calls_by_model.get(log.model, 0) + 1
        if log.skill_id is not None:
            name = skill_names.get(log.skill_id, str(log.skill_id))
            llm_calls_by_skill[name] = llm_calls_by_skill.get(name, 0) + 1
        if not log.output.strip():
            empty_output_calls += 1

    completed = [s for s in sessions if s.ended_at is not None]
    activity_times = [s.started_at for s in sessions] + [
        a.created_at for a in attempts
    ]

    return {
        "sessions_total": len(sessions),
        "sessions_completed": len(completed),
        "practice_seconds_total": sum(s.time_spent_seconds for s in sessions),
        "attempts_total": len(attempts),
        "attempts_by_mode": attempts_by_mode,
        "attempts_by_skill": attempts_by_skill,
        "feedback_total": feedback_count,
        "rubric_scores_total": rubric_score_count,
        "llm_calls_total": len(logs),
        "llm_calls_by_model": llm_calls_by_model,
        "llm_calls_by_skill": llm_calls_by_skill,
        # Empty completions are the classic "feedback never arrived" symptom;
        # counting them makes that diagnosable without reading any content.
        "llm_empty_output_calls": empty_output_calls,
        "first_activity_at": _iso(min(activity_times) if activity_times else None),
        "last_activity_at": _iso(max(activity_times) if activity_times else None),
    }


def _database_scheme(database_url: str) -> str:
    """Report only the DB dialect ('sqlite', 'postgresql') — never the full URL."""
    return database_url.split(":", 1)[0]


def _recent_sessions(db: DBSession, student: Student) -> list[dict[str, Any]]:
    sessions = db.execute(
        select(Session)
        .where(Session.student_id == student.id)
        .order_by(Session.started_at.desc())
        .limit(RECENT_SESSION_LIMIT)
    ).scalars().all()
    return [
        {
            "started_at": _iso(session.started_at),
            "ended_at": _iso(session.ended_at),
            # The stage a session stalled on is the key breadcrumb for
            # "the loop got stuck" reports; the learning intention is
            # session content and stays out.
            "stage": session.stage,
            "time_spent_seconds": session.time_spent_seconds,
            "paused": session.paused_at is not None,
        }
        for session in sessions
    ]


def _recent_interactions(db: DBSession, student: Student) -> list[dict[str, Any]]:
    logs = db.execute(
        select(InteractionLog)
        .join(Session, InteractionLog.session_id == Session.id)
        .where(Session.student_id == student.id)
        .order_by(InteractionLog.created_at.desc())
        .limit(RECENT_INTERACTION_LIMIT)
    ).scalars().all()
    skill_names = _skill_names(db)
    return [
        {
            "created_at": _iso(log.created_at),
            "model": log.model,
            "skill": skill_names.get(log.skill_id) if log.skill_id else None,
            # Lengths only: enough to diagnose empty/truncated responses and
            # prompt-size blowouts without exposing any text.
            "input_chars": len(log.input),
            "output_chars": len(log.output),
        }
        for log in logs
    ]


def build_feedback_package(
    db: DBSession, student: Student, settings: Settings
) -> dict[str, Any]:
    """Bundle telemetry + redacted config + environment into one document.

    Safe to email to the developer: it contains no student writing, no LLM
    prompts or completions, no feedback prose, no rubric notes, no student
    name, and no credentials.
    """
    skill_names = _skill_names(db)
    return {
        "format": PACKAGE_FORMAT,
        "version": PACKAGE_VERSION,
        "generated_at": datetime.now(UTC).isoformat(),
        "environment": {
            "app_version": "0.1.0",
            "app_env": settings.app_env,
            "python_version": platform.python_version(),
            "fastapi_version": fastapi.__version__,
            "sqlalchemy_version": sqlalchemy.__version__,
            "platform": platform.platform(),
            "skills_loaded": len(skill_names),
            "skill_names": sorted(skill_names.values()),
        },
        # Non-secret config only. llm_api_key is never touched; the database
        # is reduced to its dialect so no file path or credentials leak.
        "config": {
            "llm_provider": settings.llm_provider,
            "llm_model": settings.llm_model,
            "llm_stage_models": dict(settings.llm_stage_models),
            "session_time_limit_minutes": settings.session_time_limit_minutes,
            "database": _database_scheme(settings.database_url),
        },
        # Profile context needed to reproduce year/text-type specific
        # behaviour — deliberately without the student's name.
        "student_context": {
            "year_level": student.year_level,
            "curriculum": student.curriculum,
            "focus_text_types": list(student.focus_text_types or []),
            "coach_tone": student.coach_tone,
            "weekly_goal": student.weekly_goal,
            "created_at": _iso(student.created_at),
        },
        "telemetry": build_telemetry(db, student),
        "recent_sessions": _recent_sessions(db, student),
        "recent_interactions": _recent_interactions(db, student),
    }
