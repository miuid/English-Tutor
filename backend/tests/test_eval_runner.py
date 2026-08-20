"""End-to-end tests for the eval runner and ``python -m app.eval`` CLI."""

import asyncio
import os
from pathlib import Path

import pytest

from app.config import get_settings
from app.eval.__main__ import main
from app.eval.fixtures import EvalCase, discover_cases
from app.eval.runner import ERROR, PASS, CaseResult, run_cases
from app.eval.scorecard import render_scorecard, summarize
from app.llm import FakeProvider
from app.skills import load_skills
from app.skills.executor import SkillExecutionService
from tests.test_eval_fixtures import _write_skill

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"

# One canned skill output that satisfies every registered rule, and one
# well-formed judge verdict; FakeProvider alternates them per case.
RULE_PASSING_OUTPUT = (
    "Some helpful coaching.\n"
    "Route to: check-structure\n"
    "1. Explain the effect — it lifts analysis.\n"
    "2. Add a link back — it lifts structure.\n"
    "How would you rate yourself against these criteria?\n"
)
JUDGE_PASS_OUTPUT = "✓ Everything expected — present in the output\nVERDICT: PASS"


def _cases() -> list[EvalCase]:
    return discover_cases(load_skills(SKILLS_DIR))


@pytest.mark.asyncio
async def test_run_cases_returns_one_result_per_case() -> None:
    provider = FakeProvider()
    results = await run_cases(
        _cases(), SkillExecutionService(provider=provider), provider, judge=True
    )
    assert len(results) == 26
    # "fake response" is not a parseable judge verdict: judge ERROR, not a pass.
    for result in results:
        assert result.status == ERROR
        assert result.judge_error
        assert result.output == "fake response"


@pytest.mark.asyncio
async def test_run_cases_all_pass_with_cooperative_fake() -> None:
    provider = FakeProvider(canned_responses=[RULE_PASSING_OUTPUT, JUDGE_PASS_OUTPUT])
    results = await run_cases(
        _cases(), SkillExecutionService(provider=provider), provider, judge=True
    )
    assert len(results) == 26
    assert all(result.status == PASS for result in results)


@pytest.mark.asyncio
async def test_run_cases_no_judge_uses_rules_only() -> None:
    provider = FakeProvider(canned_responses=[RULE_PASSING_OUTPUT])
    results = await run_cases(
        _cases(), SkillExecutionService(provider=provider), provider, judge=False
    )
    assert all(result.status == PASS for result in results)
    assert all(result.judge_result is None for result in results)


@pytest.mark.asyncio
async def test_run_cases_rules_failure_is_fail_not_error() -> None:
    provider = FakeProvider(canned_responses=["fake response", JUDGE_PASS_OUTPUT])
    results = await run_cases(
        _cases(), SkillExecutionService(provider=provider), provider, judge=True
    )
    by_skill = {result.skill_name: result for result in results}
    # "fake response" passes generic rules but fails skill-specific ones.
    assert by_skill["give-feedback"].status == "FAIL"
    assert not by_skill["give-feedback"].rules_passed
    assert by_skill["diagnose-errors"].status == "FAIL"
    assert by_skill["check-structure"].status == PASS  # generic rules only


def test_scorecard_renders_table_and_summary() -> None:
    provider = FakeProvider(canned_responses=[RULE_PASSING_OUTPUT, JUDGE_PASS_OUTPUT])
    results = asyncio.run(
        run_cases(_cases(), SkillExecutionService(provider=provider), provider, judge=True)
    )
    card = render_scorecard(results)
    assert "skill" in card and "overall" in card
    assert "give-feedback" in card
    assert summarize(results) == "Summary: 26 cases — 26 passed, 0 failed, 0 errors"


def test_scorecard_groups_results_by_skill_and_combo() -> None:
    results = [
        CaseResult(skill_name="demo-skill", example="sample-01"),
        CaseResult(skill_name="demo-skill", example="sample-02", error="boom"),
        CaseResult(
            skill_name="demo-skill",
            example="sample-03",
            text_type="persuasive",
            year_band="year-9-10",
        ),
    ]
    card = render_scorecard(results)
    breakdown = card.split("By skill and band/text_type combo:", 1)[1]
    assert "demo-skill" in breakdown
    assert "analytical/year-8     1/2 passed (1 errors)" in breakdown
    assert "persuasive/year-9-10  1/1 passed" in breakdown


@pytest.mark.asyncio
async def test_run_cases_propagates_fixture_tags(tmp_path: Path) -> None:
    _write_skill(
        tmp_path,
        "demo-skill",
        {
            "sample-01.md": "year_level: 8\n\n---\n\nFirst text.",
            "expected-01.md": "Expected one.",
            "sample-02.md": "year_level: 10\ntext_type: persuasive\n\n---\n\nSecond text.",
            "expected-02.md": "Expected two.",
        },
    )
    cases = discover_cases(load_skills(tmp_path))
    provider = FakeProvider(canned_responses=[RULE_PASSING_OUTPUT])
    results = await run_cases(
        cases, SkillExecutionService(provider=provider), provider, judge=False
    )
    assert [result.combo for result in results] == [
        "analytical/year-8",
        "persuasive/year-9-10",
    ]


def test_main_runs_end_to_end_with_fake_provider(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_API_KEY", "")
    get_settings.cache_clear()
    try:
        exit_code = main([])
    finally:
        get_settings.cache_clear()
    out = capsys.readouterr().out
    assert "Summary: 26 cases" in out
    assert "give-feedback" in out
    assert "diagnose-errors" in out
    # FakeProvider's canned output fails checks, so the run must not pass.
    assert exit_code == 1


def test_main_exit_zero_when_everything_passes(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_API_KEY", "")
    get_settings.cache_clear()
    fake = FakeProvider(canned_responses=[RULE_PASSING_OUTPUT, JUDGE_PASS_OUTPUT])
    monkeypatch.setattr("app.eval.__main__.create_llm_provider", lambda settings: fake)
    try:
        exit_code = main([])
    finally:
        get_settings.cache_clear()
    out = capsys.readouterr().out
    assert "26 passed, 0 failed, 0 errors" in out
    assert exit_code == 0


def test_main_skill_filter(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_API_KEY", "")
    get_settings.cache_clear()
    try:
        exit_code = main(["--skill", "give-feedback", "--no-judge"])
    finally:
        get_settings.cache_clear()
    out = capsys.readouterr().out
    assert "Summary: 2 cases" in out
    assert "give-feedback" in out
    assert "diagnose-errors" not in out
    assert exit_code == 1


@pytest.mark.skipif(
    os.environ.get("LLM_PROVIDER") != "anthropic" or not os.environ.get("LLM_API_KEY"),
    reason="Real LLM test requires LLM_PROVIDER=anthropic and LLM_API_KEY",
)
def test_eval_smoke_real_llm(capsys: pytest.CaptureFixture[str]) -> None:
    get_settings.cache_clear()
    try:
        exit_code = main(["--skill", "give-feedback"])
    finally:
        get_settings.cache_clear()
    out = capsys.readouterr().out
    assert "Summary: 2 cases" in out
    assert exit_code in (0, 1)
