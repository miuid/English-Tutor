"""Deterministic rule checks for eval outputs (no LLM involved).

A rule check is one small function ``(output, context) -> RuleResult`` plus one
entry in ``GENERIC_RULES`` (applies to every skill) or ``SKILL_RULES`` (applies
to one skill). Checks are mechanically derived from each skill's documented
fail conditions; anything semantic belongs to the LLM judge, not here.
"""

import re
from collections.abc import Callable
from dataclasses import dataclass

# Bounded-feedback spirit: generous cap well above what any skill should emit.
MAX_OUTPUT_CHARS = 4000


@dataclass(frozen=True)
class RuleContext:
    """Shared context available to rule checks."""

    skill_names: tuple[str, ...]


@dataclass(frozen=True)
class RuleResult:
    name: str
    passed: bool
    detail: str


RuleCheck = Callable[[str, RuleContext], RuleResult]


def check_non_empty(output: str, context: RuleContext) -> RuleResult:
    """Every skill must return something."""
    passed = bool(output.strip())
    return RuleResult("non-empty", passed, "" if passed else "output is empty")


def check_bounded_length(output: str, context: RuleContext) -> RuleResult:
    """Output stays under a generous length cap."""
    length = len(output)
    passed = length <= MAX_OUTPUT_CHARS
    detail = "" if passed else f"{length} chars exceeds cap of {MAX_OUTPUT_CHARS}"
    return RuleResult("bounded-length", passed, detail)


_NUMBERED_STEP_RE = re.compile(r"^\s*\d+[.)]\s+\S", re.MULTILINE)


def check_max_two_next_steps(output: str, context: RuleContext) -> RuleResult:
    """give-feedback: at most 2 numbered next steps (bounded feedback).

    Heuristic: counts numbered-list lines (`1.`, `2)` ...) in the whole output;
    the give-feedback contract contains no other numbered lists.
    """
    count = len(_NUMBERED_STEP_RE.findall(output))
    passed = count <= 2
    detail = "" if passed else f"found {count} numbered steps (max 2)"
    return RuleResult("max-two-next-steps", passed, detail)


_METACOGNITIVE_RE = re.compile(
    r"self[- ]?rat|rate yourself|how would you rate|would you give yourself",
    re.IGNORECASE,
)


def check_metacognitive_prompt(output: str, context: RuleContext) -> RuleResult:
    """give-feedback: asks the student to self-rate (a question about self-rating)."""
    passed = "?" in output and bool(_METACOGNITIVE_RE.search(output))
    detail = "" if passed else "no self-rating question found"
    return RuleResult("metacognitive-prompt", passed, detail)


_ROUTE_RE = re.compile(r"^\s*Route to:\s*([a-z0-9\-]+)", re.IGNORECASE | re.MULTILINE)


def check_route_line(output: str, context: RuleContext) -> RuleResult:
    """diagnose-errors: output names a valid route, matching the router contract."""
    match = _ROUTE_RE.search(output)
    if not match:
        return RuleResult("route-line", False, "no 'Route to:' line found")
    route = match.group(1).strip().lower()
    passed = route in context.skill_names
    detail = "" if passed else f"route '{route}' is not a known skill"
    return RuleResult("route-line", passed, detail)


GENERIC_RULES: tuple[RuleCheck, ...] = (check_non_empty, check_bounded_length)

SKILL_RULES: dict[str, tuple[RuleCheck, ...]] = {
    "give-feedback": (check_max_two_next_steps, check_metacognitive_prompt),
    "diagnose-errors": (check_route_line,),
}


def checks_for(skill_name: str) -> tuple[RuleCheck, ...]:
    """Return the generic + skill-specific checks for a skill."""
    return GENERIC_RULES + SKILL_RULES.get(skill_name, ())
