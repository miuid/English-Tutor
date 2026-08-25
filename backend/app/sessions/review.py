"""Build the spaced-review history digest from a student's learning record.

The digest is the only history the ``spaced-review`` skill ever sees: a compact,
prompt-ready summary of the student's ``rubric_score`` and coaching
(``interaction_log``/attempt) history. Keeping the builder here means the
interactive loop and the scripted orchestrator generate identical inputs.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models import Attempt, Feedback, RubricScore, Session
from app.models import Skill as SkillRow

# Digest caps: enough signal for 2-3 warm-up items, never a data dump.
MAX_CRITERIA_LINES = 6
MAX_COACHED_LINES = 3

COLD_START_LINE = "No prior sessions — this is the student's first daily loop."

# A–E rank for weakest-first ordering; unknown levels sort last.
_LEVEL_RANK = {"E": 0, "D": 1, "C": 2, "B": 3, "A": 4}


def build_review_history(
    db: DBSession,
    student_id: uuid.UUID,
    *,
    now: datetime | None = None,
) -> str:
    """Return the compact review-history digest for one student.

    Shape (see ``skills/spaced-review/references/shared/retrieval-guide.md``)::

        Days since last session: <N | 0>
        Latest criterion levels (weakest first):
        - <criterion name>: <level>
        Recently coached: <skill> (<date>), ...

    A student with no finished sessions gets the cold-start line only.
    """
    now = now or datetime.now(UTC)

    last_session = db.execute(
        select(Session)
        .where(Session.student_id == student_id, Session.ended_at.is_not(None))
        .order_by(Session.ended_at.desc())
        .limit(1)
    ).scalar_one_or_none()
    if last_session is None:
        return COLD_START_LINE

    last_activity = _as_aware(last_session.ended_at) or now
    days_since = max((now.date() - last_activity.date()).days, 0)

    lines = [f"Days since last session: {days_since}"]

    criterion_lines = _latest_criterion_levels(db, student_id)
    if criterion_lines:
        lines.append("Latest criterion levels (weakest first):")
        lines.extend(f"- {line}" for line in criterion_lines)

    coached = _recently_coached(db, student_id)
    if coached:
        lines.append(f"Recently coached: {', '.join(coached)}")

    return "\n".join(lines)


def _latest_criterion_levels(db: DBSession, student_id: uuid.UUID) -> list[str]:
    """Latest level per criterion, weakest first (ties: most recent first)."""
    rows = (
        db.execute(
            select(RubricScore.criterion_name, RubricScore.level, Feedback.created_at)
            .join(Feedback, RubricScore.feedback_id == Feedback.id)
            .join(Attempt, Feedback.attempt_id == Attempt.id)
            .where(Attempt.student_id == student_id)
            .order_by(Feedback.created_at.desc())
        )
        .all()
    )
    latest: dict[str, tuple[str, datetime | None]] = {}
    for name, level, scored_at in rows:
        if name not in latest:  # rows arrive most-recent-first
            latest[name] = (level, scored_at)

    def sort_key(item: tuple[str, tuple[str, datetime | None]]) -> tuple[int, float]:
        name, (level, scored_at) = item
        rank = _LEVEL_RANK.get(level.strip().upper()[:1], len(_LEVEL_RANK))
        timestamp = scored_at.timestamp() if scored_at is not None else 0.0
        return (rank, -timestamp)

    ordered = sorted(latest.items(), key=sort_key)
    return [f"{name}: {level}" for name, (level, _) in ordered[:MAX_CRITERIA_LINES]]


def _recently_coached(db: DBSession, student_id: uuid.UUID) -> list[str]:
    """The most recent coach-skill turns as ``<skill> (<local date>)`` strings."""
    rows = (
        db.execute(
            select(SkillRow.name, Attempt.created_at)
            .join(SkillRow, Attempt.skill_id == SkillRow.id)
            .where(Attempt.student_id == student_id, Attempt.task_type == "coach")
            .order_by(Attempt.created_at.desc())
        )
        .all()
    )
    seen: list[str] = []
    for skill_name, created_at in rows:
        if any(entry.startswith(f"{skill_name} (") for entry in seen):
            continue  # one entry per skill, most recent only
        aware = _as_aware(created_at)
        date_label = aware.astimezone().date().isoformat() if aware else "unknown date"
        seen.append(f"{skill_name} ({date_label})")
        if len(seen) >= MAX_COACHED_LINES:
            break
    return seen


def _as_aware(value: datetime | None) -> datetime | None:
    """SQLite returns naive datetimes; treat them as UTC."""
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
