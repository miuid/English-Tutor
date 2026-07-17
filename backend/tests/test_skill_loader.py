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
    assert "rubric.md" in skill.references
    assert len(skill.examples) >= 1
    assert skill.loop_stage == "coach"
    assert "PEEL" in skill.method
    assert "PEEL/TEEL" in skill.pedagogical_basis
