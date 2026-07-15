from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> None:
    get_settings()  # validate config on startup, fail fast on missing API key
    yield

app = FastAPI(title="English Tutor", version="0.1.0", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
