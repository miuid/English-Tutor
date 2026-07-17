"""Tests for the deterministic eval rule checks."""

from app.eval.rules import (
    MAX_OUTPUT_CHARS,
    RuleContext,
    check_bounded_length,
    check_max_two_next_steps,
    check_metacognitive_prompt,
    check_non_empty,
    check_route_line,
    checks_for,
)

CONTEXT = RuleContext(
    skill_names=(
        "set-success-criteria",
        "model-response",
        "guided-practice",
        "independent-task",
        "diagnose-errors",
        "check-structure",
        "elevate-vocabulary",
        "give-feedback",
    )
)


def test_non_empty_passes_on_text() -> None:
    assert check_non_empty("some output", CONTEXT).passed


def test_non_empty_fails_on_blank() -> None:
    result = check_non_empty("   \n ", CONTEXT)
    assert not result.passed
    assert "empty" in result.detail


def test_bounded_length_passes_under_cap() -> None:
    assert check_bounded_length("x" * MAX_OUTPUT_CHARS, CONTEXT).passed


def test_bounded_length_fails_over_cap() -> None:
    result = check_bounded_length("x" * (MAX_OUTPUT_CHARS + 1), CONTEXT)
    assert not result.passed
    assert str(MAX_OUTPUT_CHARS) in result.detail


def test_max_two_next_steps_passes_with_two() -> None:
    output = "Your 1–2 next steps:\n  1. Explain the effect — why.\n  2. Link back — why."
    assert check_max_two_next_steps(output, CONTEXT).passed


def test_max_two_next_steps_fails_with_three() -> None:
    output = "1. one\n2. two\n3. three"
    result = check_max_two_next_steps(output, CONTEXT)
    assert not result.passed
    assert "3" in result.detail


def test_metacognitive_prompt_passes_on_self_rating_question() -> None:
    output = "Self-check: how would you rate yourself against these criteria?"
    assert check_metacognitive_prompt(output, CONTEXT).passed


def test_metacognitive_prompt_fails_without_question_mark() -> None:
    output = "Rate yourself against these criteria."
    assert not check_metacognitive_prompt(output, CONTEXT).passed


def test_metacognitive_prompt_fails_without_self_rating() -> None:
    output = "What is the poet's main idea?"
    assert not check_metacognitive_prompt(output, CONTEXT).passed


def test_route_line_passes_for_known_skill() -> None:
    output = "Primary issue: analysis/evidence (major).\nRoute to: check-structure"
    assert check_route_line(output, CONTEXT).passed


def test_route_line_fails_for_unknown_skill() -> None:
    result = check_route_line("Route to: write-the-essay", CONTEXT)
    assert not result.passed
    assert "write-the-essay" in result.detail


def test_route_line_fails_when_missing() -> None:
    result = check_route_line("No route here.", CONTEXT)
    assert not result.passed
    assert "Route to:" in result.detail


def test_checks_for_combines_generic_and_skill_rules() -> None:
    generic = checks_for("model-response")
    assert [check.__name__ for check in generic] == [
        "check_non_empty",
        "check_bounded_length",
    ]
    feedback = checks_for("give-feedback")
    assert [check.__name__ for check in feedback] == [
        "check_non_empty",
        "check_bounded_length",
        "check_max_two_next_steps",
        "check_metacognitive_prompt",
    ]
    diagnose = checks_for("diagnose-errors")
    assert "check_route_line" in [check.__name__ for check in diagnose]
