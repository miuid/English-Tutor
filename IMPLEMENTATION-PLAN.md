# English Tutor — Implementation Plan

> A resumable, multi-session build plan. The project spans weeks; no single session finishes it. Each **step** is sized to fit roughly one working session and has a concrete "Done when" check, so any session can pick up the next unchecked box. Read `CLAUDE.md` → `MEMORY.md` → this file to resume.

Last updated: 2026-07-10

## How to work a session (resume protocol)

1. Read `CLAUDE.md`, then `MEMORY.md` (§8 roadmap, §11 session log).
2. Open this file, find the **first unchecked step** on the critical path.
3. Do that one step. Keep changes surgical; write the verification/test.
4. When "Done when" passes: tick the box here, and append a dated entry to `MEMORY.md` §11 (what/decided/next).
5. Stop at a clean, verified boundary — don't leave a step half-done across sessions.

Aim for 1–2 steps per session. A comfortable cadence is ~2–3 steps/week → MVP in ~6–8 weeks part-time.

## Locked tech choices (don't re-litigate — see MEMORY §6/§7)

- Backend: Python 3.12, FastAPI, Uvicorn, SQLAlchemy 2.0, Pydantic v2, SQLite. Tests: pytest.
- LLM: Anthropic Claude Sonnet 4.6 default, behind an `LLMProvider` adapter (swappable by config).
- Skills: the Markdown packages in `skills/` are loaded at runtime — never reimplement teaching logic in code.
- Frontend: React + Vite + TypeScript, minimal.
- Keep it simple: no abstractions beyond what a step needs; add libraries only when a step requires them.

## Global definition of done (every step)

- The "Done when" check passes.
- Any code has at least one test (unit with a fake LLM where a real call isn't needed; real-LLM tests are marked and skippable without an API key).
- No unrelated refactors. The box is ticked and the session log updated.

## Effort key

S = <½ session · M = ~1 session · L = may spill to 2 sessions.

---

## Milestone 0 — Foundations (P0)  ·  unblocks everything

- [x] **0.1 Repo scaffold + tooling** (M)
  - Goal: `backend/` (FastAPI app with `GET /health`) and `frontend/` placeholders; Python deps pinned; run instructions in `backend/README.md`.
  - Touches: `backend/app/main.py`, `backend/pyproject.toml` (or `requirements.txt`), `backend/tests/test_health.py`.
  - Done when: `uvicorn app.main:app` serves and `GET /health` → 200 `{"status":"ok"}`; `pytest` runs green.
  - Depends on: —

- [ ] **0.2 Config layer** (S)
  - Goal: settings module loads from `.env` (LLM provider, model, API key, `DATABASE_URL`); `.env.example` committed; real `.env` gitignored.
  - Done when: app boots from config; missing API key raises a clear error; a test asserts settings load and defaults are correct.
  - Depends on: 0.1

- [ ] **0.3 LLM adapter layer** (M)
  - Goal: `LLMProvider` protocol (`async generate(system, messages) -> str`); `AnthropicProvider` (Sonnet); `FakeProvider` (returns canned text) for tests; a factory that picks provider from config.
  - Touches: `backend/app/llm/`.
  - Done when: unit test with `FakeProvider` passes; a real-LLM test (marked, skipped without key) returns a completion; switching provider is config-only (no code change).
  - Depends on: 0.2

- [ ] **0.4 Skill loader** (M)
  - Goal: read `skills/`; for each skill load `SKILL.md` + reference files + `examples/`; expose `Skill` objects (name, instructions, references, examples, loop_stage).
  - Touches: `backend/app/skills/loader.py`, tests.
  - Done when: loader returns all 8 skills; test asserts count == 8 and that `check-structure` includes its `rubric.md`; a malformed skill dir raises a clear error.
  - Depends on: 0.1

## Milestone 1 — Data layer (P1)

- [ ] **1.1 DB models + init** (L)
  - Goal: SQLAlchemy models for the 9 `ERD.md` entities; `create_all` on startup (no Alembic yet — MVP simplicity).
  - Done when: a test creates student→session→attempt→feedback→rubric_score and reads them back; deleting the student cascades (nothing orphaned).
  - Depends on: 0.1

- [ ] **1.2 Seed Year 8 curriculum + rubric** (M)
  - Goal: a seed script populating `curriculum_outcome` (Year 8 analytical) and the A–E rubric criteria from `reaserch.md` / `skills/give-feedback/rubric.md`.
  - Done when: running the seed twice is idempotent; a test asserts the expected outcome + criterion rows exist.
  - Depends on: 1.1

- [ ] **1.3 Skill registry sync** (S)
  - Goal: on startup, upsert `skill` rows (name, version, loop_stage) from the loader.
  - Done when: 8 skill rows after sync; re-running changes nothing (idempotent); test covers it.
  - Depends on: 0.4, 1.1

## Milestone 2 — Teaching engine (P2)

- [ ] **2.1 Skill execution service (single skill)** (L)
  - Goal: given a skill + inputs, compose the prompt (system = skill instructions + references; user = inputs), call the LLM, return output. Start with `check-structure`.
  - Done when: running `check-structure` on its `examples/sample-01` returns a response; a `FakeProvider` unit test asserts the prompt is composed correctly (includes rubric + student text).
  - Depends on: 0.3, 0.4

- [ ] **2.2 Coaching skills + diagnose-errors router** (M)
  - Goal: run `elevate-vocabulary` and `give-feedback` through the same service; `diagnose-errors` returns a structured route and the service dispatches to the named skill.
  - Done when: `diagnose-errors` on the sample routes to `check-structure`; a `FakeProvider` test verifies the dispatch table.
  - Depends on: 2.1

- [ ] **2.3 Session orchestrator (daily loop)** (L)
  - Goal: a state machine running the 6 stages (set-criteria → model → guided → independent → diagnose→coach → feedback), persisting a `session` with its `attempt`s.
  - Done when: a scripted end-to-end run advances all stages and stores a session with attempts + feedback; test uses `FakeProvider`.
  - Depends on: 2.1, 2.2, 1.1

## Milestone 3 — Eval harness + quality (P3)

- [ ] **3.1 Eval runner over golden examples** (L)
  - Goal: for each skill, feed `examples/sample-01` to the model and judge the output against `expected-01` (LLM-as-judge + simple rule checks, e.g. "focuses on exactly one gap"). Print a pass/fail scorecard.
  - Done when: `python -m app.eval` runs all fixtures and prints results; the 2 weakness skills pass.
  - Depends on: 2.1

- [ ] **3.2 Tune skills to green + persist rubric_score** (M)
  - Goal: adjust skill wording where eval fails; ensure `give-feedback` emits per-criterion A–E that persists to `rubric_score` (the North Star table).
  - Done when: eval green for all 8; a graded attempt writes `rubric_score` rows (criterion + A–E + timestamp).
  - Depends on: 3.1, 1.1

## Milestone 4 — API + UI (P4)

- [ ] **4.1 FastAPI endpoints for the loop** (L)
  - Goal: endpoints to start a session, submit a step / student text, get feedback, get progress; Pydantic schemas.
  - Done when: a full session can be driven over HTTP (httpie/curl); OpenAPI docs render; endpoint tests pass.
  - Depends on: 2.3

- [ ] **4.2 React app + chat loop UI** (L)
  - Goal: Vite React TS app, one screen: tutor turns, an input box, a "paste my school task" field; calls the endpoints.
  - Done when: `npm run dev` and a student can complete a session in the browser against the backend.
  - Depends on: 4.1

- [ ] **4.3 Progress view (North Star)** (M)
  - Goal: a view plotting `rubric_score` A–E per criterion over time.
  - Done when: after ≥2 graded attempts, the per-criterion trend renders.
  - Depends on: 4.2, 3.2

## Milestone 5 — Logging, privacy, packaging (P5)

- [ ] **5.1 interaction_log persistence** (S)
  - Done when: every LLM turn is logged (skill, model, input, output, ts); a test asserts one row per call.
  - Depends on: 2.1

- [ ] **5.2 "Delete my data" path** (S)
  - Goal: an endpoint/script deleting a student and cascading all their data (privacy requirement, `PRD.md` §6).
  - Done when: after deletion a test confirms no rows remain for that student anywhere.
  - Depends on: 1.1

- [ ] **5.3 docker compose + quickstart** (M)
  - Done when: `docker compose up` runs the backend with a persistent SQLite volume; README quickstart works from a clean clone; frontend dev steps documented.
  - Depends on: 4.1

- [ ] **5.4 One-command check** (S)
  - Goal: a `make check` / script running pytest + the eval scorecard.
  - Done when: the command runs both and reports green.
  - Depends on: 3.1

---

## Critical path & parallelism

Critical path: 0.1 → 0.3 → 0.4 → 2.1 → 2.3 → 4.1 → 4.2.
Can run alongside: the data layer (1.x) after 0.1; the eval harness (3.1) as soon as 2.1 exists; logging/privacy/packaging (5.x) mostly independent once their deps are met.

## Suggested weekly shape (part-time)

- Week 1: 0.1–0.4 (foundations).
- Week 2: 1.1–1.3 (data) + 2.1 (first skill runs for real).
- Week 3: 2.2–2.3 (engine + loop).
- Week 4: 3.1–3.2 (eval + tune to green).
- Week 5: 4.1–4.2 (API + UI).
- Week 6: 4.3 + 5.x (progress view, logging, privacy, packaging).

Slip is fine — the plan is resumable by design. Adjust as reality lands; update this file and MEMORY §11 when you do.

## Progress

Milestones done: **0.1** · Next step: **0.2 Config layer**.
(When all boxes above are ticked, the MVP is built: the 8 skills run behind a swappable model, drive the daily loop in a browser, and track A–E progress — locally and privately.)
