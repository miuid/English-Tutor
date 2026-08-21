# English Tutor

AI-powered after-school English tutor for Australian secondary students (Year 8–12).

**Beta family?** Start with `BETA-HANDBOOK.md` — install guide, privacy
expectations, feedback channel, and the weekly check-in template.

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

### First run (guided)

The first time anyone opens the app in a browser, a short wizard runs before the
main UI:

1. **Pick or create a profile.** If the server already has student profiles (e.g.
   a shared family server), pick one; otherwise create a new profile with name,
   year level, curriculum, and optional focus text types.
2. **Start your first session.** You land on the *Today* tab — paste a school
   task if you have one (optional) and press **Start today's session**.

From there the daily loop runs (goal → I do → we do → you do → feedback). The
profile stays editable any time in the **Profile** tab; **Clear** there unlinks
the browser and returns to the wizard (useful for siblings sharing a device).
A clean machine following Option A should reach a first session in under 15
minutes, most of which is the one-time image build.

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
- **Skills:** 10 portable Markdown coaching packages loaded at runtime

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
- `GET /api/students/{id}/telemetry` — aggregated usage metrics (counts only, no content)
- `GET /api/students/{id}/feedback-package` — one-click beta issue report download
- `DELETE /api/students/{id}` — delete all student data (privacy)

OpenAPI docs at `/docs`.

## Reporting a beta issue

Something broken? Open the **Profile** tab and click **Report a problem** to
download a feedback package (one JSON file), then email it to the developer.

**What's inside** (safe to share): usage counts and totals, non-secret config
(LLM provider/model, time budget), environment versions, the last sessions'
stage/timing, and the last LLM calls' model/skill/**lengths**. It contains
**no** student writing, no tutor responses, no rubric notes, no student name,
and no API key — that boundary is enforced by automated tests.

**Reading the package in under 10 minutes:**

1. `config` — is the family on the expected `llm_provider` / `llm_model`?
   A wrong provider or an overridden `llm_stage_models` explains most
   "feedback sounds different" reports.
2. `telemetry.llm_empty_output_calls` — above zero means the LLM returned
   empty completions ("feedback never arrived"); `llm_calls_by_model` shows
   which model produced them.
3. `recent_sessions` — a session stuck on a non-`ended` `stage` with a low
   `time_spent_seconds` points at the stage where the loop stalled.
4. `recent_interactions` — `output_chars: 0` rows, or suddenly huge
   `input_chars`, localise the failing skill by name and time.
5. `environment` — version drift (old app, missing skills) explains behaviour
   already fixed in a newer build.
