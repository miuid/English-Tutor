from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.database import get_session_maker, init_db
from app.skills.sync import sync_skills


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    get_settings()  # validate config on startup, fail fast on missing API key
    init_db()
    session_factory = get_session_maker()
    with session_factory() as session:
        sync_skills(session)
    yield


app = FastAPI(title="English Tutor", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
