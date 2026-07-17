"""Shared pytest fixtures for the backend test suite."""

import os
import tempfile
from collections.abc import Generator

import pytest
from sqlalchemy.orm import Session as SqlSession
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.database import get_engine, init_db


@pytest.fixture
def db_session(monkeypatch: pytest.MonkeyPatch) -> Generator[SqlSession, None, None]:
    """Yield a fresh database session backed by a temporary SQLite database."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    url = f"sqlite:///{path}"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("LLM_PROVIDER", "fake")
    monkeypatch.setenv("LLM_API_KEY", "")
    get_settings.cache_clear()
    get_engine.cache_clear()
    engine = get_engine()
    init_db()
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()
        os.unlink(path)
