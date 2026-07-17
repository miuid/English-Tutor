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
