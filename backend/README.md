# English Tutor — Backend

Python/FastAPI backend for the AI after-school English tutor.

## Quick start

Requires Python 3.12+.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Health check: `GET http://localhost:8000/health` → `{"status":"ok"}`.

## Tests & lint

```bash
pytest
ruff check app tests
mypy app
```
