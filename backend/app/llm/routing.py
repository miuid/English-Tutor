"""Config-driven per-stage model routing (ISS-021).

Heavy judgement stages (triage/coach/end/baseline) can be pointed at a
stronger model and light stages (retrieval/start/I do/we do/you do) at a
cheaper tier, purely through config — business logic stays provider-agnostic
and skill contracts never change.
"""

from app.config import Settings
from app.llm.factory import create_llm_provider
from app.llm.provider import LLMProvider


class StageProviderRouter:
    """Resolve and cache the (provider, model name) pair for each loop stage.

    The routing table is ``Settings.llm_stage_models``: loop_stage -> model
    name override. Stages without an entry use the default provider/model.
    Routing stays within the configured provider family (one API key) — only
    the model tier changes per stage.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._cache: dict[str, tuple[LLMProvider, str]] = {}

    def for_stage(self, loop_stage: str) -> tuple[LLMProvider, str]:
        """Return the (provider, model name) pair for a loop stage."""
        if loop_stage not in self._cache:
            model = self._settings.llm_stage_models.get(
                loop_stage, self._settings.llm_model
            )
            stage_settings = self._settings.model_copy(update={"llm_model": model})
            self._cache[loop_stage] = (create_llm_provider(stage_settings), model)
        return self._cache[loop_stage]
