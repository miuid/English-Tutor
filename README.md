# English Tutor

AI-powered after-school English tutor for Australian secondary students (Year 8–12).

## Quick start

### Option A: Docker Compose (recommended)

```bash
# 1. Clone and enter the project
cd english-tutor

# 2. Put your LLM API key in backend/.env
cp backend/.env.example backend/.env
# Edit backend/.env and set LLM_API_KEY (DeepSeek key; defaults to deepseek/deepseek-chat)

# 3. Start the backend
docker compose up --build

# 4. Health check
open http://localhost:8000/health
```

### Option B: Local development

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env  # Set LLM_API_KEY
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev   # starts Vite dev server + backend (via scripts/dev.mjs)
```

## Architecture

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0, SQLite
- **LLM:** DeepSeek `deepseek-chat` default (adapter-swappable; Anthropic Sonnet available)
- **Frontend:** React + Vite + TypeScript
- **Skills:** 8 portable Markdown coaching packages loaded at runtime

## Tests

```bash
cd backend
pytest
ruff check app tests
mypy app
```

## API

- `POST /api/sessions` — start a tutoring session
- `GET /api/sessions/{id}` — session state & conversation turns
- `POST /api/sessions/{id}/advance` — next tutor stage (I do → we do → you do)
- `POST /api/sessions/{id}/submit` — submit student text
- `GET /api/students/{id}/progress` — A–E rubric progression over time
- `DELETE /api/students/{id}` — delete all student data (privacy)

OpenAPI docs at `/docs`.
