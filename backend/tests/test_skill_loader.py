from pathlib import Path

import pytest

from app.skills import load_skill, load_skills

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


def test_load_skills_returns_all_thirteen() -> None:
    skills = load_skills(SKILLS_DIR)
    assert len(skills) == 13
    names = {skill.name for skill in skills}
    assert names == {
        "spaced-review",
        "set-success-criteria",
        "model-response",
        "guided-practice",
        "independent-task",
        "diagnose-errors",
        "check-structure",
        "elevate-vocabulary",
        "strengthen-argument",
        "craft-voice",
        "give-feedback",
        "baseline-assessment",
        "fix-mechanics",
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
        assert "analytical/year-8" in skill.packs, name
        assert list(skill.packs["analytical/year-8"]) == [filename], name
        assert skill.packs["analytical/year-8"][filename].strip(), name


def test_reference_files_load_into_analytical_year_9_10_pack() -> None:
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
        assert "analytical/year-9-10" in skill.packs, name
        assert list(skill.packs["analytical/year-9-10"]) == [filename], name
        assert skill.packs["analytical/year-9-10"][filename].strip(), name


def test_reference_files_load_into_analytical_year_11_12_pack() -> None:
    # ISS-025: senior analytical packs (IA2 + EA framework), sourced from the
    # official QCAA English 2025 v1.3 syllabus.
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
        assert "analytical/year-11-12" in skill.packs, name
        assert list(skill.packs["analytical/year-11-12"]) == [filename], name
        content = skill.packs["analytical/year-11-12"][filename]
        assert content.strip(), name
        # Every senior pack must cite the official syllabus source (Q-001).
        assert "English 2025 v1.3" in content, name


def test_skills_without_references_have_empty_packs() -> None:
    for name in ("model-response", "guided-practice"):
        skill = load_skill(SKILLS_DIR / name)
        assert skill.packs == {}, name


def test_strengthen_argument_loads_persuasive_packs_and_examples() -> None:
    skill = load_skill(SKILLS_DIR / "strengthen-argument")
    assert skill.loop_stage == "coach"
    for band in ("year-8", "year-9-10"):
        pack_key = f"persuasive/{band}"
        assert pack_key in skill.packs
        assert list(skill.packs[pack_key]) == ["argument-chains.md"]
        assert skill.packs[pack_key]["argument-chains.md"].strip()
    assert len(skill.examples) == 2
    assert "rebuttal" in skill.method

def test_craft_voice_loads_imaginative_packs_and_examples() -> None:
    skill = load_skill(SKILLS_DIR / "craft-voice")
    assert skill.loop_stage == "coach"
    for band in ("year-8", "year-9-10"):
        pack_key = f"imaginative/{band}"
        assert pack_key in skill.packs
        assert list(skill.packs[pack_key]) == ["voice-craft.md"]
        assert skill.packs[pack_key]["voice-craft.md"].strip()
    assert len(skill.examples) == 2
    assert "POV" in skill.method


def test_baseline_assessment_loads_shared_guide_and_examples() -> None:
    skill = load_skill(SKILLS_DIR / "baseline-assessment")
    assert skill.loop_stage == "baseline"
    assert list(skill.packs) == ["shared"]
    assert list(skill.packs["shared"]) == ["baseline-guide.md"]
    guide = skill.packs["shared"]["baseline-guide.md"]
    # The day-0 criterion names must match the loop's feedback rubric rows.
    assert "Analysis (how techniques create meaning)" in guide
    assert "Understanding of text / ideas" in guide
    assert len(skill.examples) == 2
    assert "Per-criterion levels" in skill.output_contract


def test_fix_mechanics_loads_shared_guide_and_examples() -> None:
    skill = load_skill(SKILLS_DIR / "fix-mechanics")
    assert skill.loop_stage == "coach"
    assert list(skill.packs) == ["shared"]
    assert list(skill.packs["shared"]) == ["mechanics-guide.md"]
    guide = skill.packs["shared"]["mechanics-guide.md"]
    # The guide must cover the coached error classes and the band ceilings.
    assert "Comma splices" in guide
    assert "Year 11–12" in guide
    assert len(skill.examples) == 2
    # Bounded feedback is the skill's hard limit: never more than 2 patterns.
    assert "at most 2 patterns" in skill.success_criteria


def test_spaced_review_loads_shared_guide_and_examples() -> None:
    skill = load_skill(SKILLS_DIR / "spaced-review")
    assert skill.loop_stage == "retrieval"
    assert list(skill.packs) == ["shared"]
    assert list(skill.packs["shared"]) == ["retrieval-guide.md"]
    guide = skill.packs["shared"]["retrieval-guide.md"]
    # The guide must cover the digest shape, the cold-start menu, and the
    # band calibration; the skill input contract carries the history digest.
    assert "review_history" in skill.inputs
    assert "No prior sessions" in guide
    assert "Cold-start menu" in guide
    assert "Year 11–12" in guide
    assert len(skill.examples) == 2
    # The warm-up is bounded by design: 2–3 items, never a second lesson.
    assert "2–3" in skill.success_criteria


PACK_BEARING_SKILLS = {
    "check-structure": "rubric.md",
    "diagnose-errors": "taxonomy.md",
    "elevate-vocabulary": "tiers.md",
    "give-feedback": "rubric.md",
    "independent-task": "task-specs.md",
    "set-success-criteria": "criteria-bank.md",
}


def test_reference_files_load_into_persuasive_year_8_pack() -> None:
    for name, filename in PACK_BEARING_SKILLS.items():
        skill = load_skill(SKILLS_DIR / name)
        assert "persuasive/year-8" in skill.packs, name
        assert list(skill.packs["persuasive/year-8"]) == [filename], name
        assert skill.packs["persuasive/year-8"][filename].strip(), name


def test_reference_files_load_into_persuasive_year_9_10_pack() -> None:
    for name, filename in PACK_BEARING_SKILLS.items():
        skill = load_skill(SKILLS_DIR / name)
        assert "persuasive/year-9-10" in skill.packs, name
        assert list(skill.packs["persuasive/year-9-10"]) == [filename], name
        assert skill.packs["persuasive/year-9-10"][filename].strip(), name


def test_reference_files_load_into_imaginative_year_8_pack() -> None:
    for name, filename in PACK_BEARING_SKILLS.items():
        skill = load_skill(SKILLS_DIR / name)
        assert "imaginative/year-8" in skill.packs, name
        assert list(skill.packs["imaginative/year-8"]) == [filename], name
        assert skill.packs["imaginative/year-8"][filename].strip(), name


def test_reference_files_load_into_imaginative_year_9_10_pack() -> None:
    for name, filename in PACK_BEARING_SKILLS.items():
        skill = load_skill(SKILLS_DIR / name)
        assert "imaginative/year-9-10" in skill.packs, name
        assert list(skill.packs["imaginative/year-9-10"]) == [filename], name
        assert skill.packs["imaginative/year-9-10"][filename].strip(), name


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
