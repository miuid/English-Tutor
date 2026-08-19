"""Seed QCAA curriculum outcomes and rubric criteria.

Seeded text types: analytical (Year 8-10) and persuasive (Year 8-10).
Year 8 bands are verbatim scope from MVP. Year 9 analytical descriptors
trace to reaserch.md (Year 9 marking criteria: considered analysis of
representations, contexts and positioning; discriminating thesis; formal
register) and the year-9-10 reference packs shipped in ISS-002. Year 10
analytical descriptors are *derived* from the Year 9 elaborations one band
up (provenance note Q-001 — provisional until official QCAA sources are
imported).

Persuasive descriptors trace to reaserch.md (persuasive domain "arguments,
rhetoric, and evidence to sway an audience"; Year 8 marking criteria —
advancing ideas with supporting evidence, adapting language and voice to
formal/informal audiences; Year 9 marking criteria — substantiated
viewpoints, rhetorical strategies and evidence; NAPLAN persuasive criteria)
and the ISS-004 persuasive packs (criteria banks + A-E feedback rubrics).
Year 10 persuasive descriptors carry the same Q-001 derived-not-verbatim
provenance.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CurriculumOutcome

TEXT_TYPE_ANALYTICAL = "analytical"
TEXT_TYPE_PERSUASIVE = "persuasive"
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

# Year 8 persuasive: trace to reaserch.md (Year 8 marking criteria —
# advancing ideas with supporting evidence; adapting language and voice to
# formal or informal audiences; NAPLAN persuasive criteria) and
# skills/set-success-criteria/references/persuasive/year-8/criteria-bank.md.
YEAR_8_PERSUASIVE_OUTCOMES = [
    {
        "code": "QCAA-Y8-PER-01",
        "strand": "Structure and organisation",
        "descriptor": (
            "I can structure a persuasive text with a hook, a clear contention, "
            "one reason per paragraph, and a call to action."
        ),
    },
    {
        "code": "QCAA-Y8-PER-02",
        "strand": "Argument and evidence",
        "descriptor": (
            "I can develop each reason — explaining why it holds and why my "
            "audience should care — and support it with a specific example or fact."
        ),
    },
    {
        "code": "QCAA-Y8-PER-03",
        "strand": "Audience and language",
        "descriptor": (
            "I can adapt my voice and language to suit a formal or informal audience."
        ),
    },
    {
        "code": "QCAA-Y8-PER-04",
        "strand": "Response-level persuasion",
        "descriptor": (
            "I can sustain one position across a whole persuasive response and "
            "order my reasons so my strongest lands where it counts."
        ),
    },
]

# Year 9 persuasive: trace to reaserch.md (Year 9 marking criteria —
# substantiated viewpoints; rhetorical strategies and evidence; purposeful
# selection and experimentation with structures, language features and voice)
# and skills/set-success-criteria/references/persuasive/year-9-10/criteria-bank.md.
YEAR_9_PERSUASIVE_OUTCOMES = [
    {
        "code": "QCAA-Y9-PER-01",
        "strand": "Structure and organisation",
        "descriptor": (
            "I can build a persuasive text around a clear, arguable viewpoint, "
            "with reasons ordered so the argument escalates."
        ),
    },
    {
        "code": "QCAA-Y9-PER-02",
        "strand": "Argument and evidence",
        "descriptor": (
            "I can substantiate each reason with evidence that carries the "
            "argument rather than decorates it."
        ),
    },
    {
        "code": "QCAA-Y9-PER-03",
        "strand": "Rhetoric and register",
        "descriptor": (
            "I can deploy rhetorical strategies deliberately and sustain a voice "
            "that fits the format (feature article, letter to the editor, pitch, review)."
        ),
    },
    {
        "code": "QCAA-Y9-PER-04",
        "strand": "Response-level persuasion",
        "descriptor": (
            "I can acknowledge the strongest counterargument and rebut it within "
            "a sustained persuasive response."
        ),
    },
]

# Year 10 persuasive: derived from the Year 9 elaborations one band up
# (Q-001 — derived, not verbatim; provisional until official sources are imported).
YEAR_10_PERSUASIVE_OUTCOMES = [
    {
        "code": "QCAA-Y10-PER-01",
        "strand": "Structure and organisation",
        "descriptor": (
            "I can sustain a discriminating viewpoint across an extended persuasive "
            "response, controlling escalation and emphasis."
        ),
    },
    {
        "code": "QCAA-Y10-PER-02",
        "strand": "Argument and evidence",
        "descriptor": (
            "I can integrate well-chosen evidence and appeals purposefully to sway "
            "a specific audience."
        ),
    },
    {
        "code": "QCAA-Y10-PER-03",
        "strand": "Rhetoric and register",
        "descriptor": (
            "I can maintain a controlled formal public register with deliberate "
            "modality and rhetorical metalanguage."
        ),
    },
    {
        "code": "QCAA-Y10-PER-04",
        "strand": "Response-level persuasion",
        "descriptor": (
            "I can shape structure, language features and voice experimentally for "
            "effect across a whole persuasive text."
        ),
    },
]

# (year_level, text_type, outcomes) triples seeded in one idempotent pass.
_OUTCOME_SETS: list[tuple[int, str, list[dict[str, str]]]] = [
    (8, TEXT_TYPE_ANALYTICAL, YEAR_8_OUTCOMES),
    (9, TEXT_TYPE_ANALYTICAL, YEAR_9_OUTCOMES),
    (10, TEXT_TYPE_ANALYTICAL, YEAR_10_OUTCOMES),
    (8, TEXT_TYPE_PERSUASIVE, YEAR_8_PERSUASIVE_OUTCOMES),
    (9, TEXT_TYPE_PERSUASIVE, YEAR_9_PERSUASIVE_OUTCOMES),
    (10, TEXT_TYPE_PERSUASIVE, YEAR_10_PERSUASIVE_OUTCOMES),
]


def seed(session: Session) -> list[CurriculumOutcome]:
    """Idempotently seed the QCAA curriculum outcomes (analytical + persuasive, Year 8-10)."""
    outcomes: list[CurriculumOutcome] = []
    for year_level, text_type, outcome_set in _OUTCOME_SETS:
        for data in outcome_set:
            existing = session.execute(
                select(CurriculumOutcome).where(CurriculumOutcome.code == data["code"]),
            ).scalar_one_or_none()
            if existing:
                existing.strand = data["strand"]
                existing.descriptor = data["descriptor"]
                existing.year_level = year_level
                existing.text_type = text_type
                outcomes.append(existing)
            else:
                outcome = CurriculumOutcome(
                    code=data["code"],
                    strand=data["strand"],
                    year_level=year_level,
                    text_type=text_type,
                    curriculum=CURRICULUM,
                    descriptor=data["descriptor"],
                )
                session.add(outcome)
                outcomes.append(outcome)
    session.commit()
    return outcomes
