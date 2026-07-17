# English Tutor — Backend

Python/FastAPI backend for the AI after-school English tutor.

## Quick start

Requires Python 3.12+.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env  # then set LLM_API_KEY (DeepSeek key; provider defaults to deepseek/deepseek-chat)
uvicorn app.main:app --reload
```

Health check: `GET http://localhost:8000/health` → `{"status":"ok"}`.

## Daily-loop API

Interactive loop for the frontend (docs at `/docs`):

- `POST /api/sessions` `{task_prompt, year_level?, text_type?}` → start; returns session + first tutor turn (success criteria).
- `GET /api/sessions/{id}` → full state: turns in order, stage, ended flag.
- `POST /api/sessions/{id}/advance` → next tutor turn (model → guided → independent).
- `POST /api/sessions/{id}/submit` `{text}` → student submission; at the independent stage this returns diagnosis/coaching/feedback turns and ends the session.
- `GET /api/students/{id}/progress` → all rubric scores for the student, oldest first.

CORS is open to `http://localhost:5173` (Vite dev) and `http://localhost:7100` (preview).

## Tests & lint

```bash
pytest
ruff check app tests
mypy app
```
