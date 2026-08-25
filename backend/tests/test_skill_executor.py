"""Tests for the skill execution service."""

import os
from dataclasses import replace
from pathlib import Path
from typing import cast

import pytest

from app.config import Settings
from app.llm import FakeProvider, StageProviderRouter, create_llm_provider
from app.skills import load_skill
from app.skills.executor import (
    COACH_TONE_DIRECTIVES,
    SkillExecutionService,
    select_packs,
    year_band_for,
)

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
    assert used == "analytical/year-11-12"  # exact pack exists (ISS-025)
    assert packs == [skill.packs["analytical/year-11-12"]]

    packs, used = select_packs(skill, "persuasive", "year-8")
    assert used == "persuasive/year-8"
    assert packs == [skill.packs["persuasive/year-8"]]

    packs, used = select_packs(skill, "persuasive", "year-11-12")
    assert used == "persuasive/year-8"  # nearest band fallback
    assert packs == [skill.packs["persuasive/year-8"]]

    packs, used = select_packs(skill, "imaginative", "year-8")
    assert used == "imaginative/year-8"
    assert packs == [skill.packs["imaginative/year-8"]]

    packs, used = select_packs(skill, "imaginative", "year-11-12")
    assert used == "imaginative/year-8"  # nearest band fallback
    assert packs == [skill.packs["imaginative/year-8"]]

    packs, used = select_packs(skill, "poetry", "year-8")
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
async def test_execute_year_11_12_uses_exact_pack_without_degradation_note() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["feedback"])
    service = SkillExecutionService(provider=fake)
    inputs = {"year_level": "12", "text_type": "analytical", "student_text": "Text."}

    response = await service.execute(skill, inputs)

    assert "rubric.md" in fake.calls[0][0]
    assert "discerning" in fake.calls[0][0]  # year-11-12 pack content (IA2 ISMG qualifier)
    assert response == "feedback"  # exact pack exists: no degradation note


@pytest.mark.asyncio
async def test_execute_year_9_10_uses_exact_pack_without_degradation_note() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["feedback"])
    service = SkillExecutionService(provider=fake)
    inputs = {"year_level": "9", "text_type": "analytical", "student_text": "Text."}

    response = await service.execute(skill, inputs)

    assert "rubric.md" in fake.calls[0][0]
    assert "representation" in fake.calls[0][0]  # year-9-10 pack content
    assert response == "feedback"  # exact pack exists: no degradation note


@pytest.mark.asyncio
async def test_execute_persuasive_year_9_uses_exact_pack_without_degradation_note() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["feedback"])
    service = SkillExecutionService(provider=fake)
    inputs = {"year_level": "9", "text_type": "persuasive", "student_text": "Text."}

    response = await service.execute(skill, inputs)

    assert "rubric.md" in fake.calls[0][0]
    assert "contention" in fake.calls[0][0]  # persuasive pack content
    assert response == "feedback"  # exact pack exists: no degradation note


@pytest.mark.asyncio
async def test_execute_appends_degradation_note_on_persuasive_band_fallback() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["feedback"])
    service = SkillExecutionService(provider=fake)
    inputs = {"year_level": "12", "text_type": "persuasive", "student_text": "Text."}

    response = await service.execute(skill, inputs)

    assert "rubric.md" in fake.calls[0][0]  # nearest persuasive band still included
    assert response.startswith("feedback")
    assert response.endswith(
        "_Note: no dedicated references for persuasive/year-11-12; "
        "coached from the persuasive/year-8 pack._"
    )


@pytest.mark.asyncio
async def test_execute_imaginative_year_9_uses_exact_pack_without_degradation_note() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["feedback"])
    service = SkillExecutionService(provider=fake)
    inputs = {"year_level": "9", "text_type": "imaginative", "student_text": "Text."}

    response = await service.execute(skill, inputs)

    assert "rubric.md" in fake.calls[0][0]
    assert "complication" in fake.calls[0][0]  # imaginative pack content
    assert response == "feedback"  # exact pack exists: no degradation note


@pytest.mark.asyncio
async def test_execute_appends_degradation_note_on_imaginative_band_fallback() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["feedback"])
    service = SkillExecutionService(provider=fake)
    inputs = {"year_level": "12", "text_type": "imaginative", "student_text": "Text."}

    response = await service.execute(skill, inputs)

    assert "rubric.md" in fake.calls[0][0]  # nearest imaginative band still included
    assert response.startswith("feedback")
    assert response.endswith(
        "_Note: no dedicated references for imaginative/year-11-12; "
        "coached from the imaginative/year-8 pack._"
    )


@pytest.mark.asyncio
async def test_execute_without_matching_pack_returns_response_with_note() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["feedback"])
    service = SkillExecutionService(provider=fake)
    inputs = {"year_level": "8", "text_type": "poetry", "student_text": "Text."}

    response = await service.execute(skill, inputs)

    assert response  # a response, not an error
    assert "--- Reference material ---" not in fake.calls[0][0]
    assert response.endswith(
        "_Note: no dedicated references for poetry/year-8; "
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


@pytest.mark.asyncio
async def test_execute_shared_only_skill_adds_no_degradation_note() -> None:
    """Shared-only skills are combo-agnostic: no banded pack to degrade from."""
    skill = load_skill(SKILLS_DIR / "baseline-assessment")
    fake = FakeProvider(canned_responses=["baseline report"])
    service = SkillExecutionService(provider=fake)
    inputs = {"year_level": "9", "text_type": "imaginative", "student_text": "Text."}

    response = await service.execute(skill, inputs)

    assert response == "baseline report"
    # The shared guide still lands in the system prompt.
    assert "baseline-guide.md" in fake.calls[0][0]


@pytest.mark.asyncio
@pytest.mark.parametrize("tone", ["warm", "strict", "humorous"])
async def test_execute_injects_coach_tone_directive_into_system_prompt(tone: str) -> None:
    """A coach_tone input adds the tone directive to the system prompt only."""
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["ok"])
    service = SkillExecutionService(provider=fake)
    inputs = {
        "year_level": "8",
        "text_type": "analytical",
        "coach_tone": tone,
        "student_text": "Text.",
    }

    response = await service.execute(skill, inputs)

    assert response == "ok"
    system_prompt, messages = fake.calls[0]
    assert "--- Coach tone ---" in system_prompt
    assert COACH_TONE_DIRECTIVES[tone] in system_prompt
    # The contract reminder pins tone to style, never teaching content.
    assert "never what you teach" in system_prompt
    # Tone is prompt-level only: it never leaks into the user message.
    assert "coach_tone" not in messages[0]["content"]


@pytest.mark.asyncio
async def test_execute_same_input_yields_different_tone_identical_contract() -> None:
    """Same input + different tones: system prompts differ, outputs do not."""
    skill = load_skill(SKILLS_DIR / "check-structure")
    prompts: dict[str, str] = {}
    for tone in ("warm", "strict", "humorous"):
        fake = FakeProvider(canned_responses=["identical contract output"])
        service = SkillExecutionService(provider=fake)
        response = await service.execute(
            skill,
            {
                "year_level": "8",
                "text_type": "analytical",
                "coach_tone": tone,
                "student_text": "Text.",
            },
        )
        # The skill output contract is tone-invariant.
        assert response == "identical contract output"
        prompts[tone] = fake.calls[0][0]
    # Each tone produces a perceptibly different system prompt.
    assert len(set(prompts.values())) == 3


@pytest.mark.asyncio
async def test_execute_unknown_coach_tone_falls_back_to_warm() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["ok"])
    service = SkillExecutionService(provider=fake)

    await service.execute(
        skill,
        {
            "year_level": "8",
            "text_type": "analytical",
            "coach_tone": "sassy",
            "student_text": "T.",
        },
    )

    system_prompt = fake.calls[0][0]
    assert COACH_TONE_DIRECTIVES["warm"] in system_prompt
    assert "sassy" not in system_prompt


@pytest.mark.asyncio
async def test_execute_without_coach_tone_adds_no_tone_section() -> None:
    """No coach_tone input -> no tone section (byte-identical legacy prompts)."""
    skill = load_skill(SKILLS_DIR / "check-structure")
    fake = FakeProvider(canned_responses=["ok"])
    service = SkillExecutionService(provider=fake)

    await service.execute(
        skill, {"year_level": "8", "text_type": "analytical", "student_text": "Text."}
    )

    assert "--- Coach tone ---" not in fake.calls[0][0]


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


@pytest.mark.asyncio
async def test_execute_routes_to_the_skills_stage_provider() -> None:
    """With a stage router, the executor picks the provider for the skill's
    loop stage and reports the stage-routed model name (ISS-021)."""
    skill = load_skill(SKILLS_DIR / "check-structure")  # loop_stage "coach"
    settings = Settings(
        llm_provider="fake",
        llm_model="fake-base",
        llm_api_key="",
        llm_stage_models={"coach": "fake-strong"},
    )
    router = StageProviderRouter(settings)
    default_provider = FakeProvider(canned_responses=["default output"])
    service = SkillExecutionService(
        provider=default_provider, model_name="fake-base", stage_router=router
    )

    response = await service.execute(
        skill, {"year_level": "8", "text_type": "analytical", "student_text": "Text."}
    )

    stage_provider = cast("FakeProvider", router.for_stage("coach")[0])
    assert len(stage_provider.calls) == 1
    assert default_provider.calls == []
    assert response == "fake response"
    assert service.model_used_for(skill) == "fake-strong"


def test_model_used_for_falls_back_to_model_name_without_router() -> None:
    skill = load_skill(SKILLS_DIR / "check-structure")
    service = SkillExecutionService(provider=FakeProvider(), model_name="fake-base")
    assert service.model_used_for(skill) == "fake-base"
