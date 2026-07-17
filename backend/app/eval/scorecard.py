"""Render the eval scorecard printed by ``python -m app.eval``."""

from app.eval.runner import ERROR, PASS, CaseResult


def render_scorecard(results: list[CaseResult], *, verbose: bool = False) -> str:
    """Render a per-case table plus a summary line."""
    rows = [_render_row(result) for result in results]
    skill_width = max([len("skill"), *(len(result.skill_name) for result in results)])
    header = (
        f"{'skill'.ljust(skill_width)}  {'example'.ljust(9)}  "
        f"{'rules'.ljust(28)}  {'judge'.ljust(5)}  overall"
    )
    lines = [header, "-" * len(header)]
    for result, row in zip(results, rows, strict=True):
        lines.append(f"{result.skill_name.ljust(skill_width)}  {row}")
        if verbose:
            lines.extend(_render_verbose(result))
    lines.append("")
    lines.append(summarize(results))
    return "\n".join(lines)


def summarize(results: list[CaseResult]) -> str:
    """One-line summary of case counts by status."""
    passed = sum(1 for result in results if result.status == PASS)
    errored = sum(1 for result in results if result.status == ERROR)
    failed = len(results) - passed - errored
    noun = "case" if len(results) == 1 else "cases"
    return (
        f"Summary: {len(results)} {noun} — "
        f"{passed} passed, {failed} failed, {errored} errors"
    )


def _render_row(result: CaseResult) -> str:
    rules_summary = _rules_summary(result)
    judge_summary = _judge_summary(result)
    return (
        f"{result.example.ljust(9)}  "
        f"{rules_summary.ljust(28)}  "
        f"{judge_summary.ljust(5)}  "
        f"{result.status}"
    )


def _rules_summary(result: CaseResult) -> str:
    if result.error:
        return "-"
    passed = sum(1 for rule in result.rule_results if rule.passed)
    total = len(result.rule_results)
    failed_names = ",".join(rule.name for rule in result.rule_results if not rule.passed)
    summary = f"{passed}/{total}"
    return f"{summary} ✗ {failed_names}" if failed_names else f"{summary} ✓"


def _judge_summary(result: CaseResult) -> str:
    if result.judge_error:
        return ERROR
    if result.judge_result is None:
        return "-"
    return result.judge_result.verdict


def _render_verbose(result: CaseResult) -> list[str]:
    lines = [f"    output: {_indent(result.output)}"]
    for rule in result.rule_results:
        mark = "✓" if rule.passed else "✗"
        detail = f" — {rule.detail}" if rule.detail else ""
        lines.append(f"    rule {mark} {rule.name}{detail}")
    if result.judge_result is not None:
        for criterion in result.judge_result.criteria:
            mark = "✓" if criterion.met else "✗"
            lines.append(f"    judge {mark} {criterion.criterion} — {criterion.justification}")
    if result.judge_error:
        lines.append(f"    judge error: {result.judge_error}")
    if result.error:
        lines.append(f"    error: {result.error}")
    return lines


def _indent(text: str) -> str:
    return "\n           ".join(text.splitlines())
