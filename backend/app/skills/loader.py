"""Load agent skills from Markdown packages in the skills directory."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SkillExample:
    sample: str
    expected: str


@dataclass(frozen=True)
class Skill:
    name: str
    folder: str
    instructions: str
    purpose: str
    when_to_use: str
    inputs: str
    pedagogical_basis: str
    method: str
    output_contract: str
    success_criteria: str
    guardrails: str
    loop_stage: str
    packs: dict[str, dict[str, str]]
    examples: list[SkillExample]


REQUIRED_SECTIONS = [
    "purpose",
    "when to use",
    "inputs",
    "pedagogical basis",
    "method",
    "output contract",
    "success criteria",
    "guardrails",
]

# Orchestration stage for each skill. This belongs in skill metadata long-term.
LOOP_STAGES: dict[str, str] = {
    "set-success-criteria": "start",
    "model-response": "I do",
    "guided-practice": "we do",
    "independent-task": "you do",
    "diagnose-errors": "triage",
    "check-structure": "coach",
    "elevate-vocabulary": "coach",
    "give-feedback": "end",
}


def load_skills(skills_dir: Path) -> list[Skill]:
    """Load every skill package under skills_dir."""
    skills = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        skills.append(load_skill(skill_dir))
    return skills


def load_skill(skill_dir: Path) -> Skill:
    """Load a single skill package."""
    if not skill_dir.is_dir():
        msg = f"Skill path is not a directory: {skill_dir}"
        raise ValueError(msg)

    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        msg = f"Skill directory {skill_dir} is missing SKILL.md"
        raise ValueError(msg)

    raw = skill_file.read_text(encoding="utf-8")
    sections = _parse_sections(raw)

    missing = [section for section in REQUIRED_SECTIONS if section not in sections]
    if missing:
        msg = f"Skill {skill_dir.name} is missing required sections: {', '.join(missing)}"
        raise ValueError(msg)

    packs = _load_packs(skill_dir)
    examples = _load_examples(skill_dir / "examples")

    return Skill(
        name=skill_dir.name,
        folder=str(skill_dir),
        instructions=raw,
        purpose=sections["purpose"],
        when_to_use=sections["when to use"],
        inputs=sections["inputs"],
        pedagogical_basis=sections["pedagogical basis"],
        method=sections["method"],
        output_contract=sections["output contract"],
        success_criteria=sections["success criteria"],
        guardrails=sections["guardrails"],
        loop_stage=LOOP_STAGES.get(skill_dir.name, "unknown"),
        packs=packs,
        examples=examples,
    )


def _parse_sections(raw: str) -> dict[str, str]:
    """Split SKILL.md on ## headers into a map of lower-cased section names."""
    sections: dict[str, str] = {}
    current_header: str | None = None
    current_lines: list[str] = []
    for line in raw.splitlines():
        if line.startswith("## "):
            if current_header is not None:
                sections[current_header] = "\n".join(current_lines).strip()
            current_header = line[3:].strip().split("(")[0].strip().lower()
            current_lines = []
        elif current_header is not None:
            current_lines.append(line)
    if current_header is not None:
        sections[current_header] = "\n".join(current_lines).strip()
    return sections


def _load_packs(skill_dir: Path) -> dict[str, dict[str, str]]:
    """Load references/**/*.md into packs keyed by "shared" or "<text_type>/<year_band>".

    A file at ``references/shared/<name>.md`` lands in the ``shared`` pack; a file
    at ``references/<text_type>/<year_band>/<name>.md`` lands in the
    ``"<text_type>/<year_band>"`` pack. Each pack maps filename → content.
    """
    packs: dict[str, dict[str, str]] = {}
    references_dir = skill_dir / "references"
    if not references_dir.is_dir():
        return packs
    for ref_file in sorted(references_dir.rglob("*.md")):
        pack_key = "/".join(ref_file.relative_to(references_dir).parent.parts) or "shared"
        packs.setdefault(pack_key, {})[ref_file.name] = ref_file.read_text(encoding="utf-8")
    return packs


def _load_examples(examples_dir: Path) -> list[SkillExample]:
    """Load paired sample-NN.md / expected-NN.md fixtures."""
    examples: list[SkillExample] = []
    if not examples_dir.exists():
        return examples
    for sample_file in sorted(examples_dir.glob("sample-*.md")):
        expected_file = examples_dir / sample_file.name.replace("sample-", "expected-", 1)
        if not expected_file.exists():
            continue
        examples.append(
            SkillExample(
                sample=sample_file.read_text(encoding="utf-8"),
                expected=expected_file.read_text(encoding="utf-8"),
            )
        )
    return examples
