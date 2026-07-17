"""Session orchestrator that runs the daily teaching loop end to end."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.models import Attempt, Feedback, RubricScore, Session, Student
from app.models import Skill as SkillRow
from app.skills.executor import SkillExecutionService
from app.skills.loader import Skill
from app.skills.router import DiagnosisRouter
from app.skills.rubric_parser import parse_rubric_levels


class SessionOrchestrator:
    """Run the daily loop stages and persist a Session with its Attempts."""

    def __init__(self, db: DBSession, executor: SkillExecutionService, skills: dict[str, Skill]):
        self.db = db
        self.executor = executor
        self.skills = skills
        self.router = DiagnosisRouter(executor=executor, skills=list(skills.values()))

    async def run_daily_loop(
        self,
        student_id: uuid.UUID,
        year_level: str,
        text_type: str,
        task_prompt: str,
        student_text: str,
    ) -> Session:
        """Run all daily-loop stages and return the persisted Session."""
        student = self.db.get(Student, student_id)
        if not student:
            raise ValueError(f"Student not found: {student_id}")

        db_session = Session(student_id=student_id, learning_intention=task_prompt)
        self.db.add(db_session)
        self.db.flush()

        base_inputs = {
            "year_level": year_level,
            "text_type": text_type,
            "task_prompt": task_prompt,
            "student_text": "",
        }

        # Stage 1: set success criteria
        criteria = await self.executor.execute(self.skills["set-success-criteria"], base_inputs)
        self._save_attempt(
            db_session.id,
            student_id,
            "set-success-criteria",
            "criteria",
            "start",
            task_prompt,
            criteria,
        )

        # Stage 2: model response (I do)
        model = await self.executor.execute(self.skills["model-response"], base_inputs)
        self._save_attempt(
            db_session.id, student_id, "model-response", "model", "I do", task_prompt, model
        )

        # Stage 3: guided practice (we do)
        guided = await self.executor.execute(self.skills["guided-practice"], base_inputs)
        self._save_attempt(
            db_session.id, student_id, "guided-practice", "guided", "we do", task_prompt, guided
        )

        # Stage 4: independent task (you do)
        task_for_student = await self.executor.execute(self.skills["independent-task"], base_inputs)
        self._save_attempt(
            db_session.id,
            student_id,
            "independent-task",
            "independent",
            "you do",
            task_prompt,
            task_for_student,
        )

        # Stage 5+6: diagnose -> coach
        coach_inputs = {
            "year_level": year_level,
            "text_type": text_type,
            "task_prompt": task_for_student,
            "student_text": student_text,
        }
        diagnosis, coaching, route = await self.router.coach(coach_inputs)
        self._save_attempt(
            db_session.id,
            student_id,
            "diagnose-errors",
            "diagnosis",
            "triage",
            task_for_student,
            diagnosis,
        )
        self._save_attempt(
            db_session.id, student_id, route, "coach", "coach", task_for_student, coaching
        )

        # Stage 7: give feedback
        feedback_output = await self.executor.execute(self.skills["give-feedback"], coach_inputs)
        final_attempt = self._save_attempt(
            db_session.id,
            student_id,
            "give-feedback",
            "feedback",
            "end",
            task_for_student,
            feedback_output,
        )

        feedback = Feedback(
            attempt_id=final_attempt.id,
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
        db_session.ended_at = datetime.now(UTC)
        self.db.commit()
        return db_session

    def _save_attempt(
        self,
        session_id: uuid.UUID,
        student_id: uuid.UUID,
        skill_name: str,
        task_type: str,
        mode: str,
        task_prompt: str,
        student_text: str,
    ) -> Attempt:
        skill_row = self.db.execute(
            select(SkillRow).where(SkillRow.name == skill_name)
        ).scalar_one()
        attempt = Attempt(
            session_id=session_id,
            student_id=student_id,
            skill_id=skill_row.id,
            task_type=task_type,
            mode=mode,
            task_prompt=task_prompt,
            student_text=student_text,
        )
        self.db.add(attempt)
        self.db.flush()
        return attempt
