"""Tests for the give-feedback rubric-level parser."""

from app.skills.rubric_parser import parse_rubric_levels

CONTRACT_OUTPUT = """## Per-criterion levels
- Understanding of text / ideas: **C** — a point exists but is vague.
- Analysis (how techniques create meaning): **D** — quote dropped in, effect not explained.
- Use of evidence: **C–** — relevant quote, loosely integrated.
- Structure & cohesion: **D+** — no link back.
- Language & vocabulary: **C** — clear but flat.

Strength: A relevant simile, well chosen.
Your 1–2 next steps to level up:
  1. Explain how the simile creates its effect — it lifts Analysis from D toward B.
Self-check: how would you rate yourself against these criteria?
"""


def test_parses_contract_section() -> None:
    levels = parse_rubric_levels(CONTRACT_OUTPUT)
    by_name = {level.criterion_name: level for level in levels}
    assert len(levels) == 5
    assert by_name["Understanding of text / ideas"].level == "C"
    assert by_name["Analysis (how techniques create meaning)"].level == "D"
    assert (
        by_name["Analysis (how techniques create meaning)"].note
        == "quote dropped in, effect not explained."
    )
    assert by_name["Use of evidence"].level == "C-"  # en dash normalised
    assert by_name["Structure & cohesion"].level == "D+"
    assert by_name["Language & vocabulary"].note == "clear but flat."


def test_ignores_strength_steps_and_self_check_lines() -> None:
    levels = parse_rubric_levels(CONTRACT_OUTPUT)
    names = [level.criterion_name for level in levels]
    assert "Strength" not in names
    assert not any(name.startswith("1.") for name in names)


def test_plain_variant_without_bullets_or_bold() -> None:
    output = "Use of evidence: C — relevant but thin\nStructure & cohesion: B+ — solid links"
    levels = parse_rubric_levels(output)
    assert [(level.criterion_name, level.level) for level in levels] == [
        ("Use of evidence", "C"),
        ("Structure & cohesion", "B+"),
    ]


def test_bold_criterion_name_and_lowercase_level() -> None:
    levels = parse_rubric_levels("- **Structure & cohesion**: **b-** — mostly linked")
    assert len(levels) == 1
    assert levels[0].criterion_name == "Structure & cohesion"
    assert levels[0].level == "B-"


def test_note_is_optional() -> None:
    levels = parse_rubric_levels("- Use of evidence: **B**")
    assert len(levels) == 1
    assert levels[0].note is None


def test_ignores_overall_line() -> None:
    output = "## Per-criterion levels\n- Use of evidence: **B** — ok\n(Overall: **C**)"
    levels = parse_rubric_levels(output)
    assert [level.criterion_name for level in levels] == ["Use of evidence"]


def test_rejects_invalid_levels() -> None:
    output = "- Use of evidence: **F** — nope\n- Structure & cohesion: **D/E** — boundary"
    assert parse_rubric_levels(output) == []


def test_missing_section_returns_empty() -> None:
    assert parse_rubric_levels("Strength: A real move.\n1. One step — why.") == []
    assert parse_rubric_levels("") == []


def test_section_scoping_avoids_false_positive_strength_line() -> None:
    output = (
        "## Per-criterion levels\n"
        "- Use of evidence: **B** — ok\n"
        "\n"
        "Strength: A — you embedded a quote well\n"  # would false-positive unscoped
    )
    levels = parse_rubric_levels(output)
    assert [level.criterion_name for level in levels] == ["Use of evidence"]
