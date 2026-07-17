"""Route from diagnose-errors to the recommended coaching skill."""

import re

from app.skills.executor import SkillExecutionService
from app.skills.loader import Skill

DEFAULT_ROUTE = "give-feedback"


class DiagnosisRouter:
    """Run diagnose-errors and dispatch to the recommended coaching skill."""

    def __init__(self, executor: SkillExecutionService, skills: list[Skill]):
        self.executor = executor
        self.skills = {skill.name: skill for skill in skills}

    async def diagnose(self, inputs: dict[str, str]) -> str:
        """Run the diagnose-errors skill and return its raw output."""
        return await self.executor.execute(self.skills["diagnose-errors"], inputs)

    def parse_route(self, diagnosis: str) -> str:
        """Extract the recommended downstream skill from the diagnosis."""
        match = re.search(
            r"^\s*Route to:\s*([a-z0-9\-]+)",
            diagnosis,
            re.IGNORECASE | re.MULTILINE,
        )
        if not match:
            return DEFAULT_ROUTE
        route = match.group(1).strip().lower()
        return route if route in self.skills else DEFAULT_ROUTE

    async def coach(self, inputs: dict[str, str]) -> tuple[str, str, str]:
        """Diagnose, route, and execute the recommended coaching skill.

        Returns (diagnosis, coaching_output, route).
        """
        diagnosis = await self.diagnose(inputs)
        route = self.parse_route(diagnosis)
        coaching = await self.executor.execute(self.skills[route], inputs)
        return diagnosis, coaching, route
