"""Interactive daily-loop service: a stage machine over the tutor stages.

Stages reuse the GRR loop-stage vocabulary from ``app.skills.loader.LOOP_STAGES``:
``start`` -> ``I do`` -> ``we do`` -> ``you do`` -> ``ended``. The current stage
is persisted on the Session row so any client can resume after a reload.

Turn persistence mirrors the scripted SessionOrchestrator: every loop turn is an
Attempt row. Tutor turns carry the skill output in ``Attempt.student_text``
(existing convention); student submissions use ``skill_id=None`` and
``task_type="submission"`` with the student's own text.
"""

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models import (
    Attempt,
    Feedback,
    InteractionLog,
    RubricScore,
    Session,
    Student,
)
from app.models import Skill as SkillRow
from app.skills.executor import SkillExecutionService
from app.skills.loader import Skill
from app.skills.router import DiagnosisRouter
from app.skills.rubric_parser import parse_rubric_levels

# advance() transitions: current stage -> (skill to run, Attempt task_type, next stage).
ADVANCE_TRANSITIONS: dict[str, tuple[str, str, str]] = {
    "start": ("model-response", "model", "I do"),
    "I do": ("guided-practice", "guided", "we do"),
    "we do": ("independent-task", "independent", "you do"),
}
SUBMIT_STAGES = ("we do", "you do")
ENDED = "ended"
DEFAULT_TEXT_TYPE = "analytical"  # MVP scope: Year 8 analytical only
DEFAULT_CURRICULUM = "QCAA"
# Used when the student starts a session without pasting a school task.
DEFAULT_TASK_PROMPT = "General analytical writing practice"

# Soft daily time budget: gaps between interactions longer than this count as
# the cap (a student who walks away without pausing is not punished, while
# ordinary reading/writing gaps still count), and the counter resets when the
# activity date rolls over, so an unfinished session simply continues the next
# day with a fresh budget.
IDLE_CAP_SECONDS = 10 * 60
DEFAULT_TIME_LIMIT_SECONDS = 15 * 60

# What tomorrow holds, per stage where the session wrapped up.
WRAP_UP_NEXT_STEP = {
    "start": "tomorrow we'll watch how a strong response is put together",
    "I do": "tomorrow we'll practise together, side by side",
    "we do": "tomorrow it'll be your turn to write your own piece",
}
WRAP_UP_FALLBACK = "tomorrow we'll pick up right where we left off"


class SessionNotFoundError(Exception):
    """Raised when a session id does not exist."""


class StageConflictError(Exception):
    """Raised when advance/submit is called in the wrong stage."""


@dataclass(frozen=True)
class AdvanceResult:
    """What an advance() call produced: the tutor turn and the time-up flag."""

    turn: Attempt
    time_up: bool = False


@dataclass(frozen=True)
class SubmitResult:
    """What a submit() call persisted, in creation order."""

    submission: Attempt
    tutor_turns: list[Attempt]
    feedback: Feedback | None
    time_up: bool = False


class InteractiveLoop:
    """Drive one Session through the daily loop one interactive step at a time.

    ``now`` is injectable so tests can control the clock; the time limit is a
    soft daily budget (see module constants).
    """

    def __init__(
        self,
        db: DBSession,
        executor: SkillExecutionService,
        skills: dict[str, Skill],
        *,
        time_limit_seconds: int = DEFAULT_TIME_LIMIT_SECONDS,
        now: Callable[[], datetime] | None = None,
    ):
        self.db = db
        self.executor = executor
        self.skills = skills
        self.router = DiagnosisRouter(executor=executor, skills=list(skills.values()))
        self.time_limit_seconds = time_limit_seconds
        self._now = now or (lambda: datetime.now(UTC))

    async def start(
        self,
        *,
        task_prompt: str | None,
        year_level: str,
        text_type: str,
        context: str | None = None,
        student_id: uuid.UUID | None = None,
    ) -> Session:
        """Create/fetch the student, open a Session, and run set-success-criteria.

        ``task_prompt`` is optional: when absent the loop falls back to
        ``DEFAULT_TASK_PROMPT`` so the skills still get a usable prompt, while
        ``Session.learning_intention`` stays ``None`` (no pasted school task).

        When ``student_id`` is provided, the session attaches to that profile
        and ``year_level`` / ``text_type`` inherit from the student's profile
        (the request's values are ignored). Otherwise the legacy single-user
        student is used (created on first call).
        """
        student = self._resolve_student(
            student_id=student_id,
            year_level=year_level,
        )
        session = Session(
            student_id=student.id,
            learning_intention=task_prompt,
            stage="start",
            last_activity_at=self._now(),
        )
        self.db.add(session)
        self.db.flush()

        resolved_text_type = self._resolve_text_type(student, text_type)
        resolved_year_level = str(student.year_level)

        criteria = await self._execute_and_log(
            session,
            self.skills["set-success-criteria"],
            {
                "year_level": resolved_year_level,
                "text_type": resolved_text_type,
                "task_prompt": task_prompt or DEFAULT_TASK_PROMPT,
                "context": context or "",
                "student_text": "",
            },
        )
        self._save_tutor_turn(
            session,
            "set-success-criteria",
            "criteria",
            "start",
            task_prompt or DEFAULT_TASK_PROMPT,
            criteria,
        )
        self.db.commit()
        return session

    def get_session(self, session_id: uuid.UUID) -> Session:
        """Fetch a session or raise SessionNotFoundError."""
        session = self.db.get(Session, session_id)
        if session is None:
            msg = f"Session not found: {session_id}"
            raise SessionNotFoundError(msg)
        return session

    def get_state(self, session_id: uuid.UUID) -> tuple[Session, list[Attempt]]:
        """Return the session and all its turns in creation order."""
        session = self.get_session(session_id)
        attempts = (
            self.db.execute(
                select(Attempt)
                .where(Attempt.session_id == session.id)
                .order_by(Attempt.created_at)
            )
            .scalars()
            .all()
        )
        return session, list(attempts)

    async def advance(self, session_id: uuid.UUID) -> AdvanceResult:
        """Run the next tutor stage (model -> guided -> independent).

        If the daily time budget is spent, no new stage is started: the loop
        persists a wrap-up turn and auto-pauses the session instead.
        """
        session = self.get_session(session_id)
        self._ensure_running(session)
        transition = ADVANCE_TRANSITIONS.get(session.stage)
        if transition is None:
            msg = f"Stage '{session.stage}' expects a student submission, not advance"
            raise StageConflictError(msg)
        skill_name, task_type, next_stage = transition

        self._touch(session)
        if self._time_up(session):
            turn = self._wrap_up(session)
            self.db.commit()
            return AdvanceResult(turn=turn, time_up=True)

        output = await self._execute_and_log(
            session,
            self.skills[skill_name],
            self._base_inputs(session),
        )
        turn = self._save_tutor_turn(
            session, skill_name, task_type, next_stage, self._task_prompt(session), output
        )
        session.stage = next_stage
        self.db.commit()
        return AdvanceResult(turn=turn, time_up=False)

    async def submit(self, session_id: uuid.UUID, text: str) -> SubmitResult:
        """Persist a student submission; at 'you do' also run the feedback pipeline.

        The current unit of work always finishes even when time is up: a
        'we do' exchange completes and then wraps up; a 'you do' submission
        always receives the full feedback pipeline and ends the session.
        """
        session = self.get_session(session_id)
        self._ensure_running(session)
        if session.stage not in SUBMIT_STAGES:
            msg = f"Stage '{session.stage}' does not accept a student submission"
            raise StageConflictError(msg)
        self._touch(session)

        submission = Attempt(
            session_id=session.id,
            student_id=session.student_id,
            skill_id=None,
            task_type="submission",
            mode=session.stage,
            task_prompt=self._task_prompt(session),
            student_text=text,
        )
        self.db.add(submission)
        self.db.flush()

        if session.stage == "we do":
            follow_up = await self._execute_and_log(
                session,
                self.skills["guided-practice"],
                self._base_inputs(session, student_text=text),
            )
            turn = self._save_tutor_turn(
                session, "guided-practice", "guided", "we do", self._task_prompt(session), follow_up
            )
            if not self._time_up(session):
                self.db.commit()
                return SubmitResult(submission=submission, tutor_turns=[turn], feedback=None)
            wrap_turn = self._wrap_up(session)
            self.db.commit()
            return SubmitResult(
                submission=submission,
                tutor_turns=[turn, wrap_turn],
                feedback=None,
                time_up=True,
            )

        # "you do": diagnose -> route -> coach -> give-feedback, then end the session.
        task_for_student = self._latest_independent_task(session)
        coach_inputs = self._base_inputs(
            session, task_prompt=task_for_student, student_text=text
        )
        diagnosis = await self._execute_and_log(
            session, self.skills["diagnose-errors"], coach_inputs
        )
        route = self.router.parse_route(diagnosis)
        coaching = await self._execute_and_log(
            session, self.skills[route], coach_inputs
        )
        diagnosis_turn = self._save_tutor_turn(
            session, "diagnose-errors", "diagnosis", "triage", task_for_student, diagnosis
        )
        coach_turn = self._save_tutor_turn(
            session, route, "coach", "coach", task_for_student, coaching
        )
        feedback_output = await self._execute_and_log(
            session, self.skills["give-feedback"], coach_inputs
        )
        feedback_turn = self._save_tutor_turn(
            session, "give-feedback", "feedback", "end", task_for_student, feedback_output
        )

        feedback = Feedback(
            attempt_id=feedback_turn.id,
            strength="see feedback output",
            next_steps="see feedback output",
        )
        for parsed in parse_rubric_levels(feedback_output):
            feedback.rubric_scores.append(
                RubricScore(
                    criterion_name=parsed.criterion_name,
                    level=parsed.level,
                    note=parsed.note,
                )
            )
        self.db.add(feedback)
        session.stage = ENDED
        session.ended_at = self._now()
        self.db.commit()
        return SubmitResult(
            submission=submission,
            tutor_turns=[diagnosis_turn, coach_turn, feedback_turn],
            feedback=feedback,
            time_up=self._time_up(session),
        )

    def pause(self, session_id: uuid.UUID) -> Session:
        """Pause a running session; paused time is never counted."""
        session = self.get_session(session_id)
        if session.stage == ENDED or session.ended_at is not None:
            msg = "Session has already ended"
            raise StageConflictError(msg)
        if session.paused_at is None:
            session.paused_at = self._now()
            self.db.commit()
        return session

    def resume(self, session_id: uuid.UUID) -> Session:
        """Resume a paused session; a new day restores the full time budget."""
        session = self.get_session(session_id)
        if session.stage == ENDED or session.ended_at is not None:
            msg = "Session has already ended"
            raise StageConflictError(msg)
        now = self._now()
        last = self._as_aware(session.last_activity_at)
        if last is not None and self._local_date(last) != self._local_date(now):
            session.time_spent_seconds = 0
        session.paused_at = None
        session.last_activity_at = now
        self.db.commit()
        return session

    def time_state(self, session: Session) -> tuple[int, bool]:
        """Effective (seconds spent today, time-up flag) for display purposes."""
        spent = session.time_spent_seconds
        last = self._as_aware(session.last_activity_at)
        if last is not None and self._local_date(last) != self._local_date(self._now()):
            spent = 0  # new day, not yet persisted — the next _touch() resets it
        return spent, spent >= self.time_limit_seconds

    def _ensure_running(self, session: Session) -> None:
        if session.stage == ENDED or session.ended_at is not None:
            msg = "Session has already ended"
            raise StageConflictError(msg)
        if session.paused_at is not None:
            msg = "Session is paused — resume it to continue"
            raise StageConflictError(msg)

    def _touch(self, session: Session) -> None:
        """Accumulate active time since the last interaction onto today's budget."""
        now = self._now()
        last = self._as_aware(session.last_activity_at)
        if last is None:
            session.last_activity_at = now
            return
        if self._local_date(last) != self._local_date(now):
            session.time_spent_seconds = 0  # day rolled over: fresh budget
        else:
            gap = max((now - last).total_seconds(), 0.0)
            session.time_spent_seconds += int(min(gap, IDLE_CAP_SECONDS))
        session.last_activity_at = now

    def _time_up(self, session: Session) -> bool:
        return session.time_spent_seconds >= self.time_limit_seconds

    def _wrap_up(self, session: Session) -> Attempt:
        """Persist a time-up wrap-up tutor turn and auto-pause the session.

        Idempotent per pause: if the latest turn is already a wrap-up it is
        returned as-is rather than duplicated.
        """
        latest = self.db.execute(
            select(Attempt)
            .where(Attempt.session_id == session.id)
            .order_by(Attempt.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()
        if latest is not None and latest.task_type == "wrap-up":
            turn = latest
        else:
            turn = Attempt(
                session_id=session.id,
                student_id=session.student_id,
                skill_id=None,
                task_type="wrap-up",
                mode="wrap-up",
                task_prompt=self._task_prompt(session),
                student_text=self._wrap_up_message(session),
            )
            self.db.add(turn)
            self.db.flush()
        session.paused_at = self._now()
        return turn

    def _wrap_up_message(self, session: Session) -> str:
        minutes = max(self.time_limit_seconds // 60, 1)
        plural = "s" if minutes != 1 else ""
        next_step = WRAP_UP_NEXT_STEP.get(session.stage, WRAP_UP_FALLBACK)
        return (
            f"⏰ **That's our {minutes} minute{plural} for today — nice work!**\n\n"
            f"Don't worry about finishing now: {next_step}. "
            "Your place is saved, so come back tomorrow and we'll pick up "
            "right where we left off."
        )

    @staticmethod
    def _as_aware(value: datetime | None) -> datetime | None:
        """SQLite returns naive datetimes; treat them as UTC."""
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value

    @staticmethod
    def _local_date(value: datetime) -> date:
        """The server's local calendar date — 'tomorrow' for the student."""
        return value.astimezone().date()

    async def _execute_and_log(
        self,
        session: Session,
        skill: Skill,
        inputs: dict[str, str],
    ) -> str:
        "Run a skill and persist an InteractionLog row."
        output = await self.executor.execute(skill, inputs)
        self._log_interaction(session, skill, inputs, output)
        return output

    def _log_interaction(
        self,
        session: Session,
        skill: Skill,
        inputs: dict[str, str],
        output: str,
    ) -> None:
        "Write one InteractionLog row (best-effort; never blocks the turn)."
        try:
            skill_row = self.db.execute(
                select(SkillRow).where(SkillRow.name == skill.name)
            ).scalar_one_or_none()
            self.db.add(
                InteractionLog(
                    session_id=session.id,
                    skill_id=skill_row.id if skill_row is not None else None,
                    model=self.executor.model_name,
                    input=inputs.get("student_text", ""),
                    output=output,
                )
            )
        except Exception:
            pass

    def _resolve_student(
        self,
        *,
        student_id: uuid.UUID | None,
        year_level: str,
    ) -> Student:
        """Resolve the session's student.

        - ``student_id`` provided: use that profile (raises if missing).
        - Otherwise: single-user MVP — reuse the first student, else create a
          default one with ``year_level`` and the default curriculum.
        """
        if student_id is not None:
            student = self.db.get(Student, student_id)
            if student is None:
                msg = f"Student not found: {student_id}"
                raise SessionNotFoundError(msg)
            return student
        return self._get_or_create_student(year_level)

    @staticmethod
    def _resolve_text_type(student: Student, requested: str) -> str:
        """Pick the text type for the session from the student profile or request.

        If the student's ``focus_text_types`` is non-empty, the first entry is
        used (the request's ``text_type`` is ignored — the profile wins).
        Otherwise the request's ``text_type`` is used (MVP default).
        """
        focus = student.focus_text_types or []
        if focus:
            return focus[0]
        return requested

    def _get_or_create_student(self, year_level: str) -> Student:
        """Single-user MVP: reuse the first student, else create a default one."""
        student = self.db.execute(
            select(Student).order_by(Student.created_at).limit(1)
        ).scalar_one_or_none()
        if student is not None:
            return student
        try:
            parsed_year = int(year_level)
        except ValueError:
            parsed_year = 8
        student = Student(name="Student", year_level=parsed_year, curriculum=DEFAULT_CURRICULUM)
        self.db.add(student)
        self.db.flush()
        return student

    def _base_inputs(
        self,
        session: Session,
        *,
        task_prompt: str | None = None,
        student_text: str = "",
    ) -> dict[str, str]:
        """Rebuild skill inputs for an existing session.

        year_level and text_type come from the student row when the student has
        a profile (year_level always; focus_text_types[0] when non-empty), so
        sessions stay consistent with the student's profile across reloads.
        """
        student = self.db.get(Student, session.student_id)
        if student is not None:
            year_level = str(student.year_level)
            text_type = self._resolve_text_type(student, DEFAULT_TEXT_TYPE)
        else:
            year_level = "8"
            text_type = DEFAULT_TEXT_TYPE
        return {
            "year_level": year_level,
            "text_type": text_type,
            "task_prompt": task_prompt if task_prompt is not None else self._task_prompt(session),
            "student_text": student_text,
        }

    def _task_prompt(self, session: Session) -> str:
        return session.learning_intention or DEFAULT_TASK_PROMPT

    def _latest_independent_task(self, session: Session) -> str:
        """The independent-task tutor output is the prompt the student answered."""
        turn = self.db.execute(
            select(Attempt)
            .where(Attempt.session_id == session.id, Attempt.task_type == "independent")
            .order_by(Attempt.created_at.desc())
            .limit(1)
        ).scalar_one_or_none()
        if turn is not None:
            return turn.student_text
        return self._task_prompt(session)

    def _save_tutor_turn(
        self,
        session: Session,
        skill_name: str,
        task_type: str,
        mode: str,
        task_prompt: str,
        output: str,
    ) -> Attempt:
        """Persist a tutor turn as an Attempt (output in student_text, per convention)."""
        skill_row = self.db.execute(
            select(SkillRow).where(SkillRow.name == skill_name)
        ).scalar_one()
        attempt = Attempt(
            session_id=session.id,
            student_id=session.student_id,
            skill_id=skill_row.id,
            task_type=task_type,
            mode=mode,
            task_prompt=task_prompt,
            student_text=output,
        )
        self.db.add(attempt)
        self.db.flush()
        return attempt
