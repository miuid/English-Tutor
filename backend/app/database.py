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
    """Create all tables if they do not exist, then patch older SQLite DBs.

    The project has no migration framework; new nullable/defaulted columns on
    ``session`` are added in place so existing dev and LAN-server databases
    keep their data.
    """
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    _ensure_session_time_columns(engine)


# (column name, DDL type) pairs added after the original schema shipped.
_SESSION_TIME_COLUMNS = (
    ("time_spent_seconds", "INTEGER NOT NULL DEFAULT 0"),
    ("last_activity_at", "DATETIME"),
    ("paused_at", "DATETIME"),
)


def _ensure_session_time_columns(engine: Engine) -> None:
    """Idempotently add the session time-budget columns (SQLite only)."""
    if not engine.url.get_backend_name().startswith("sqlite"):
        return
    with engine.begin() as conn:
        existing = {
            row[1] for row in conn.exec_driver_sql('PRAGMA table_info("session")')
        }
        for name, ddl in _SESSION_TIME_COLUMNS:
            if name not in existing:
                conn.exec_driver_sql(f'ALTER TABLE "session" ADD COLUMN {name} {ddl}')
