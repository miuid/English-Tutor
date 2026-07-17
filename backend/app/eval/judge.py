"""LLM-as-judge: score a skill's output against its expected-behaviour rubric.

The judge is a second provider call with a dedicated prompt. It must answer in
a strict machine-parseable format — one verdict line per rubric criterion, then
a final verdict line::

    ✓ <criterion> — <one-line justification>
    ✗ <criterion> — <one-line justification>
    VERDICT: PASS

``parse_judge_response`` parses strictly: anything else raises
``JudgeParseError`` (counted as a judge ERROR, never as a pass).
"""

import re
from dataclasses import dataclass

from app.llm.provider import LLMProvider

JUDGE_SYSTEM_PROMPT = """\
You are a strict evaluator for an AI English tutor's teaching skills.

Judge the skill's output ONLY against the behaviour rubric you are given — \
not against general writing quality and not against your own idea of a good \
answer. Each distinct expectation in the rubric is one criterion. If the output \
exhibits a behaviour listed under "Fail conditions", the matching criterion \
fails.

Reply in EXACTLY this machine-readable format and nothing else:
✓ <criterion> — <one-line justification>
✗ <criterion> — <one-line justification>
VERDICT: PASS

Rules:
- One line per rubric criterion, starting with ✓ (met) or ✗ (not met).
- The final line must be `VERDICT: PASS` if every criterion is met, otherwise \
`VERDICT: FAIL`.
- No headings, no preamble, no commentary, no extra lines."""

JUDGE_USER_TEMPLATE = """\
skill: {skill_name}

sample input:
---
{sample}
---

behaviour rubric (the ONLY standard to judge against):
---
{expected}
---

actual output to judge:
---
{output}
---"""

_VERDICT_RE = re.compile(r"^VERDICT:\s*(PASS|FAIL)\s*$")
_CRITERION_RE = re.compile(r"^(?P<mark>[✓✗])\s+(?P<body>\S.*)$")
_SEPARATOR_RE = re.compile(r"\s+[—–-]\s+")


class JudgeParseError(ValueError):
    """Raised when judge output does not follow the required format."""


@dataclass(frozen=True)
class CriterionResult:
    criterion: str
    met: bool
    justification: str


@dataclass(frozen=True)
class JudgeResult:
    criteria: list[CriterionResult]
    verdict: str  # "PASS" | "FAIL"


async def judge_output(
    provider: LLMProvider,
    *,
    skill_name: str,
    sample: str,
    expected: str,
    output: str,
) -> JudgeResult:
    """Run the judging prompt and parse the verdict. Raises JudgeParseError."""
    user_message = JUDGE_USER_TEMPLATE.format(
        skill_name=skill_name,
        sample=sample,
        expected=expected,
        output=output,
    )
    response = await provider.generate(
        JUDGE_SYSTEM_PROMPT,
        [{"role": "user", "content": user_message}],
    )
    return parse_judge_response(response)


def parse_judge_response(text: str) -> JudgeResult:
    """Strictly parse judge output; raise JudgeParseError on anything malformed."""
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        msg = "judge output is empty"
        raise JudgeParseError(msg)

    verdict_match = _VERDICT_RE.match(lines[-1])
    if not verdict_match:
        msg = f"final line is not 'VERDICT: PASS|FAIL': {lines[-1]!r}"
        raise JudgeParseError(msg)

    criteria: list[CriterionResult] = []
    for line in lines[:-1]:
        criterion_match = _CRITERION_RE.match(line)
        if not criterion_match:
            msg = f"line is not a '✓/✗ <criterion>' line: {line!r}"
            raise JudgeParseError(msg)
        body = criterion_match.group("body")
        parts = _SEPARATOR_RE.split(body, maxsplit=1)
        criteria.append(
            CriterionResult(
                criterion=parts[0].strip(),
                met=criterion_match.group("mark") == "✓",
                justification=parts[1].strip() if len(parts) > 1 else "",
            )
        )

    if not criteria:
        msg = "judge output has no criterion lines"
        raise JudgeParseError(msg)

    verdict = verdict_match.group(1)
    if verdict == "PASS" and any(not criterion.met for criterion in criteria):
        msg = "verdict is PASS but at least one criterion is marked ✗"
        raise JudgeParseError(msg)

    return JudgeResult(criteria=criteria, verdict=verdict)
