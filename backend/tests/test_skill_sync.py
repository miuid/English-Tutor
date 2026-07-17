"""Tests for skill registry sync."""

from sqlalchemy import select
from sqlalchemy.orm import Session as SqlSession

from app.models import Skill
from app.skills.sync import sync_skills


def test_sync_skills_creates_all_rows(db_session: SqlSession) -> None:
    sync_skills(db_session)
    skills = db_session.execute(select(Skill)).scalars().all()
    assert len(skills) == 8
    names = {s.name for s in skills}
    assert "check-structure" in names
    assert "elevate-vocabulary" in names
    assert "give-feedback" in names


def test_sync_skills_is_idempotent(db_session: SqlSession) -> None:
    sync_skills(db_session)
    first = db_session.execute(select(Skill)).scalars().all()
    sync_skills(db_session)
    second = db_session.execute(select(Skill)).scalars().all()
    assert len(first) == len(second) == 8
