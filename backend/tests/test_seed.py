"""Tests for the curriculum seed script."""

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlSession

from app.models import CurriculumOutcome
from app.seed import (
    RUBRIC_CRITERIA,
    SENIOR_EA_OUTCOMES,
    SENIOR_IA1_OUTCOMES,
    SENIOR_IA2_OUTCOMES,
    SENIOR_IA3_OUTCOMES,
    SENIOR_UNIT_OUTCOMES,
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

SENIOR_INSTRUMENT_OUTCOMES = (
    SENIOR_IA1_OUTCOMES + SENIOR_IA2_OUTCOMES + SENIOR_IA3_OUTCOMES + SENIOR_EA_OUTCOMES
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
    + SENIOR_UNIT_OUTCOMES
    + SENIOR_INSTRUMENT_OUTCOMES
)

JUNIOR_YEARS = (8, 9, 10)


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
            select(CurriculumOutcome).where(
                CurriculumOutcome.text_type == "persuasive",
                CurriculumOutcome.year_level.in_(JUNIOR_YEARS),
            )
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
            select(CurriculumOutcome).where(
                CurriculumOutcome.text_type == "analytical",
                CurriculumOutcome.year_level.in_(JUNIOR_YEARS),
            )
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
            select(CurriculumOutcome).where(
                CurriculumOutcome.text_type == "imaginative",
                CurriculumOutcome.year_level.in_(JUNIOR_YEARS),
            )
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
            select(CurriculumOutcome).where(
                CurriculumOutcome.text_type != "imaginative",
                CurriculumOutcome.year_level.in_(JUNIOR_YEARS),
            )
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


def test_seed_creates_senior_qce_outcomes(db_session: SqlSession) -> None:
    seed(db_session)
    senior = (
        db_session.execute(
            select(CurriculumOutcome).where(CurriculumOutcome.year_level.in_((11, 12)))
        )
        .scalars()
        .all()
    )
    expected = SENIOR_UNIT_OUTCOMES + SENIOR_INSTRUMENT_OUTCOMES
    assert {o.code for o in senior} == {o["code"] for o in expected}
    for outcome in senior:
        assert outcome.curriculum == "QCAA"
    # Units 1-2 are Year 11 formative; Units 3-4 and every instrument are Year 12.
    units = [o for o in senior if o.text_type == "framework"]
    assert len(units) == len(SENIOR_UNIT_OUTCOMES)
    assert {o.code for o in units if o.year_level == 11} == {"QCAA-Y11-U1", "QCAA-Y11-U2"}
    assert {o.code for o in units if o.year_level == 12} == {"QCAA-Y12-U3", "QCAA-Y12-U4"}
    instruments = [o for o in senior if o.text_type != "framework"]
    assert len(instruments) == len(SENIOR_INSTRUMENT_OUTCOMES)
    assert all(o.year_level == 12 for o in instruments)
    # Instrument descriptors carry the official instrument name, 25% weight and
    # the three ISMG criteria (English 2025 v1.3, Assessment section).
    criteria = ("Knowledge application", "Organisation and development", "Textual features")
    for outcome in instruments:
        assert "25%" in outcome.descriptor
        assert "Source: English 2025 v1.3" in outcome.descriptor
    internal = [o for o in instruments if o.code != "QCAA-Y12-EA"]
    for outcome in internal:
        assert all(criterion in outcome.descriptor for criterion in criteria)
    by_code = {o.code: o for o in instruments}
    # IA1 is a spoken persuasive response; IA3 is the imaginative examination;
    # IA2 and the EA are the analytical written instruments (English 2025 v1.3).
    assert by_code["QCAA-Y12-IA1"].text_type == "persuasive"
    assert "Spoken persuasive response" in by_code["QCAA-Y12-IA1"].descriptor
    assert by_code["QCAA-Y12-IA2"].text_type == "analytical"
    assert by_code["QCAA-Y12-IA3"].text_type == "imaginative"
    assert by_code["QCAA-Y12-EA"].text_type == "analytical"
    assert "developed and marked by the QCAA" in by_code["QCAA-Y12-EA"].descriptor
    # Year 8-10 rows are untouched by the senior seed pass.
    junior = (
        db_session.execute(
            select(CurriculumOutcome).where(
                CurriculumOutcome.year_level.in_(JUNIOR_YEARS)
            )
        )
        .scalars()
        .all()
    )
    assert len(junior) == len(ALL_OUTCOMES) - len(expected)


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
