"""Tests for the curriculum seed script."""

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlSession

from app.models import CurriculumOutcome
from app.seed import (
    RUBRIC_CRITERIA,
    YEAR_8_OUTCOMES,
    YEAR_9_OUTCOMES,
    YEAR_10_OUTCOMES,
    seed,
)

ALL_OUTCOMES = YEAR_8_OUTCOMES + YEAR_9_OUTCOMES + YEAR_10_OUTCOMES


def test_seed_creates_year_8_outcomes(db_session: SqlSession) -> None:
    seed(db_session)
    outcomes = (
        db_session.execute(select(CurriculumOutcome).where(CurriculumOutcome.year_level == 8))
        .scalars()
        .all()
    )
    assert len(outcomes) == len(YEAR_8_OUTCOMES)
    codes = {o.code for o in outcomes}
    assert all(outcome["code"] in codes for outcome in YEAR_8_OUTCOMES)
    assert all(o.curriculum == "QCAA" for o in outcomes)


def test_seed_creates_year_9_10_outcomes(db_session: SqlSession) -> None:
    seed(db_session)
    year_9 = (
        db_session.execute(select(CurriculumOutcome).where(CurriculumOutcome.year_level == 9))
        .scalars()
        .all()
    )
    year_10 = (
        db_session.execute(select(CurriculumOutcome).where(CurriculumOutcome.year_level == 10))
        .scalars()
        .all()
    )
    assert len(year_9) == len(YEAR_9_OUTCOMES)
    assert len(year_10) == len(YEAR_10_OUTCOMES)
    assert {o.code for o in year_9} == {o["code"] for o in YEAR_9_OUTCOMES}
    assert {o.code for o in year_10} == {o["code"] for o in YEAR_10_OUTCOMES}
    for outcome in [*year_9, *year_10]:
        assert outcome.curriculum == "QCAA"
        assert outcome.text_type == "analytical"
    # Year 9-10 band shift (reaserch.md: Year 9 marking criteria): analysis of
    # representations / positioning replaces Year 8's explain-the-effect focus.
    year_9_descriptors = " ".join(o.descriptor for o in year_9)
    assert "representation" in year_9_descriptors
    assert "positions the reader" in year_9_descriptors


def test_seed_is_idempotent(db_session: SqlSession) -> None:
    seed(db_session)
    first_count = len(db_session.execute(select(CurriculumOutcome)).scalars().all())
    seed(db_session)
    second_count = len(db_session.execute(select(CurriculumOutcome)).scalars().all())
    assert first_count == second_count == len(ALL_OUTCOMES)
    outcome = db_session.execute(
        select(CurriculumOutcome).where(CurriculumOutcome.code == "QCAA-Y8-ANL-01"),
    ).scalar_one()
    assert outcome.descriptor == YEAR_8_OUTCOMES[0]["descriptor"]
    assert outcome.curriculum == "QCAA"
    year_9_outcome = db_session.execute(
        select(CurriculumOutcome).where(CurriculumOutcome.code == "QCAA-Y9-ANL-01"),
    ).scalar_one()
    assert year_9_outcome.descriptor == YEAR_9_OUTCOMES[0]["descriptor"]
    assert year_9_outcome.year_level == 9


def test_rubric_criteria_defined() -> None:
    assert len(RUBRIC_CRITERIA) == 5
    assert "Analysis (how techniques create meaning)" in RUBRIC_CRITERIA
