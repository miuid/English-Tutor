"""CLI entry point: ``python -m app.eval [--skill NAME] [--no-judge] [--verbose]``.

Runs every skill's golden example fixtures through the skill executor, checks
the outputs with deterministic rules and an LLM judge, prints a scorecard, and
exits non-zero unless every case passes. The provider comes from
``get_settings()``; with ``LLM_PROVIDER=fake`` the pipeline runs end-to-end
without an API key (canned outputs will fail checks — that is expected).
"""

import argparse
import asyncio
from pathlib import Path

from app.config import get_settings
from app.eval.fixtures import discover_cases
from app.eval.runner import PASS, run_cases
from app.eval.scorecard import render_scorecard
from app.llm.factory import create_llm_provider
from app.skills.executor import SkillExecutionService
from app.skills.loader import load_skills


def build_parser(skill_names: list[str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app.eval",
        description="Run skill golden-example evals and print a scorecard.",
    )
    parser.add_argument("--skill", choices=skill_names, help="evaluate one skill only")
    parser.add_argument(
        "--no-judge",
        action="store_true",
        help="rules only; skip the LLM-as-judge call",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="print raw outputs and per-criterion judge detail",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the eval pipeline; return 0 if every case passes, else 1."""
    settings = get_settings()
    skills = load_skills(Path(settings.skills_dir))
    args = build_parser([skill.name for skill in skills]).parse_args(argv)

    cases = discover_cases(skills)
    if args.skill:
        cases = [case for case in cases if case.skill.name == args.skill]

    provider = create_llm_provider(settings)
    executor = SkillExecutionService(provider=provider)
    results = asyncio.run(run_cases(cases, executor, provider, judge=not args.no_judge))

    print(render_scorecard(results, verbose=args.verbose))
    return 0 if all(result.status == PASS for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
