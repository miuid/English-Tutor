"""Tests for the curriculum seed script."""

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlSession

from app.models import CurriculumOutcome
from app.seed import RUBRIC_CRITERIA, YEAR_8_OUTCOMES, seed


def test_seed_creates_year_8_outcomes(db_session: SqlSession) -> None:
    seed(db_session)
    outcomes = db_session.execute(select(CurriculumOutcome)).scalars().all()
    assert len(outcomes) == len(YEAR_8_OUTCOMES)
    codes = {o.code for o in outcomes}
    assert all(outcome["code"] in codes for outcome in YEAR_8_OUTCOMES)
    assert all(o.curriculum == "QCAA" for o in outcomes)


def test_seed_is_idempotent(db_session: SqlSession) -> None:
    seed(db_session)
    first_count = len(db_session.execute(select(CurriculumOutcome)).scalars().all())
    seed(db_session)
    second_count = len(db_session.execute(select(CurriculumOutcome)).scalars().all())
    assert first_count == second_count == len(YEAR_8_OUTCOMES)
    outcome = db_session.execute(
        select(CurriculumOutcome).where(CurriculumOutcome.code == "QCAA-Y8-ANL-01"),
    ).scalar_one()
    assert outcome.descriptor == YEAR_8_OUTCOMES[0]["descriptor"]
    assert outcome.curriculum == "QCAA"


def test_rubric_criteria_defined() -> None:
    assert len(RUBRIC_CRITERIA) == 5
    assert "Analysis (how techniques create meaning)" in RUBRIC_CRITERIA
