"""Criterion level-up detection for one student (ISS-017).

A level-up is *derived* from the student's persisted ``RubricScore`` rows —
never stored separately — mirroring the derived-streak decision in
``app/motivation.py``. One source of truth: the celebration can never disagree
with the recorded A–E history.

Rule: a level-up fires when a criterion reaches a band (A–E letter, ``+``/``-``
modifiers ignored) **higher than any previous score for that criterion** — a
personal-best band crossing. Within-band moves (C → C+) and re-crossings after
a dip (C → B → C → B) do not re-celebrate: only the first arrival at a new
best band counts. This keeps the moment honest (PRD §5: celebrate observed
progress only, never invented progress) and prevents flip-flop re-celebration.

Tone contract (IMPLEMENTATION-PLAN-2 B4.2): the message names the real change
— criterion, from → to band, and the rubric note recorded with the new score
(the improvement mechanism) — never generic praise alone.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models import Attempt, Feedback, RubricScore

# A–E band values; higher is better. Modifiers (+/-) are ignored for band
# crossings, matching the progress view's levelValue() base letters.
BAND_VALUE: dict[str, int] = {"A": 5, "B": 4, "C": 3, "D": 2, "E": 1}


@dataclass(frozen=True)
class LevelUp:
    """One observed personal-best band crossing for a criterion."""

    criterion_name: str
    # The student's previous best level string for this criterion (e.g. "C+").
    from_level: str
    # The new best level string (e.g. "B").
    to_level: str
    # The rubric note recorded with the new score — the improvement mechanism.
    note: str | None
    scored_at: datetime
    session_id: uuid.UUID
    feedback_id: uuid.UUID


def band_of(level: str) -> str | None:
    """Normalise a rubric level string to its A–E band letter, or None."""
    letter = level.strip().upper()[:1]
    return letter if letter in BAND_VALUE else None


def build_level_ups(db: DBSession, student_id: uuid.UUID) -> list[LevelUp]:
    """Derive every personal-best band crossing, oldest first.

    Scores are grouped by criterion and walked in chronological order; an
    event is emitted when a score's band exceeds the best band seen so far
    for that criterion. Unknown/unparseable levels are skipped (they neither
    raise the best band nor produce events).
    """
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

    best_band: dict[str, int] = {}
    best_level: dict[str, str] = {}
    events: list[LevelUp] = []
    for score, session_id in rows:
        band = band_of(score.level)
        if band is None:
            continue
        value = BAND_VALUE[band]
        previous = best_band.get(score.criterion_name)
        if previous is not None and value > previous:
            events.append(
                LevelUp(
                    criterion_name=score.criterion_name,
                    from_level=best_level[score.criterion_name],
                    to_level=score.level,
                    note=score.note,
                    scored_at=score.scored_at,
                    session_id=session_id,
                    feedback_id=score.feedback_id,
                )
            )
        if previous is None or value > previous:
            best_band[score.criterion_name] = value
            best_level[score.criterion_name] = score.level
    return events
