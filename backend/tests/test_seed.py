"""Tests for the curriculum seed script."""

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlSession

from app.models import CurriculumOutcome
from app.seed import (
    RUBRIC_CRITERIA,
    YEAR_8_IMAGINATIVE_OUTCOMES,
    YEAR_8_OUTCOMES,
    YEAR_8_PERSUASIVE_OUTCOMES,
    YEAR_9_IMAGINATIVE_OUTCOMES,
    YEAR_9_OUTCOMES,
    YEAR_9_PERSUASIVE_OUTCOMES,
    YEAR_10_IMAGINATIVE_OUTCOMES,
    YEAR_10_OUTCOMES,
    YEAR_10_PERSUASIVE_OUTCOMES,
    seed,
)

ALL_OUTCOMES = (
    YEAR_8_OUTCOMES
    + YEAR_9_OUTCOMES
    + YEAR_10_OUTCOMES
    + YEAR_8_PERSUASIVE_OUTCOMES
    + YEAR_9_PERSUASIVE_OUTCOMES
    + YEAR_10_PERSUASIVE_OUTCOMES
    + YEAR_8_IMAGINATIVE_OUTCOMES
    + YEAR_9_IMAGINATIVE_OUTCOMES
    + YEAR_10_IMAGINATIVE_OUTCOMES
)


def test_seed_creates_year_8_outcomes(db_session: SqlSession) -> None:
    seed(db_session)
    outcomes = (
        db_session.execute(
            select(CurriculumOutcome).where(
                CurriculumOutcome.year_level == 8,
                CurriculumOutcome.text_type == "analytical",
            )
        )
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
        db_session.execute(
            select(CurriculumOutcome).where(
                CurriculumOutcome.year_level == 9,
                CurriculumOutcome.text_type == "analytical",
            )
        )
        .scalars()
        .all()
    )
    year_10 = (
        db_session.execute(
            select(CurriculumOutcome).where(
                CurriculumOutcome.year_level == 10,
                CurriculumOutcome.text_type == "analytical",
            )
        )
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


def test_seed_creates_persuasive_outcomes(db_session: SqlSession) -> None:
    seed(db_session)
    persuasive = (
        db_session.execute(
            select(CurriculumOutcome).where(CurriculumOutcome.text_type == "persuasive")
        )
        .scalars()
        .all()
    )
    expected = (
        YEAR_8_PERSUASIVE_OUTCOMES + YEAR_9_PERSUASIVE_OUTCOMES + YEAR_10_PERSUASIVE_OUTCOMES
    )
    assert len(persuasive) == len(expected)
    assert {o.code for o in persuasive} == {o["code"] for o in expected}
    for outcome in persuasive:
        assert outcome.curriculum == "QCAA"
    by_year = {year: [o for o in persuasive if o.year_level == year] for year in (8, 9, 10)}
    assert all(len(rows) == 4 for rows in by_year.values())
    # Year 9-10 band shift (reaserch.md: Year 9 marking criteria — substantiated
    # viewpoints, rhetorical strategies): rebuttal and escalation replace Year 8's
    # develop-one-reason focus.
    year_9_descriptors = " ".join(o.descriptor for o in by_year[9])
    assert "rebut" in year_9_descriptors
    assert "rhetorical" in year_9_descriptors
    year_8_descriptors = " ".join(o.descriptor for o in by_year[8])
    assert "call to action" in year_8_descriptors
    # Analytical outcomes are untouched by the persuasive seed pass.
    analytical = (
        db_session.execute(
            select(CurriculumOutcome).where(CurriculumOutcome.text_type == "analytical")
        )
        .scalars()
        .all()
    )
    assert {o.code for o in analytical} == {
        o["code"] for o in YEAR_8_OUTCOMES + YEAR_9_OUTCOMES + YEAR_10_OUTCOMES
    }


def test_seed_creates_imaginative_outcomes(db_session: SqlSession) -> None:
    seed(db_session)
    imaginative = (
        db_session.execute(
            select(CurriculumOutcome).where(CurriculumOutcome.text_type == "imaginative")
        )
        .scalars()
        .all()
    )
    expected = (
        YEAR_8_IMAGINATIVE_OUTCOMES
        + YEAR_9_IMAGINATIVE_OUTCOMES
        + YEAR_10_IMAGINATIVE_OUTCOMES
    )
    assert len(imaginative) == len(expected)
    assert {o.code for o in imaginative} == {o["code"] for o in expected}
    for outcome in imaginative:
        assert outcome.curriculum == "QCAA"
    by_year = {year: [o for o in imaginative if o.year_level == year] for year in (8, 9, 10)}
    assert all(len(rows) == 4 for rows in by_year.values())
    # Year 9-10 band shift (reaserch.md: Year 9 marking criteria — purposeful
    # selection and considered experimentation with structures, language
    # features and voice): deliberate experimentation and motif replace
    # Year 8's one-complication / show-don't-tell focus.
    year_9_descriptors = " ".join(o.descriptor for o in by_year[9])
    assert "experiment" in year_9_descriptors
    assert "motif" in year_9_descriptors
    year_8_descriptors = " ".join(o.descriptor for o in by_year[8])
    assert "complication" in year_8_descriptors
    # Analytical and persuasive outcomes are untouched by the imaginative pass.
    other = (
        db_session.execute(
            select(CurriculumOutcome).where(CurriculumOutcome.text_type != "imaginative")
        )
        .scalars()
        .all()
    )
    assert {o.code for o in other} == {
        o["code"]
        for o in YEAR_8_OUTCOMES
        + YEAR_9_OUTCOMES
        + YEAR_10_OUTCOMES
        + YEAR_8_PERSUASIVE_OUTCOMES
        + YEAR_9_PERSUASIVE_OUTCOMES
        + YEAR_10_PERSUASIVE_OUTCOMES
    }


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
