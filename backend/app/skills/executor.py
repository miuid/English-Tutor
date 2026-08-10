"""Execute a skill by composing its instructions + references into a prompt."""

from dataclasses import dataclass

from app.llm.provider import LLMProvider
from app.skills.loader import Skill

DEFAULT_TEXT_TYPE = "analytical"
DEFAULT_YEAR_BAND = "year-8"
# Nearest-band fallback order when no exact pack exists for a text type.
BAND_FALLBACK_ORDER = ("year-8", "year-9-10", "year-11-12")


def year_band_for(year_level: str | None) -> str:
    """Map a year_level input to its band; unparseable/missing -> year-8."""
    try:
        year = int(str(year_level).strip())
    except (TypeError, ValueError):
        return DEFAULT_YEAR_BAND
    if year <= 8:
        return "year-8"
    if year <= 10:
        return "year-9-10"
    return "year-11-12"


def select_packs(
    skill: Skill, text_type: str, year_band: str
) -> tuple[list[dict[str, str]], str | None]:
    """Pick the reference packs for a (text_type, year_band) combo.

    Returns (ordered packs to include, pack key actually used for the combo).
    The shared pack comes first; then the exact "<text_type>/<year_band>" pack,
    or the same text type's nearest band (BAND_FALLBACK_ORDER). The second
    element is None when no pack exists for the text type at all.
    """
    packs: list[dict[str, str]] = []
    shared = skill.packs.get("shared")
    if shared:
        packs.append(shared)
    exact_key = f"{text_type}/{year_band}"
    if exact_key in skill.packs:
        packs.append(skill.packs[exact_key])
        return packs, exact_key
    for band in BAND_FALLBACK_ORDER:
        key = f"{text_type}/{band}"
        if key in skill.packs:
            packs.append(skill.packs[key])
            return packs, key
    return packs, None


@dataclass
class SkillExecutionService:
    """Run a skill's instructions against the configured LLM provider."""

    provider: LLMProvider
    model_name: str = "unknown"

    async def execute(self, skill: Skill, inputs: dict[str, str]) -> str:
        """Compose and send the skill prompt, returning the LLM response."""
        text_type = (inputs.get("text_type") or "").strip().lower() or DEFAULT_TEXT_TYPE
        year_band = year_band_for(inputs.get("year_level"))
        packs, used_key = select_packs(skill, text_type, year_band)

        system_prompt = self._build_system_prompt(skill, packs)
        user_message = self._build_user_message(inputs)
        messages = [{"role": "user", "content": user_message}]
        response = await self.provider.generate(system_prompt, messages)

        note = self._degradation_note(skill, text_type, year_band, used_key)
        if note is not None:
            response = f"{response}\n\n{note}"
        return response

    def _build_system_prompt(self, skill: Skill, packs: list[dict[str, str]]) -> str:
        parts = [skill.instructions]
        if packs:
            parts.append("\n\n--- Reference material ---")
            for pack in packs:
                for name, content in pack.items():
                    parts.append(f"\n\n### {name}\n\n{content}")
        return "".join(parts)

    def _degradation_note(
        self, skill: Skill, text_type: str, year_band: str, used_key: str | None
    ) -> str | None:
        """Note appended when no exact pack exists for the combo (None if exact/none)."""
        exact_key = f"{text_type}/{year_band}"
        if not skill.packs or exact_key in skill.packs:
            return None
        if used_key is not None:
            if "shared" in skill.packs:
                used = f"shared references and the {used_key} pack"
            else:
                used = f"the {used_key} pack"
        elif "shared" in skill.packs:
            used = "shared references only"
        else:
            used = "skill instructions only"
        return f"_Note: no dedicated references for {text_type}/{year_band}; coached from {used}._"

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
