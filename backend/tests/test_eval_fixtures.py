"""Tests for eval fixture discovery and the sample→inputs mapping."""

from pathlib import Path

from app.eval.fixtures import discover_cases, parse_sample_inputs
from app.skills import load_skills

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"

MINIMAL_SKILL_MD = """# demo-skill

## Purpose

Demo.

## When to use

Demo.

## Inputs

Demo.

## Pedagogical basis

Demo.

## Method

Demo.

## Output contract

Demo.

## Success criteria

Demo.

## Guardrails

Demo.
"""


def _write_skill(skill_root: Path, name: str, fixtures: dict[str, str]) -> None:
    """Create a minimal valid skill package with the given example fixtures."""
    examples_dir = skill_root / name / "examples"
    examples_dir.mkdir(parents=True)
    (skill_root / name / "SKILL.md").write_text(MINIMAL_SKILL_MD, encoding="utf-8")
    for filename, content in fixtures.items():
        (examples_dir / filename).write_text(content, encoding="utf-8")


def test_discover_cases_finds_all_skill_examples() -> None:
    skills = load_skills(SKILLS_DIR)
    cases = discover_cases(skills)
    assert len(skills) == 12
    assert len(cases) == 24
    assert {case.skill.name for case in cases} == {skill.name for skill in skills}
    for case in cases:
        assert case.example in {"sample-01", "sample-02"}
        assert case.inputs
        assert case.expected.strip()


def test_parse_sample_maps_header_keys_and_body() -> None:
    sample = (SKILLS_DIR / "give-feedback" / "examples" / "sample-01.md").read_text(
        encoding="utf-8"
    )
    inputs = parse_sample_inputs(sample)
    assert inputs["year_level"] == "8"
    assert inputs["text_type"] == "analytical"
    assert inputs["mode"] == "formative"
    assert inputs["task_prompt"] == "How does the poet present the effects of war?"
    assert "I can start with a clear point" in inputs["success_criteria"]
    assert "I can link back to the main idea." in inputs["success_criteria"]
    assert inputs["student_text"].startswith("In this poem the poet shows that war is bad.")


def test_parse_sample_body_becomes_context_when_student_text_in_header() -> None:
    sample = (SKILLS_DIR / "guided-practice" / "examples" / "sample-01.md").read_text(
        encoding="utf-8"
    )
    inputs = parse_sample_inputs(sample)
    assert inputs["student_text"].startswith("The poet uses the simile")
    assert "no explanation of the effect yet" in inputs["context"]
    assert inputs["scaffold_level"] == "partial"


def test_parse_sample_without_separator_has_no_student_text() -> None:
    sample = (SKILLS_DIR / "independent-task" / "examples" / "sample-01.md").read_text(
        encoding="utf-8"
    )
    inputs = parse_sample_inputs(sample)
    assert "student_text" not in inputs
    assert inputs["mode"] == "assessment"
    assert inputs["stimulus"] == "none"


def test_parse_sample_defaults_year_level_and_text_type() -> None:
    sample = (SKILLS_DIR / "model-response" / "examples" / "sample-01.md").read_text(
        encoding="utf-8"
    )
    inputs = parse_sample_inputs(sample)
    assert inputs["year_level"] == "8"
    assert inputs["text_type"] == "analytical"
    assert inputs["skill_focus"].startswith("explain how a technique")


def test_parse_sample_bare_student_text_fallback() -> None:
    inputs = parse_sample_inputs("The poem is bad and it makes me sad.")
    assert inputs == {
        "student_text": "The poem is bad and it makes me sad.",
        "year_level": "8",
        "text_type": "analytical",
    }


def test_existing_fixtures_get_default_analytical_year_8_tags() -> None:
    # The original v1 fixtures carry no explicit text_type header and must
    # default to analytical/year-8. Specialist skills declare their home type
    # explicitly (strengthen-argument: persuasive; craft-voice: imaginative),
    # so they are out of scope here.
    core_skills = {
        "set-success-criteria",
        "model-response",
        "guided-practice",
        "independent-task",
        "diagnose-errors",
        "check-structure",
        "elevate-vocabulary",
        "give-feedback",
    }
    cases = discover_cases(load_skills(SKILLS_DIR))
    year_8_cases = [
        case
        for case in cases
        if case.example == "sample-01" and case.skill.name in core_skills
    ]
    assert year_8_cases
    for case in year_8_cases:
        assert case.tags == {"text_type": "analytical", "year_band": "year-8"}
        assert case.combo == "analytical/year-8"


def test_each_core_skill_has_a_year_9_10_analytical_fixture() -> None:
    # The 8 original v1 loop skills each carry an analytical/year-9-10 fixture
    # (ISS-002). Later specialist skills (strengthen-argument, craft-voice) are
    # scoped to persuasive/imaginative and intentionally ship no analytical
    # fixtures.
    core_skills = {
        "set-success-criteria",
        "model-response",
        "guided-practice",
        "independent-task",
        "diagnose-errors",
        "check-structure",
        "elevate-vocabulary",
        "give-feedback",
    }
    cases = discover_cases(load_skills(SKILLS_DIR))
    band_cases = [case for case in cases if case.combo == "analytical/year-9-10"]
    assert {case.skill.name for case in band_cases} == core_skills
    for case in band_cases:
        assert case.tags == {"text_type": "analytical", "year_band": "year-9-10"}
        assert case.inputs["year_level"] == "9"
        assert "year_band" not in case.inputs
        assert case.expected.strip()


def test_discover_cases_supports_multiple_tagged_fixtures_per_skill(tmp_path: Path) -> None:
    _write_skill(
        tmp_path,
        "demo-skill",
        {
            "sample-01.md": "year_level: 8\ntext_type: analytical\n\n---\n\nFirst text.",
            "expected-01.md": "Expected one.",
            "sample-02.md": (
                "year_level: 10\ntext_type: persuasive\nyear_band: year-9-10\n\n---\n\nSecond text."
            ),
            "expected-02.md": "Expected two.",
        },
    )
    cases = discover_cases(load_skills(tmp_path))
    assert len(cases) == 2
    first, second = cases
    assert first.example == "sample-01"
    assert first.tags == {"text_type": "analytical", "year_band": "year-8"}
    assert first.combo == "analytical/year-8"
    assert second.example == "sample-02"
    assert second.tags == {"text_type": "persuasive", "year_band": "year-9-10"}
    assert second.combo == "persuasive/year-9-10"
    # year_band is a discovery tag only — it must never reach the prompt inputs.
    assert "year_band" not in second.inputs
    assert second.inputs["year_level"] == "10"
    assert second.inputs["text_type"] == "persuasive"


def test_year_band_tag_derived_from_year_level_when_not_explicit(tmp_path: Path) -> None:
    _write_skill(
        tmp_path,
        "demo-skill",
        {
            "sample-01.md": "year_level: 9\ntext_type: analytical\n\n---\n\nText.",
            "expected-01.md": "Expected.",
        },
    )
    (case,) = discover_cases(load_skills(tmp_path))
    assert case.tags == {"text_type": "analytical", "year_band": "year-9-10"}
    assert case.combo == "analytical/year-9-10"
