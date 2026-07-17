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
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models import Attempt, Feedback, RubricScore, Session, Student
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


class SessionNotFoundError(Exception):
    """Raised when a session id does not exist."""


class StageConflictError(Exception):
    """Raised when advance/submit is called in the wrong stage."""


@dataclass(frozen=True)
class SubmitResult:
    """What a submit() call persisted, in creation order."""

    submission: Attempt
    tutor_turns: list[Attempt]
    feedback: Feedback | None


class InteractiveLoop:
    """Drive one Session through the daily loop one interactive step at a time."""

    def __init__(self, db: DBSession, executor: SkillExecutionService, skills: dict[str, Skill]):
        self.db = db
        self.executor = executor
        self.skills = skills
        self.router = DiagnosisRouter(executor=executor, skills=list(skills.values()))

    async def start(
        self,
        *,
        task_prompt: str | None,
        year_level: str,
        text_type: str,
        context: str | None = None,
    ) -> Session:
        """Create/fetch the student, open a Session, and run set-success-criteria.

        ``task_prompt`` is optional: when absent the loop falls back to
        ``DEFAULT_TASK_PROMPT`` so the skills still get a usable prompt, while
        ``Session.learning_intention`` stays ``None`` (no pasted school task).
        """
        student = self._get_or_create_student(year_level)
        session = Session(
            student_id=student.id,
            learning_intention=task_prompt,
            stage="start",
        )
        self.db.add(session)
        self.db.flush()

        criteria = await self.executor.execute(
            self.skills["set-success-criteria"],
            {
                "year_level": year_level,
                "text_type": text_type,
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

    async def advance(self, session_id: uuid.UUID) -> Attempt:
        """Run the next tutor stage (model -> guided -> independent)."""
        session = self.get_session(session_id)
        if session.stage == ENDED:
            msg = "Session has already ended"
            raise StageConflictError(msg)
        transition = ADVANCE_TRANSITIONS.get(session.stage)
        if transition is None:
            msg = f"Stage '{session.stage}' expects a student submission, not advance"
            raise StageConflictError(msg)
        skill_name, task_type, next_stage = transition

        output = await self.executor.execute(
            self.skills[skill_name],
            self._base_inputs(session),
        )
        turn = self._save_tutor_turn(
            session, skill_name, task_type, next_stage, self._task_prompt(session), output
        )
        session.stage = next_stage
        self.db.commit()
        return turn

    async def submit(self, session_id: uuid.UUID, text: str) -> SubmitResult:
        """Persist a student submission; at 'you do' also run the feedback pipeline."""
        session = self.get_session(session_id)
        if session.stage not in SUBMIT_STAGES:
            msg = f"Stage '{session.stage}' does not accept a student submission"
            raise StageConflictError(msg)

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
            follow_up = await self.executor.execute(
                self.skills["guided-practice"],
                self._base_inputs(session, student_text=text),
            )
            turn = self._save_tutor_turn(
                session, "guided-practice", "guided", "we do", self._task_prompt(session), follow_up
            )
            self.db.commit()
            return SubmitResult(submission=submission, tutor_turns=[turn], feedback=None)

        # "you do": diagnose -> route -> coach -> give-feedback, then end the session.
        task_for_student = self._latest_independent_task(session)
        coach_inputs = self._base_inputs(
            session, task_prompt=task_for_student, student_text=text
        )
        diagnosis, coaching, route = await self.router.coach(coach_inputs)
        diagnosis_turn = self._save_tutor_turn(
            session, "diagnose-errors", "diagnosis", "triage", task_for_student, diagnosis
        )
        coach_turn = self._save_tutor_turn(
            session, route, "coach", "coach", task_for_student, coaching
        )
        feedback_output = await self.executor.execute(self.skills["give-feedback"], coach_inputs)
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
        session.ended_at = datetime.now(UTC)
        self.db.commit()
        return SubmitResult(
            submission=submission,
            tutor_turns=[diagnosis_turn, coach_turn, feedback_turn],
            feedback=feedback,
        )

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

        year_level comes from the student row; text_type is fixed to the MVP
        analytical scope (Session does not store it).
        """
        student = self.db.get(Student, session.student_id)
        year_level = str(student.year_level) if student is not None else "8"
        return {
            "year_level": year_level,
            "text_type": DEFAULT_TEXT_TYPE,
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
