# English Tutor

AI-powered after-school English tutor for Australian secondary students (Year 8–12).

## Quick start

### Option A: Docker Compose (recommended)

```bash
# 1. Clone and enter the project
cd english-tutor

# 2. Put your LLM API key in backend/.env
cp backend/.env.example backend/.env
# Edit backend/.env and set LLM_API_KEY (Kimi/Moonshot key; defaults to kimi/kimi-k3)

# 3. Build and start frontend + backend
docker compose up -d --build

# 4. Open the app (UI + API served from one port)
open http://localhost/          # health check: http://localhost/health
```

The frontend container (nginx) serves the production React build and proxies `/api`
to the backend container, so the whole app runs behind a single port (default 80,
override with `WEB_PORT=8080 docker compose up -d`). For deploying to a LAN server,
see `DEPLOYMENT.md`.

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
- **LLM:** Kimi K3 `kimi-k3` default (adapter-swappable; DeepSeek `deepseek-chat` and Anthropic Sonnet available)
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
