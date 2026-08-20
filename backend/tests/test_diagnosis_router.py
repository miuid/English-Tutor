"""Tests for the diagnosis router."""

from pathlib import Path

import pytest

from app.llm import FakeProvider
from app.skills import load_skills
from app.skills.executor import SkillExecutionService
from app.skills.router import DiagnosisRouter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


@pytest.fixture
def router() -> DiagnosisRouter:
    skills = load_skills(SKILLS_DIR)
    executor = SkillExecutionService(provider=FakeProvider())
    return DiagnosisRouter(executor=executor, skills=skills)


def test_parse_route_extracts_target(router: DiagnosisRouter) -> None:
    diagnosis = "...\nRoute to: check-structure\n"
    assert router.parse_route(diagnosis) == "check-structure"


def test_parse_route_handles_whitespace(router: DiagnosisRouter) -> None:
    diagnosis = "  Route to:   elevate-vocabulary  \n"
    assert router.parse_route(diagnosis) == "elevate-vocabulary"


def test_parse_route_defaults_to_give_feedback(router: DiagnosisRouter) -> None:
    assert router.parse_route("Route to: unknown-skill") == "give-feedback"
    assert router.parse_route("No route here") == "give-feedback"


@pytest.mark.asyncio
async def test_diagnosis_router_routes_to_check_structure() -> None:
    skills = {s.name: s for s in load_skills(SKILLS_DIR)}
    fake = FakeProvider(canned_responses=["Route to: check-structure", "coaching output"])
    executor = SkillExecutionService(provider=fake)
    router = DiagnosisRouter(executor=executor, skills=list(skills.values()))

    diagnosis, coaching, route = await router.coach({"student_text": "The text is interesting."})

    assert route == "check-structure"
    assert coaching == "coaching output"
    assert len(fake.calls) == 2
    assert "# diagnose-errors" in fake.calls[0][0]
    assert "# check-structure" in fake.calls[1][0]


@pytest.mark.asyncio
async def test_diagnosis_router_routes_persuasive_to_strengthen_argument() -> None:
    skills = {s.name: s for s in load_skills(SKILLS_DIR)}
    fake = FakeProvider(
        canned_responses=["Route to: strengthen-argument", "argument coaching output"]
    )
    executor = SkillExecutionService(provider=fake)
    router = DiagnosisRouter(executor=executor, skills=list(skills.values()))

    diagnosis, coaching, route = await router.coach(
        {
            "student_text": "Uniforms are unfair. Everyone knows they are uncomfortable.",
            "text_type": "persuasive",
            "year_level": "8",
        }
    )

    assert route == "strengthen-argument"
    assert coaching == "argument coaching output"
    assert len(fake.calls) == 2
    assert "# diagnose-errors" in fake.calls[0][0]
    assert "# strengthen-argument" in fake.calls[1][0]
    # The coaching prompt must carry the persuasive year-8 argument-chains pack.
    assert "argument-chains.md" in fake.calls[1][0]
    assert "Argument chains (Year 8 persuasive)" in fake.calls[1][0]

@pytest.mark.asyncio
async def test_diagnosis_router_routes_imaginative_to_craft_voice() -> None:
    skills = {s.name: s for s in load_skills(SKILLS_DIR)}
    fake = FakeProvider(
        canned_responses=["Route to: craft-voice", "voice coaching output"]
    )
    executor = SkillExecutionService(provider=fake)
    router = DiagnosisRouter(executor=executor, skills=list(skills.values()))

    diagnosis, coaching, route = await router.coach(
        {
            "student_text": "He was very scared. Then he heard a noise and he was terrified.",
            "text_type": "imaginative",
            "year_level": "8",
        }
    )

    assert route == "craft-voice"
    assert coaching == "voice coaching output"
    assert len(fake.calls) == 2
    assert "# diagnose-errors" in fake.calls[0][0]
    assert "# craft-voice" in fake.calls[1][0]
    # The coaching prompt must carry the imaginative year-8 voice-craft pack.
    assert "voice-craft.md" in fake.calls[1][0]
    assert "Voice craft (Year 8 imaginative)" in fake.calls[1][0]

@pytest.mark.asyncio
async def test_diagnosis_router_routes_mechanics_to_fix_mechanics() -> None:
    skills = {s.name: s for s in load_skills(SKILLS_DIR)}
    fake = FakeProvider(
        canned_responses=["Route to: fix-mechanics", "mechanics coaching output"]
    )
    executor = SkillExecutionService(provider=fake)
    router = DiagnosisRouter(executor=executor, skills=list(skills.values()))

    diagnosis, coaching, route = await router.coach(
        {
            "student_text": "The opening positions the reader, this is clear early. Its effective.",
            "text_type": "analytical",
            "year_level": "8",
        }
    )

    assert route == "fix-mechanics"
    assert coaching == "mechanics coaching output"
    assert len(fake.calls) == 2
    assert "# diagnose-errors" in fake.calls[0][0]
    # The diagnosis prompt must offer fix-mechanics as a valid route.
    assert "fix-mechanics" in fake.calls[0][0]
    assert "# fix-mechanics" in fake.calls[1][0]
    # The coaching prompt must carry the shared mechanics guide.
    assert "mechanics-guide.md" in fake.calls[1][0]
    assert "Mechanics guide (all text types, all bands)" in fake.calls[1][0]
    # Shared-only skills are combo-agnostic: no degradation note appended.
    assert "no dedicated references" not in coaching
