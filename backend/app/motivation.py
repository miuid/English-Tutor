"""Streak and weekly-goal motivation state for one student (ISS-016).

The streak is *derived* from the student's persisted ``Session`` rows — a
practice day is any local calendar date with at least one session (daily
loop, baseline, or weekly mock all count). Deriving instead of storing keeps
one source of truth: the streak can never disagree with session history.

Tone contract (IMPLEMENTATION-PLAN-2 B4.1): motivation serves practice. A
lapsed streak is a recovery moment ("welcome back — one session starts a
fresh streak"), never a penalty. There are no points, shops, or leaderboards.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models import Session


@dataclass(frozen=True)
class MotivationSummary:
    """The per-student motivation state surfaced by the API."""

    current_streak: int
    # True when the student has practised before but the run lapsed — the UI
    # answers with a recovery prompt, never a penalty.
    streak_broken: bool
    weekly_goal: int
    sessions_this_week: int
    goal_met: bool
    last_activity_date: date | None


def build_motivation(
    db: DBSession,
    student_id: uuid.UUID,
    weekly_goal: int,
    *,
    now: datetime | None = None,
) -> MotivationSummary:
    """Compute the streak and weekly-goal state for one student.

    ``now`` is injectable for tests; the week runs Monday-Sunday on the
    server's local calendar, matching the session time budget's notion of
    "today" (``InteractiveLoop._local_date``).
    """
    aware_now = _as_aware(now) or datetime.now(UTC)
    today = aware_now.astimezone().date()

    started_rows = (
        db.execute(
            select(Session.started_at).where(Session.student_id == student_id)
        )
        .scalars()
        .all()
    )
    practice_dates = [
        aware.astimezone().date()
        for started in started_rows
        if (aware := _as_aware(started)) is not None
    ]
    if not practice_dates:
        return MotivationSummary(
            current_streak=0,
            streak_broken=False,
            weekly_goal=weekly_goal,
            sessions_this_week=0,
            goal_met=False,
            last_activity_date=None,
        )

    practice_days = set(practice_dates)
    streak = _current_streak(practice_days, today)
    week_start = today - timedelta(days=today.weekday())  # Monday
    sessions_this_week = sum(1 for day in practice_dates if week_start <= day <= today)

    return MotivationSummary(
        current_streak=streak,
        # Any prior activity with no live run means the streak lapsed.
        streak_broken=streak == 0,
        weekly_goal=weekly_goal,
        sessions_this_week=sessions_this_week,
        goal_met=sessions_this_week >= weekly_goal,
        last_activity_date=max(practice_days),
    )


def _current_streak(practice_days: set[date], today: date) -> int:
    """Consecutive practice days ending today or yesterday (0 if lapsed).

    Yesterday counts as alive so the streak only breaks after a full missed
    day — one session today or tomorrow always continues or restarts it.
    """
    if today in practice_days:
        anchor = today
    elif today - timedelta(days=1) in practice_days:
        anchor = today - timedelta(days=1)
    else:
        return 0
    streak = 0
    day = anchor
    while day in practice_days:
        streak += 1
        day -= timedelta(days=1)
    return streak


def _as_aware(value: datetime | None) -> datetime | None:
    """SQLite returns naive datetimes; treat them as UTC."""
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
