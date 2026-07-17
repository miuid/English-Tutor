"""Tests for eval fixture discovery and the sample→inputs mapping."""

from pathlib import Path

from app.eval.fixtures import discover_cases, parse_sample_inputs
from app.skills import load_skills

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


def test_discover_cases_finds_all_skill_examples() -> None:
    skills = load_skills(SKILLS_DIR)
    cases = discover_cases(skills)
    assert len(skills) == 8
    assert len(cases) == 8
    assert {case.skill.name for case in cases} == {skill.name for skill in skills}
    for case in cases:
        assert case.example == "sample-01"
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
