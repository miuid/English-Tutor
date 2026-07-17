"""Database engine and session management."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models import Base


@lru_cache
def get_engine() -> Engine:
    """Return the cached SQLAlchemy engine for the current DATABASE_URL."""
    url = get_settings().database_url
    engine = create_engine(url, connect_args={"check_same_thread": False})
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_conn: Any, connection_record: Any) -> None:
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def get_session_maker() -> sessionmaker[DBSession]:
    """Return a sessionmaker bound to the current engine."""
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def init_db() -> None:
    """Create all tables if they do not exist."""
    Base.metadata.create_all(bind=get_engine())
