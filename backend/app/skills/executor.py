"""Execute a skill by composing its instructions + references into a prompt."""

from dataclasses import dataclass

from app.llm.provider import LLMProvider
from app.skills.loader import Skill


@dataclass
class SkillExecutionService:
    """Run a skill's instructions against the configured LLM provider."""

    provider: LLMProvider

    async def execute(self, skill: Skill, inputs: dict[str, str]) -> str:
        """Compose and send the skill prompt, returning the LLM response."""
        system_prompt = self._build_system_prompt(skill)
        user_message = self._build_user_message(inputs)
        messages = [{"role": "user", "content": user_message}]
        return await self.provider.generate(system_prompt, messages)

    def _build_system_prompt(self, skill: Skill) -> str:
        parts = [skill.instructions]
        if skill.references:
            parts.append("\n\n--- Reference material ---")
            for name, content in skill.references.items():
                parts.append(f"\n\n### {name}\n\n{content}")
        return "".join(parts)

    def _build_user_message(self, inputs: dict[str, str]) -> str:
        ordered_keys = ["year_level", "text_type", "task_prompt", "context", "mode", "student_text"]
        lines: list[str] = []
        remaining = set(inputs.keys())

        for key in ordered_keys:
            if key in inputs:
                value = inputs[key]
                remaining.remove(key)
                if key == "student_text":
                    lines.append(f"\n{key}:\n---\n{value}\n---")
                else:
                    lines.append(f"{key}: {value}")

        for key in sorted(remaining):
            lines.append(f"{key}: {inputs[key]}")

        return "\n".join(lines)
