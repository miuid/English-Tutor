"""Seed QCAA curriculum outcomes and rubric criteria.

Seeded text types: analytical, persuasive and imaginative (Year 8-10).
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

Imaginative descriptors trace to reaserch.md (imaginative domain "conveys
meaning and perspectives through narrative structure"; Year 8 marking
criteria — purposeful creation, variation of text structures and language
features; Year 9 marking criteria — purposeful selection and considered
experimentation with structures, language features and voice; NAPLAN
narrative criteria) and the ISS-007 imaginative packs (criteria banks +
A-E feedback rubrics). Year 10 imaginative descriptors carry the same
Q-001 derived-not-verbatim provenance.

Senior QCE rows (Units 1-4 and the IA1/IA2/IA3/EA instruments) trace to
the official QCAA English General Senior Syllabus 2025 v1.3 (January
2026), © State of Queensland (QCAA) 2026, licensed CC-BY 4.0 — archived
at research/official/english-2025-v1.3-syllabus.md and modelled per
research/qce-senior-instrument-modelling.md (ISS-024). They are
framework rows only: no senior content depth is claimed beyond the
modelled units/instruments.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import CurriculumOutcome

TEXT_TYPE_ANALYTICAL = "analytical"
TEXT_TYPE_PERSUASIVE = "persuasive"
TEXT_TYPE_IMAGINATIVE = "imaginative"
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

# Year 8 imaginative: trace to reaserch.md (imaginative domain "conveys
# meaning and perspectives through narrative structure"; Year 8 marking
# criteria — purposeful creation, variation of text structures and language
# features; NAPLAN narrative criteria — Audience, Text Structure, Ideas,
# Character & Setting, Vocabulary, Cohesion) and
# skills/set-success-criteria/references/imaginative/year-8/criteria-bank.md.
YEAR_8_IMAGINATIVE_OUTCOMES = [
    {
        "code": "QCAA-Y8-IMA-01",
        "strand": "Structure and organisation",
        "descriptor": (
            "I can build a narrative around one clear complication, with tension "
            "that rises scene by scene and a resolution that follows from what "
            "happened."
        ),
    },
    {
        "code": "QCAA-Y8-IMA-02",
        "strand": "Showing and detail",
        "descriptor": (
            "I can show a key emotion or moment through action and concrete "
            "sensory detail instead of naming it."
        ),
    },
    {
        "code": "QCAA-Y8-IMA-03",
        "strand": "Character and voice",
        "descriptor": (
            "I can hold one consistent point of view and make my character act "
            "like the person I've shown the reader."
        ),
    },
    {
        "code": "QCAA-Y8-IMA-04",
        "strand": "Response-level narrative",
        "descriptor": (
            "I can hook the reader early and sustain a coherent narrative in the "
            "format the task asks for (story, diary, memoir)."
        ),
    },
]

# Year 9 imaginative: trace to reaserch.md (Year 9 marking criteria —
# purposeful selection and considered experimentation with structures,
# language features and voice; Year 9 imaginative formats — structural
# experimentation, manipulating narrative voice, changing character points of
# view, playing with tone) and
# skills/set-success-criteria/references/imaginative/year-9-10/criteria-bank.md.
YEAR_9_IMAGINATIVE_OUTCOMES = [
    {
        "code": "QCAA-Y9-IMA-01",
        "strand": "Structure and organisation",
        "descriptor": (
            "I can experiment with structure (non-linear, multi-voice, shifting "
            "POV) because of what it does, while keeping the reader oriented."
        ),
    },
    {
        "code": "QCAA-Y9-IMA-02",
        "strand": "Voice and tone",
        "descriptor": (
            "I can hold a distinct narrator voice across the whole piece and "
            "shift tone or point of view deliberately, with the shift signalled."
        ),
    },
    {
        "code": "QCAA-Y9-IMA-03",
        "strand": "Showing and imagery",
        "descriptor": (
            "I can show my key moments and sustain an image as a motif that "
            "builds meaning rather than decorates."
        ),
    },
    {
        "code": "QCAA-Y9-IMA-04",
        "strand": "Response-level narrative",
        "descriptor": (
            "I can sustain a complication across 600-800 words with controlled, "
            "purposeful experimentation."
        ),
    },
]

# Year 10 imaginative: derived from the Year 9 elaborations one band up
# (Q-001 — derived, not verbatim; provisional until official sources are imported).
YEAR_10_IMAGINATIVE_OUTCOMES = [
    {
        "code": "QCAA-Y10-IMA-01",
        "strand": "Structure and organisation",
        "descriptor": (
            "I can sustain purposeful structural experimentation across an "
            "extended imaginative response, controlling orientation and payoff."
        ),
    },
    {
        "code": "QCAA-Y10-IMA-02",
        "strand": "Voice and tone",
        "descriptor": (
            "I can craft and control a distinctive narrative voice, using tone "
            "and point-of-view shifts for deliberate effect."
        ),
    },
    {
        "code": "QCAA-Y10-IMA-03",
        "strand": "Showing and imagery",
        "descriptor": (
            "I can integrate imagery, motif and understatement purposefully to "
            "shape meaning and affect the reader."
        ),
    },
    {
        "code": "QCAA-Y10-IMA-04",
        "strand": "Response-level narrative",
        "descriptor": (
            "I can shape structure, language features and voice experimentally "
            "for effect across a whole imaginative text."
        ),
    },
]

# Senior QCE framework rows. Source: QCAA English General Senior Syllabus
# 2025 v1.3 (January 2026), © State of Queensland (QCAA) 2026, CC-BY 4.0
# (research/official/english-2025-v1.3-syllabus.md). Framework only — no
# senior content depth beyond the modelled units and instruments (ISS-024).
_TEXT_TYPE_FRAMEWORK = "framework"

# Units 1-4 (syllabus "Units" section, pp. 17-32). Units 1-2 are Year 11
# formative (reported S/U); Units 3-4 are studied as a Year 12 summative pair.
SENIOR_UNIT_OUTCOMES = [
    {
        "code": "QCAA-Y11-U1",
        "strand": "Course structure",
        "descriptor": (
            "Unit 1: Perspectives and texts — students explore how perspectives and "
            "representations of concepts, identities and/or groups are constructed "
            "through textual choices. Year 11 formative unit, reported S/U. "
            "Source: English 2025 v1.3, Unit 1 (p. 17)."
        ),
    },
    {
        "code": "QCAA-Y11-U2",
        "strand": "Course structure",
        "descriptor": (
            "Unit 2: Texts and culture — students examine the relationship between "
            "language and identity and how textual choices position audiences, "
            "including Australian texts. Year 11 formative unit, reported S/U. "
            "Source: English 2025 v1.3, Unit 2 (p. 21)."
        ),
    },
    {
        "code": "QCAA-Y12-U3",
        "strand": "Course structure",
        "descriptor": (
            "Unit 3: Textual connections — students explore connections between "
            "texts through representations of the same concepts and issues; must "
            "include a study of media texts. Year 12 summative unit (studied as a "
            "pair with Unit 4). Source: English 2025 v1.3, Unit 3 (p. 24)."
        ),
    },
    {
        "code": "QCAA-Y12-U4",
        "strand": "Course structure",
        "descriptor": (
            "Unit 4: Close study of literary texts — students engage with literary "
            "texts from diverse times and places through close study. Year 12 "
            "summative unit (studied as a pair with Unit 3). "
            "Source: English 2025 v1.3, Unit 4 (p. 29)."
        ),
    },
]

# Summative instruments implemented with Units 3 and 4 (syllabus "Assessment"
# section, pp. 33-48). Each instrument is marked against three ISMG criteria —
# Knowledge application, Organisation and development, Textual features — and
# contributes 25% to the subject result out of 100.
SENIOR_IA1_OUTCOMES = [
    {
        "code": "QCAA-Y12-IA1",
        "strand": "Summative assessment",
        "descriptor": (
            "IA1 — Spoken persuasive response (25%, Units 3-4): create a persuasive "
            "argument on a contemporary contentious media issue for an identified "
            "public audience; spoken up to 8 minutes; 4 weeks notification; "
            "individual task. ISMG criteria: Knowledge application (8 marks), "
            "Organisation and development (8), Textual features (9). "
            "Source: English 2025 v1.3, Internal assessment 1 (pp. 34-38)."
        ),
    },
]

SENIOR_IA2_OUTCOMES = [
    {
        "code": "QCAA-Y12-IA2",
        "strand": "Summative assessment",
        "descriptor": (
            "IA2 — Written response for a public audience (25%, Units 3-4): analyse "
            "a representation of a concept, identity, time or place across two "
            "connected texts (at least one from the prescribed text list) in a "
            "written text for a public audience; up to 1500 words; 5 weeks "
            "notification; individual task. ISMG criteria: Knowledge application "
            "(9 marks), Organisation and development (8), Textual features (8). "
            "Source: English 2025 v1.3, Internal assessment 2 (pp. 39-42)."
        ),
    },
]

SENIOR_IA3_OUTCOMES = [
    {
        "code": "QCAA-Y12-IA3",
        "strand": "Summative assessment",
        "descriptor": (
            "IA3 — Examination: extended response (25%, Units 3-4): supervised "
            "imaginative response using a literary text from the prescribed text "
            "list as a springboard; 15 minutes planning + 120 minutes working; "
            "no notes or springboard text in the examination. ISMG criteria: "
            "Knowledge application (9 marks), Organisation and development (8), "
            "Textual features (8). "
            "Source: English 2025 v1.3, Internal assessment 3 (pp. 43-47)."
        ),
    },
]

SENIOR_EA_OUTCOMES = [
    {
        "code": "QCAA-Y12-EA",
        "strand": "Summative assessment",
        "descriptor": (
            "EA — Examination: extended response (25%, relates to Unit 4): external "
            "analytical essay responding to an unseen question on a literary text "
            "from the external assessment section of the prescribed text list; "
            "15 minutes planning + 120 minutes working; developed and marked by "
            "the QCAA, common to all schools. "
            "Source: English 2025 v1.3, External assessment (p. 48)."
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
    (8, TEXT_TYPE_IMAGINATIVE, YEAR_8_IMAGINATIVE_OUTCOMES),
    (9, TEXT_TYPE_IMAGINATIVE, YEAR_9_IMAGINATIVE_OUTCOMES),
    (10, TEXT_TYPE_IMAGINATIVE, YEAR_10_IMAGINATIVE_OUTCOMES),
    (11, _TEXT_TYPE_FRAMEWORK, SENIOR_UNIT_OUTCOMES[:2]),
    (12, _TEXT_TYPE_FRAMEWORK, SENIOR_UNIT_OUTCOMES[2:]),
    (12, TEXT_TYPE_PERSUASIVE, SENIOR_IA1_OUTCOMES),
    (12, TEXT_TYPE_ANALYTICAL, SENIOR_IA2_OUTCOMES),
    (12, TEXT_TYPE_IMAGINATIVE, SENIOR_IA3_OUTCOMES),
    (12, TEXT_TYPE_ANALYTICAL, SENIOR_EA_OUTCOMES),
]


def seed(session: Session) -> list[CurriculumOutcome]:
    """Idempotently seed QCAA outcomes (analytical + persuasive + imaginative, Year 8-10)."""
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
