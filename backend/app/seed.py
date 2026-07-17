"""Seed Year 8 analytical curriculum outcomes and rubric criteria."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CurriculumOutcome

YEAR = 8
TEXT_TYPE = "analytical"
CURRICULUM = "QCAA"

RUBRIC_CRITERIA = [
    "Understanding of text / ideas",
    "Analysis (how techniques create meaning)",
    "Use of evidence",
    "Structure & cohesion",
    "Language & vocabulary",
]

YEAR_8_OUTCOMES = [
    {
        "code": "QCAA-Y8-ANL-01",
        "strand": "Structure and organisation",
        "descriptor": (
            "I can structure an analytical paragraph with a clear point, embedded evidence, "
            "and a link back to the question."
        ),
    },
    {
        "code": "QCAA-Y8-ANL-02",
        "strand": "Analysis and interpretation",
        "descriptor": (
            "I can explain how a writer's language technique creates a specific effect "
            "on the reader."
        ),
    },
    {
        "code": "QCAA-Y8-ANL-03",
        "strand": "Vocabulary and language",
        "descriptor": (
            "I can use precise, analytical vocabulary instead of vague or repeated words."
        ),
    },
    {
        "code": "QCAA-Y8-ANL-04",
        "strand": "Essay-level response",
        "descriptor": (
            "I can maintain a clear position across multiple paragraphs in an analytical essay."
        ),
    },
]


def seed(session: Session) -> list[CurriculumOutcome]:
    """Idempotently seed Year 8 analytical curriculum outcomes."""
    outcomes: list[CurriculumOutcome] = []
    for data in YEAR_8_OUTCOMES:
        existing = session.execute(
            select(CurriculumOutcome).where(CurriculumOutcome.code == data["code"]),
        ).scalar_one_or_none()
        if existing:
            existing.strand = data["strand"]
            existing.descriptor = data["descriptor"]
            existing.year_level = YEAR
            existing.text_type = TEXT_TYPE
            outcomes.append(existing)
        else:
            outcome = CurriculumOutcome(
                code=data["code"],
                strand=data["strand"],
                year_level=YEAR,
                text_type=TEXT_TYPE,
                curriculum=CURRICULUM,
                descriptor=data["descriptor"],
            )
            session.add(outcome)
            outcomes.append(outcome)
    session.commit()
    return outcomes
