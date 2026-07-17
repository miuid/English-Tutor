"""Discover eval cases from skill example fixtures.

Each ``sample-NN.md`` fixture uses a simple header/body format::

    year_level: 8
    text_type: analytical
    task_prompt: "How does the poet present the effects of war?"
    success_criteria:
      - I can start with a clear point that answers the question.

    ---

    <student text>

Sample → inputs mapping (kept deliberately simple):

- Header ``key: value`` lines map directly to executor input keys. Indented
  continuation lines (e.g. a ``- item`` list) belong to the previous key and
  are kept as a multi-line value. Matching surrounding quotes are stripped.
- The body after ``---`` becomes ``student_text``. If the header already
  provided ``student_text``, the body becomes ``context`` instead (see
  ``guided-practice``), unless the header also provided ``context``.
- Missing ``year_level`` / ``text_type`` default to ``"8"`` / ``"analytical"``
  (the MVP defaults), since every v1 skill expects them.
- Fallback: a sample with no parseable header and no separator is treated as
  bare student text (``{"student_text": sample}``).
"""

from dataclasses import dataclass

from app.skills.loader import Skill

SEPARATOR = "---"

DEFAULT_INPUTS = {
    "year_level": "8",
    "text_type": "analytical",
}


@dataclass(frozen=True)
class EvalCase:
    """One eval case: a skill executed against one example fixture."""

    skill: Skill
    example: str
    inputs: dict[str, str]
    sample: str
    expected: str


def parse_sample_inputs(sample: str) -> dict[str, str]:
    """Parse a sample-NN.md fixture into executor inputs (see module docstring)."""
    lines = sample.splitlines()
    split_at = next(
        (i for i, line in enumerate(lines) if line.strip() == SEPARATOR),
        len(lines),
    )
    inputs = _parse_header("\n".join(lines[:split_at]))
    body = "\n".join(lines[split_at + 1 :]).strip()
    if not inputs and not body and sample.strip():
        # Fallback: a sample that is just student text, no header/separator.
        inputs["student_text"] = sample.strip()
    if body:
        if "student_text" not in inputs:
            inputs["student_text"] = body
        elif "context" not in inputs:
            inputs["context"] = body
    for key, default in DEFAULT_INPUTS.items():
        inputs.setdefault(key, default)
    return inputs


def discover_cases(skills: list[Skill]) -> list[EvalCase]:
    """Build one eval case per SkillExample across all skills."""
    cases: list[EvalCase] = []
    for skill in skills:
        for index, example in enumerate(skill.examples, start=1):
            cases.append(
                EvalCase(
                    skill=skill,
                    example=f"sample-{index:02d}",
                    inputs=parse_sample_inputs(example.sample),
                    sample=example.sample,
                    expected=example.expected,
                )
            )
    return cases


def _parse_header(header_text: str) -> dict[str, str]:
    """Parse `key: value` lines; indented lines continue the previous value."""
    inputs: dict[str, str] = {}
    current_key: str | None = None
    for line in header_text.splitlines():
        if not line.strip() or line.strip() == SEPARATOR:
            continue
        if not line.startswith((" ", "\t")) and ":" in line:
            key, _, value = line.partition(":")
            current_key = key.strip()
            inputs[current_key] = _unquote(value.strip())
        elif current_key is not None:
            continued = line.strip()
            if continued:
                existing = inputs[current_key]
                inputs[current_key] = f"{existing}\n{continued}" if existing else continued
    return inputs


def _unquote(value: str) -> str:
    """Strip one pair of matching surrounding quotes, if present."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value
