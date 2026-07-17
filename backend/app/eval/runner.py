"""Run eval cases: execute the skill, apply rule checks, run the LLM judge."""

from dataclasses import dataclass, field

from app.eval.fixtures import EvalCase
from app.eval.judge import JudgeParseError, JudgeResult, judge_output
from app.eval.rules import RuleContext, RuleResult, checks_for
from app.llm.provider import LLMProvider
from app.skills.executor import SkillExecutionService

PASS = "PASS"
FAIL = "FAIL"
ERROR = "ERROR"


@dataclass(frozen=True)
class CaseResult:
    """Outcome of running one eval case."""

    skill_name: str
    example: str
    output: str = ""
    rule_results: list[RuleResult] = field(default_factory=list)
    judge_result: JudgeResult | None = None
    judge_error: str | None = None
    error: str | None = None

    @property
    def rules_passed(self) -> bool:
        return all(result.passed for result in self.rule_results)

    @property
    def status(self) -> str:
        """PASS | FAIL | ERROR (judge/execution errors are never passes)."""
        if self.error or self.judge_error:
            return ERROR
        if not self.rules_passed:
            return FAIL
        if self.judge_result is not None and self.judge_result.verdict != PASS:
            return FAIL
        return PASS


async def run_case(
    case: EvalCase,
    executor: SkillExecutionService,
    provider: LLMProvider,
    context: RuleContext,
    *,
    judge: bool = True,
) -> CaseResult:
    """Execute one case end to end; errors are captured, never raised."""
    try:
        output = await executor.execute(case.skill, case.inputs)
    except Exception as exc:  # an errored case must not stop the run
        return CaseResult(
            skill_name=case.skill.name,
            example=case.example,
            error=f"{type(exc).__name__}: {exc}",
        )

    rule_results = [check(output, context) for check in checks_for(case.skill.name)]

    judge_result: JudgeResult | None = None
    judge_error: str | None = None
    if judge:
        try:
            judge_result = await judge_output(
                provider,
                skill_name=case.skill.name,
                sample=case.sample,
                expected=case.expected,
                output=output,
            )
        except JudgeParseError as exc:
            judge_error = f"unparseable judge output: {exc}"
        except Exception as exc:  # judge infra errors are not case failures
            judge_error = f"{type(exc).__name__}: {exc}"

    return CaseResult(
        skill_name=case.skill.name,
        example=case.example,
        output=output,
        rule_results=rule_results,
        judge_result=judge_result,
        judge_error=judge_error,
    )


async def run_cases(
    cases: list[EvalCase],
    executor: SkillExecutionService,
    provider: LLMProvider,
    *,
    judge: bool = True,
) -> list[CaseResult]:
    """Run cases sequentially (few fixtures; keeps provider logs ordered)."""
    context = RuleContext(skill_names=tuple(case.skill.name for case in cases))
    results: list[CaseResult] = []
    for case in cases:
        results.append(await run_case(case, executor, provider, context, judge=judge))
    return results
