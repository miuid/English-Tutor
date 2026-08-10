"""Tests for the skill execution service."""

import os
from dataclasses import replace
from pathlib import Path

import pytest

from app.config import Settings
from app.llm import FakeProvider, create_llm_provider
from app.skills import load_skill
from app.skills.executor import SkillExecutionService, select_packs, year_band_for

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


@pytest.mark.asyncio
async def test_execute_composes_prompt_with_references() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["structure feedback"])
    service = SkillExecutionService(provider=fake)
    inputs = {
        "year_level": "8",
        "text_type": "analytical",
        "task_prompt": "How does the poet present the effects of war?",
        "student_text": "In this poem the poet shows that war is bad.",
    }

    response = await service.execute(skill, inputs)

    assert response == "structure feedback"
    assert len(fake.calls) == 1
    system_prompt, messages = fake.calls[0]
    assert "PEEL/TEEL" in system_prompt
    assert "rubric.md" in system_prompt
    assert "student_text:" in messages[0]["content"]
    assert "war is bad" in messages[0]["content"]


@pytest.mark.asyncio
async def test_execute_uses_ordered_inputs_format() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["ok"])
    service = SkillExecutionService(provider=fake)
    inputs = {
        "student_text": "The text is interesting.",
        "year_level": "8",
        "text_type": "analytical",
        "task_prompt": "Discuss.",
        "extra": "ignored",
    }

    await service.execute(skill, inputs)

    content = fake.calls[0][1][0]["content"]
    assert content.startswith("year_level: 8\ntext_type: analytical\ntask_prompt: Discuss")
    assert "student_text:\n---\nThe text is interesting.\n---" in content
    assert "extra: ignored" in content


@pytest.mark.asyncio
async def test_execute_prompt_is_byte_identical_for_year_8_analytical() -> None:
    """Regression guard: current sessions get exactly the pre-P6.1 prompt."""
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["ok"])
    service = SkillExecutionService(provider=fake)
    inputs = {"year_level": "8", "text_type": "analytical", "student_text": "Text."}

    response = await service.execute(skill, inputs)

    rubric = (SKILLS_DIR / "check-structure" / "references" / "analytical" / "year-8" / "rubric.md")
    expected_prompt = (
        f"{skill.instructions}\n\n--- Reference material ---\n\n### rubric.md\n\n"
        f"{rubric.read_text(encoding='utf-8')}"
    )
    assert fake.calls[0][0] == expected_prompt
    assert response == "ok"  # exact pack exists: no degradation note


@pytest.mark.asyncio
async def test_execute_defaults_to_analytical_year_8() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["ok"])
    service = SkillExecutionService(provider=fake)

    response = await service.execute(skill, {"student_text": "Text."})

    assert response == "ok"  # no note: defaults resolve to the exact pack
    assert "rubric.md" in fake.calls[0][0]


@pytest.mark.parametrize(
    ("year_level", "expected_band"),
    [
        ("7", "year-8"),
        ("8", "year-8"),
        ("9", "year-9-10"),
        ("10", "year-9-10"),
        ("11", "year-11-12"),
        ("12", "year-11-12"),
        (None, "year-8"),
        ("", "year-8"),
        ("eight", "year-8"),
        (" 9 ", "year-9-10"),
    ],
)
def test_year_band_for(year_level: str | None, expected_band: str) -> None:
    assert year_band_for(year_level) == expected_band


def test_select_packs_prefers_exact_then_nearest_band() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")

    packs, used = select_packs(skill, "analytical", "year-8")
    assert used == "analytical/year-8"
    assert packs == [skill.packs["analytical/year-8"]]

    packs, used = select_packs(skill, "analytical", "year-11-12")
    assert used == "analytical/year-8"  # nearest band fallback
    assert packs == [skill.packs["analytical/year-8"]]

    packs, used = select_packs(skill, "persuasive", "year-8")
    assert used is None
    assert packs == []


def test_select_packs_shared_comes_first() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    packs_map = {
        "shared": {"common.md": "shared"},
        "analytical/year-8": {"rubric.md": "band"},
    }
    skill = replace(skill, packs=packs_map)

    packs, used = select_packs(skill, "analytical", "year-8")

    assert used == "analytical/year-8"
    assert packs == [packs_map["shared"], packs_map["analytical/year-8"]]


@pytest.mark.asyncio
async def test_execute_appends_degradation_note_on_band_fallback() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["feedback"])
    service = SkillExecutionService(provider=fake)
    inputs = {"year_level": "10", "text_type": "analytical", "student_text": "Text."}

    response = await service.execute(skill, inputs)

    assert "rubric.md" in fake.calls[0][0]  # nearest analytical band still included
    assert response.startswith("feedback")
    assert response.endswith(
        "_Note: no dedicated references for analytical/year-9-10; "
        "coached from the analytical/year-8 pack._"
    )


@pytest.mark.asyncio
async def test_execute_without_matching_pack_returns_response_with_note() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["feedback"])
    service = SkillExecutionService(provider=fake)
    inputs = {"year_level": "8", "text_type": "persuasive", "student_text": "Text."}

    response = await service.execute(skill, inputs)

    assert response  # a response, not an error
    assert "--- Reference material ---" not in fake.calls[0][0]
    assert response.endswith(
        "_Note: no dedicated references for persuasive/year-8; "
        "coached from skill instructions only._"
    )


@pytest.mark.asyncio
async def test_execute_skill_without_packs_never_adds_note() -> None:
    skill = load_skill(SKILLS_DIR / "guided-practice")
    fake = FakeProvider(canned_responses=["ok"])
    service = SkillExecutionService(provider=fake)
    inputs = {"year_level": "11", "text_type": "persuasive", "student_text": "Text."}

    response = await service.execute(skill, inputs)

    assert response == "ok"


@pytest.mark.skipif(
    os.environ.get("LLM_PROVIDER") != "anthropic" or not os.environ.get("LLM_API_KEY"),
    reason="Real LLM test requires LLM_PROVIDER=anthropic and LLM_API_KEY",
)
@pytest.mark.asyncio
async def test_execute_check_structure_real_sample() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    settings = Settings()
    provider = create_llm_provider(settings)
    service = SkillExecutionService(provider=provider)

    sample = (SKILLS_DIR / "check-structure" / "examples" / "sample-01.md").read_text()
    lines = sample.splitlines()
    inputs = {
        "year_level": lines[0].split(":", 1)[1].strip(),
        "text_type": lines[1].split(":", 1)[1].strip(),
        "task_prompt": lines[2].split(":", 1)[1].strip(),
        "student_text": "\n".join(lines[4:]).strip(),
    }

    response = await service.execute(skill, inputs)
    assert response
    assert "Structure snapshot:" in response
    assert "Your next move:" in response
    assert "Try this:" in response
