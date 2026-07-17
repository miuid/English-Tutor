"""Tests for the skill execution service."""

import os
from pathlib import Path

import pytest

from app.config import Settings
from app.llm import FakeProvider, create_llm_provider
from app.skills import load_skill
from app.skills.executor import SkillExecutionService

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
