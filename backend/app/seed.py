"""Seed QCAA analytical curriculum outcomes and rubric criteria.

Seeded bands: Year 8 (verbatim scope from MVP) and Year 9–10. Year 9
descriptors trace to reaserch.md (Year 9 marking criteria: considered
analysis of representations, contexts and positioning; discriminating
thesis; formal register) and the year-9-10 reference packs shipped in
ISS-002. Year 10 descriptors are *derived* from the Year 9 elaborations
one band up (provenance note Q-001 — provisional until official QCAA
sources are imported).
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CurriculumOutcome

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

# Year 9: trace to reaserch.md Year 9 marking criteria and
# skills/set-success-criteria/references/analytical/year-9-10/criteria-bank.md.
YEAR_9_OUTCOMES = [
    {
        "code": "QCAA-Y9-ANL-01",
        "strand": "Structure and organisation",
        "descriptor": (
            "I can build an analytical essay around a clear, arguable thesis, with each "
            "paragraph's point advancing that thesis."
        ),
    },
    {
        "code": "QCAA-Y9-ANL-02",
        "strand": "Analysis and interpretation",
        "descriptor": (
            "I can analyse how a writer constructs a representation (of a person, place, "
            "event or idea) and how the text positions the reader."
        ),
    },
    {
        "code": "QCAA-Y9-ANL-03",
        "strand": "Vocabulary and language",
        "descriptor": (
            "I can write in a formal academic register using precise analytical "
            "metalanguage (e.g. 'positions', 'representation', 'motif')."
        ),
    },
    {
        "code": "QCAA-Y9-ANL-04",
        "strand": "Essay-level response",
        "descriptor": (
            "I can link a writer's choices to their historical, social or cultural "
            "context across a sustained analytical response (600-800 words)."
        ),
    },
]

# Year 10: derived from the Year 9 elaborations one band up (Q-001 —
# derived, not verbatim; provisional until official sources are imported).
YEAR_10_OUTCOMES = [
    {
        "code": "QCAA-Y10-ANL-01",
        "strand": "Structure and organisation",
        "descriptor": (
            "I can sustain a discriminating thesis across an extended or comparative "
            "analytical response."
        ),
    },
    {
        "code": "QCAA-Y10-ANL-02",
        "strand": "Analysis and interpretation",
        "descriptor": (
            "I can evaluate how representations and reader positioning shape a response, "
            "connecting a writer's technique to its context."
        ),
    },
    {
        "code": "QCAA-Y10-ANL-03",
        "strand": "Vocabulary and language",
        "descriptor": (
            "I can maintain a controlled formal register with discriminating, varied "
            "analytical vocabulary choices."
        ),
    },
    {
        "code": "QCAA-Y10-ANL-04",
        "strand": "Essay-level response",
        "descriptor": (
            "I can integrate well-chosen evidence and analysis purposefully across a "
            "sustained essay-length response."
        ),
    },
]

# (year_level, outcomes) pairs seeded in one idempotent pass.
_OUTCOME_SETS: list[tuple[int, list[dict[str, str]]]] = [
    (8, YEAR_8_OUTCOMES),
    (9, YEAR_9_OUTCOMES),
    (10, YEAR_10_OUTCOMES),
]


def seed(session: Session) -> list[CurriculumOutcome]:
    """Idempotently seed the QCAA analytical curriculum outcomes (Year 8-10)."""
    outcomes: list[CurriculumOutcome] = []
    for year_level, outcome_set in _OUTCOME_SETS:
        for data in outcome_set:
            existing = session.execute(
                select(CurriculumOutcome).where(CurriculumOutcome.code == data["code"]),
            ).scalar_one_or_none()
            if existing:
                existing.strand = data["strand"]
                existing.descriptor = data["descriptor"]
                existing.year_level = year_level
                existing.text_type = TEXT_TYPE
                outcomes.append(existing)
            else:
                outcome = CurriculumOutcome(
                    code=data["code"],
                    strand=data["strand"],
                    year_level=year_level,
                    text_type=TEXT_TYPE,
                    curriculum=CURRICULUM,
                    descriptor=data["descriptor"],
                )
                session.add(outcome)
                outcomes.append(outcome)
    session.commit()
    return outcomes
