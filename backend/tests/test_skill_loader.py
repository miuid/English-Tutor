from pathlib import Path

import pytest

from app.skills import load_skill, load_skills

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


def test_load_skills_returns_all_eight() -> None:
    skills = load_skills(SKILLS_DIR)
    assert len(skills) == 8
    names = {skill.name for skill in skills}
    assert names == {
        "set-success-criteria",
        "model-response",
        "guided-practice",
        "independent-task",
        "diagnose-errors",
        "check-structure",
        "elevate-vocabulary",
        "give-feedback",
    }


def test_load_skill_requires_skill_md(tmp_path: Path) -> None:
    skill_dir = tmp_path / "empty-skill"
    skill_dir.mkdir()
    with pytest.raises(ValueError, match="missing SKILL.md"):
        load_skill(skill_dir)


def test_load_skill_requires_sections(tmp_path: Path) -> None:
    skill_dir = tmp_path / "bad-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# bad-skill\n\n## Purpose\nOnly purpose.\n")
    with pytest.raises(ValueError, match="missing required sections"):
        load_skill(skill_dir)


def test_check_structure_loads_rubric_and_example() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    assert "rubric.md" in skill.packs["analytical/year-8"]
    assert len(skill.examples) >= 1
    assert skill.loop_stage == "coach"
    assert "PEEL" in skill.method
    assert "PEEL/TEEL" in skill.pedagogical_basis


def test_reference_files_load_into_analytical_year_8_pack() -> None:
    expected = {
        "check-structure": "rubric.md",
        "diagnose-errors": "taxonomy.md",
        "elevate-vocabulary": "tiers.md",
        "give-feedback": "rubric.md",
        "independent-task": "task-specs.md",
        "set-success-criteria": "criteria-bank.md",
    }
    for name, filename in expected.items():
        skill = load_skill(SKILLS_DIR / name)
        assert list(skill.packs) == ["analytical/year-8"], name
        assert list(skill.packs["analytical/year-8"]) == [filename], name
        assert skill.packs["analytical/year-8"][filename].strip(), name


def test_skills_without_references_have_empty_packs() -> None:
    for name in ("model-response", "guided-practice"):
        skill = load_skill(SKILLS_DIR / name)
        assert skill.packs == {}, name


def _write_minimal_skill(skill_dir: Path) -> None:
    skill_dir.mkdir(parents=True)
    sections = "\n\n".join(
        f"## {section}\ncontent." for section in REQUIRED_SECTION_NAMES
    )
    (skill_dir / "SKILL.md").write_text(f"# x\n\n{sections}\n", encoding="utf-8")


REQUIRED_SECTION_NAMES = [
    "Purpose",
    "When to use",
    "Inputs",
    "Pedagogical basis",
    "Method",
    "Output contract",
    "Success criteria",
    "Guardrails",
]


def test_loads_shared_and_banded_packs(tmp_path: Path) -> None:
    skill_dir = tmp_path / "packed-skill"
    _write_minimal_skill(skill_dir)
    shared_dir = skill_dir / "references" / "shared"
    band_dir = skill_dir / "references" / "analytical" / "year-9-10"
    shared_dir.mkdir(parents=True)
    band_dir.mkdir(parents=True)
    (shared_dir / "common.md").write_text("shared content", encoding="utf-8")
    (band_dir / "rubric.md").write_text("band content", encoding="utf-8")

    skill = load_skill(skill_dir)

    assert set(skill.packs) == {"shared", "analytical/year-9-10"}
    assert skill.packs["shared"] == {"common.md": "shared content"}
    assert skill.packs["analytical/year-9-10"] == {"rubric.md": "band content"}
