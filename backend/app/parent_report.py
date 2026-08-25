"""Weekly parent report with the D3 privacy boundary (ISS-019).

Parents see trends, levels, time, and goals — never the student's essay
text or tutor feedback prose (IMPLEMENTATION-PLAN-2 B5.1, PRD §7 deferred
parent layer, ERD Privacy & retention). The report is *derived* from
persisted sessions and rubric scores, mirroring the derived-streak decision
in ``app/motivation.py``: one source of truth, nothing extra stored.

Privacy contract: the builder reads ``Attempt``/``Feedback`` only to reach
rubric scores; no ``student_text``, ``task_prompt``, feedback prose, or
rubric notes ever leave this module. The printable HTML is rendered from
the same ``ParentReport`` value, so the boundary is enforced in exactly
one place.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from html import escape

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.level_ups import BAND_VALUE, band_of, build_level_ups
from app.models import Attempt, Feedback, RubricScore, Session, Student


@dataclass(frozen=True)
class TrendPoint:
    """One scored data point for a criterion, local calendar day."""

    scored_on: date
    level: str


@dataclass(frozen=True)
class CriterionTrend:
    """The A–E story for one criterion, oldest score first."""

    criterion_name: str
    latest_level: str
    previous_level: str | None  # the score before the latest, if any
    direction: str  # "up" | "down" | "steady" | "new"
    points: list[TrendPoint]


@dataclass(frozen=True)
class ParentReport:
    """Everything a parent sees for one week — and nothing more (D3)."""

    student_id: uuid.UUID
    student_name: str
    year_level: int
    curriculum: str
    week_start: date  # Monday of the current week, local calendar
    week_end: date  # today, local calendar
    sessions_this_week: int
    practice_seconds_this_week: int
    weekly_goal: int
    goal_met: bool
    shared_goal: str | None  # the family's agreed weekly focus (ISS-020) — a goal, not content
    trends: list[CriterionTrend]
    highlight: str | None  # the week's single most encouraging moment
    next_week_suggestion: str


def build_parent_report(
    db: DBSession,
    student: Student,
    *,
    now: datetime | None = None,
) -> ParentReport:
    """Derive the weekly parent report for one student.

    ``now`` is injectable for tests; the week runs Monday-to-today on the
    server's local calendar, matching ``build_motivation``'s week.
    """
    aware_now = _as_aware(now) or datetime.now(UTC)
    today = aware_now.astimezone().date()
    week_start = today - timedelta(days=today.weekday())  # Monday

    sessions = (
        db.execute(
            select(Session)
            .where(Session.student_id == student.id)
            .order_by(Session.started_at)
        )
        .scalars()
        .all()
    )
    week_sessions = [
        session
        for session in sessions
        if (day := _local_date_of(session.started_at)) is not None
        and week_start <= day <= today
    ]
    sessions_this_week = len(week_sessions)
    practice_seconds = sum(s.time_spent_seconds for s in week_sessions)
    goal_met = sessions_this_week >= student.weekly_goal

    score_rows = (
        db.execute(
            select(RubricScore)
            .join(Feedback, RubricScore.feedback_id == Feedback.id)
            .join(Attempt, Feedback.attempt_id == Attempt.id)
            .where(Attempt.student_id == student.id)
            .order_by(RubricScore.scored_at)
        )
        .scalars()
        .all()
    )
    by_criterion: dict[str, list[RubricScore]] = {}
    for score in score_rows:
        by_criterion.setdefault(score.criterion_name, []).append(score)
    trends = [
        _build_trend(name, scores)
        for name, scores in sorted(by_criterion.items())
    ]

    highlight = _build_highlight(
        db,
        student,
        week_start=week_start,
        today=today,
        sessions_this_week=sessions_this_week,
        goal_met=goal_met,
    )
    suggestion = _build_suggestion(student, sessions_this_week, trends)

    return ParentReport(
        student_id=student.id,
        student_name=student.name,
        year_level=student.year_level,
        curriculum=student.curriculum,
        week_start=week_start,
        week_end=today,
        sessions_this_week=sessions_this_week,
        practice_seconds_this_week=practice_seconds,
        weekly_goal=student.weekly_goal,
        goal_met=goal_met,
        shared_goal=student.shared_goal,
        trends=trends,
        highlight=highlight,
        next_week_suggestion=suggestion,
    )


def _build_trend(criterion_name: str, scores: list[RubricScore]) -> CriterionTrend:
    points = [
        TrendPoint(scored_on=day, level=score.level)
        for score in scores
        if (day := _local_date_of(score.scored_at)) is not None
    ]
    latest_level = scores[-1].level
    previous_level = scores[-2].level if len(scores) > 1 else None
    return CriterionTrend(
        criterion_name=criterion_name,
        latest_level=latest_level,
        previous_level=previous_level,
        direction=_direction(latest_level, previous_level),
        points=points,
    )


def _build_highlight(
    db: DBSession,
    student: Student,
    *,
    week_start: date,
    today: date,
    sessions_this_week: int,
    goal_met: bool,
) -> str | None:
    """One honest, specific encouraging moment — never invented progress."""
    events = [
        event
        for event in build_level_ups(db, student.id)
        if (day := _local_date_of(event.scored_at)) is not None
        and week_start <= day <= today
    ]
    if events:
        latest = events[-1]
        return (
            f"{latest.criterion_name} lifted "
            f"{latest.from_level} → {latest.to_level} this week."
        )
    if goal_met and sessions_this_week > 0:
        return (
            f"{student.name} met the weekly goal — "
            f"{sessions_this_week} sessions this week."
        )
    return None


def _build_suggestion(
    student: Student,
    sessions_this_week: int,
    trends: list[CriterionTrend],
) -> str:
    """One supportive, achievable next step — never a laundry list."""
    if sessions_this_week < student.weekly_goal:
        remaining = student.weekly_goal - sessions_this_week
        plural = "s" if remaining != 1 else ""
        return (
            f"Aim for the weekly goal of {student.weekly_goal} sessions — "
            f"{remaining} more short session{plural} this week. "
            "Ten to fifteen minutes is plenty."
        )
    dips = [trend for trend in trends if trend.direction == "down"]
    if dips:
        dip = dips[0]
        return (
            f"Revisit {dip.criterion_name} — it moved "
            f"{dip.previous_level} → {dip.latest_level} recently. "
            "One focused session can steady it."
        )
    weakest = _weakest_trend(trends)
    if weakest is not None:
        return (
            f"Next growth area: {weakest.criterion_name} "
            f"(currently {weakest.latest_level}). "
            "One targeted practice session can move it."
        )
    return "Keep the rhythm going — regular short practice is working."


def _weakest_trend(trends: list[CriterionTrend]) -> CriterionTrend | None:
    """The lowest-band criterion, unless everything is already at A."""
    valued = [
        (value, trend)
        for trend in trends
        if (value := _level_value(trend.latest_level)) is not None
    ]
    if not valued:
        return None
    valued.sort(key=lambda pair: pair[0])
    value, trend = valued[0]
    return trend if value < float(BAND_VALUE["A"]) else None


def _direction(latest_level: str, previous_level: str | None) -> str:
    if previous_level is None:
        return "new"
    latest = _level_value(latest_level)
    previous = _level_value(previous_level)
    if latest is None or previous is None:
        return "steady"
    if latest - previous > 0.05:
        return "up"
    if previous - latest > 0.05:
        return "down"
    return "steady"


def _level_value(level: str) -> float | None:
    """Numeric value of an A–E level; +/- modifiers nudge within the band."""
    band = band_of(level)
    if band is None:
        return None
    value = float(BAND_VALUE[band])
    if "+" in level:
        return value + 0.15
    if "-" in level or "–" in level:
        return value - 0.15
    return value


def _local_date_of(value: datetime | None) -> date | None:
    aware = _as_aware(value)
    return aware.astimezone().date() if aware is not None else None


def _as_aware(value: datetime | None) -> datetime | None:
    """SQLite returns naive datetimes; treat them as UTC."""
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


_DIRECTION_GLYPH = {"up": "↑", "down": "↓", "steady": "→", "new": "·"}


def _format_day(day: date) -> str:
    return day.strftime("%a %-d %b")


def render_parent_report_html(report: ParentReport) -> str:
    """Render the printable one-page report from the same derived data.

    Every interpolated value is HTML-escaped. The page intentionally shows
    no essay text and no feedback prose — the D3 privacy boundary — and
    says so on the page. Parents print to PDF from the browser.
    """
    name = escape(report.student_name)
    minutes = report.practice_seconds_this_week // 60
    goal_chip = (
        f"{report.sessions_this_week} of {report.weekly_goal} sessions this week"
        + (" — goal reached ⭐" if report.goal_met else "")
    )
    shared_goal_chip = (
        f'<span class="chip">Shared goal: {escape(report.shared_goal)}</span>'
        if report.shared_goal
        else ""
    )
    trend_rows = "".join(
        "<tr>"
        f"<td>{escape(trend.criterion_name)}</td>"
        f"<td class='level'>{escape(trend.latest_level)}</td>"
        f"<td class='dir'>{_DIRECTION_GLYPH.get(trend.direction, '→')}"
        f" {escape(trend.direction)}</td>"
        f"<td class='muted'>{_format_points(trend)}</td>"
        "</tr>"
        for trend in report.trends
    )
    trends_block = (
        "<table class='trends'><thead><tr>"
        "<th>Criterion</th><th>Latest</th><th>Trend</th><th>Recent scores</th>"
        "</tr></thead>"
        f"<tbody>{trend_rows}</tbody></table>"
        if report.trends
        else (
            "<p class='muted'>No graded writing yet — the first session "
            "will start the trend lines.</p>"
        )
    )
    highlight_block = (
        f"<div class='highlight'><strong>This week's highlight:</strong> "
        f"{escape(report.highlight)}</div>"
        if report.highlight
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Weekly report — {name}</title>
<style>
  body {{ font-family: -apple-system, 'Segoe UI', Roboto, sans-serif; color: #1a1a2e;
         max-width: 720px; margin: 2rem auto; padding: 0 1rem; line-height: 1.45; }}
  h1 {{ font-size: 1.4rem; margin-bottom: 0.2rem; }}
  h2 {{ font-size: 1.05rem; margin: 1.4rem 0 0.5rem; }}
  .muted {{ color: #666; }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.8rem 0; }}
  .chip {{ border: 1px solid #d0d0dd; border-radius: 999px;
    padding: 0.25rem 0.8rem; font-size: 0.9rem; }}
  table.trends {{ width: 100%; border-collapse: collapse; font-size: 0.95rem; }}
  table.trends th, table.trends td {{ text-align: left; padding: 0.4rem 0.6rem;
    border-bottom: 1px solid #e4e4ee; }}
  td.level {{ font-weight: 700; }}
  .highlight {{ background: #f2f8f0; border: 1px solid #cfe3c8; border-radius: 8px;
    padding: 0.6rem 0.9rem; margin: 0.8rem 0; }}
  .suggestion {{ background: #f0f5fb; border: 1px solid #c9dcf2; border-radius: 8px;
    padding: 0.6rem 0.9rem; margin: 0.8rem 0; }}
  .privacy {{ font-size: 0.85rem; color: #666; margin-top: 1.6rem;
    border-top: 1px solid #e4e4ee; padding-top: 0.8rem; }}
  .print-btn {{ margin-top: 1rem; padding: 0.45rem 1.1rem; font-size: 0.95rem;
    border: 1px solid #9ab; border-radius: 6px; background: #fff; cursor: pointer; }}
  @media print {{ .print-btn {{ display: none; }} body {{ margin: 0; }} }}
</style>
</head>
<body>
<h1>Weekly report — {name}</h1>
<p class="muted">Year {report.year_level} · {escape(report.curriculum)} · Week of
{_format_day(report.week_start)} – {_format_day(report.week_end)}</p>

<div class="chips">
  <span class="chip">{escape(goal_chip)}</span>
  <span class="chip">{minutes} min practice this week</span>
  {shared_goal_chip}
</div>

{highlight_block}

<h2>How the writing is tracking</h2>
{trends_block}

<h2>Suggested focus for next week</h2>
<div class="suggestion">{escape(report.next_week_suggestion)}</div>

<p class="privacy">This report shows progress trends only. Your child's essays and
the tutor's detailed feedback stay in the student view by design — ask them to walk
you through a piece they're proud of.</p>

<button class="print-btn" onclick="window.print()">Print / save as PDF</button>
</body>
</html>
"""


def _format_points(trend: CriterionTrend) -> str:
    """Compact 'C (12 Aug) → B (19 Aug)' history for the print table."""
    recent = trend.points[-4:]
    return escape(" → ".join(f"{p.level} ({_format_day(p.scored_on)})" for p in recent))
