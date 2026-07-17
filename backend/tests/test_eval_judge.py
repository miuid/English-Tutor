"""Tests for the LLM-as-judge response parser and judging call."""

import pytest

from app.eval.judge import JudgeParseError, judge_output, parse_judge_response
from app.llm import FakeProvider


def test_parse_pass_verdict() -> None:
    text = (
        "✓ Bounded next steps — only two next steps given\n"
        "✓ Metacognitive prompt — asks the student to self-rate\n"
        "VERDICT: PASS"
    )
    result = parse_judge_response(text)
    assert result.verdict == "PASS"
    assert len(result.criteria) == 2
    assert result.criteria[0].criterion == "Bounded next steps"
    assert result.criteria[0].met
    assert result.criteria[0].justification == "only two next steps given"


def test_parse_fail_verdict_with_unmet_criterion() -> None:
    text = (
        "✓ Bounded next steps — only two given\n"
        "✗ Metacognitive prompt — no self-rating question\n"
        "VERDICT: FAIL"
    )
    result = parse_judge_response(text)
    assert result.verdict == "FAIL"
    assert not result.criteria[1].met


def test_parse_accepts_criterion_without_justification() -> None:
    result = parse_judge_response("✗ Metacognitive prompt\nVERDICT: FAIL")
    assert result.criteria[0].criterion == "Metacognitive prompt"
    assert result.criteria[0].justification == ""


def test_parse_rejects_missing_verdict() -> None:
    with pytest.raises(JudgeParseError, match="VERDICT"):
        parse_judge_response("✓ Bounded next steps — fine")


def test_parse_rejects_verdict_not_on_final_line() -> None:
    text = "VERDICT: PASS\n✓ Bounded next steps — fine"
    with pytest.raises(JudgeParseError, match="VERDICT"):
        parse_judge_response(text)


def test_parse_rejects_junk_line() -> None:
    text = "Here is my assessment of the output.\n✓ One criterion — ok\nVERDICT: PASS"
    with pytest.raises(JudgeParseError, match="criterion"):
        parse_judge_response(text)


def test_parse_rejects_empty_output() -> None:
    with pytest.raises(JudgeParseError, match="empty"):
        parse_judge_response("   ")


def test_parse_rejects_no_criteria() -> None:
    with pytest.raises(JudgeParseError, match="no criterion"):
        parse_judge_response("VERDICT: PASS")


def test_parse_rejects_pass_verdict_with_unmet_criterion() -> None:
    text = "✗ Metacognitive prompt — missing\nVERDICT: PASS"
    with pytest.raises(JudgeParseError, match="PASS"):
        parse_judge_response(text)


@pytest.mark.asyncio
async def test_judge_output_calls_provider_and_parses() -> None:
    provider = FakeProvider(canned_responses=["✓ One criterion — met\nVERDICT: PASS"])
    result = await judge_output(
        provider,
        skill_name="give-feedback",
        sample="sample text",
        expected="rubric text",
        output="output text",
    )
    assert result.verdict == "PASS"
    system_prompt, messages = provider.calls[0]
    assert "ONLY" in system_prompt  # judge is rubric-scoped, not general quality
    content = messages[0]["content"]
    assert "give-feedback" in content
    assert "sample text" in content
    assert "rubric text" in content
    assert "output text" in content


@pytest.mark.asyncio
async def test_judge_output_raises_on_unparseable_response() -> None:
    provider = FakeProvider(canned_responses=["fake response"])
    with pytest.raises(JudgeParseError):
        await judge_output(
            provider,
            skill_name="give-feedback",
            sample="s",
            expected="e",
            output="o",
        )
