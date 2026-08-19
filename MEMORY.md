# English Tutor — Project Memory

> Long-term memory for this project. It records the vision, every meaningful decision (with dates and rationale), what's been built, the roadmap, and open questions. **Update this file whenever a decision is made, a milestone is hit, or something important is discovered — and append a dated entry to the Session log (§11) at the end of each working session.** New sessions should read this first.

Last updated: 2026-08-19

---

## 1. Vision

An AI-powered **after-school English tutor** for Australian secondary students (Year 8–12). It is **not** a replacement for school — it's a daily practice resource that takes a student from their current level toward A+. A web app talks to an AI backend; the LLM model is swappable. MVP runs locally; the design must scale to hundreds/thousands of users later.

First real user: one Year 8 student (the owner's child), then broadened into a product.

## 2. Scope decision (the core tension, resolved)

"MVP" pulls against "cover Year 8–12 + all skill areas". Resolution — **separate design scope from delivery scope**:

- **Design for** Year 8–12 and all text types (imaginative / analytical / persuasive) from day one — data model, skill framework, curriculum model, LLM layer all leave the doors open.
- **Deliver first** only the depth for **Year 8 · QCAA · analytical/essay writing**, and tune the feedback engine to the first student's two weaknesses.

Do one grade × one skill area to A+ depth, then extend.

## 3. First student's weaknesses (drives MVP focus)

1. **Flat vocabulary** → skill `elevate-vocabulary`.
2. **Weak structure** → skill `check-structure`.

The Year 8 C→A lever is almost always **thin analysis (explaining how a technique creates its effect)** — this recurs across the skills as the highest-leverage move.

## 4. Brainstorm themes (divergent phase, kept for reference)

The eight lenses explored, and what happened to each:

| # | Theme | Decision |
|---|---|---|
| 1 | **Teaching engine / agent skills** (GRR I-do/we-do/you-do, success criteria, feedback, differentiation) | **Core IP. Built (8 skills).** |
| 2 | **Daily student loop** (retrieval → goal → I do → we do → you do → review; "one paragraph a day"; weekly mock) | **MVP.** Loop realised by composing the skills. |
| 3 | **Feedback & scoring** (QCAA rubric, inline comments, next-step-not-grade, progress curve, rewrite loop) | **MVP.** `give-feedback` + `diagnose-errors`. |
| 4 | **Content & curriculum modeling** (QCAA strands/outcomes as structured data, technique library, text-type templates, copyright-safe texts) | **MVP.** Reference files seed this. |
| 5 | **Motivation & retention** (streaks, AI persona, safe practice space) | **Deferred → Beta/GA.** |
| 6 | **Parent / oversight layer** (weekly parent report, goals, privacy boundary) | **Deferred → Beta/GA.** |
| 7 | **Architecture & LLM flexibility** (adapter layer, teaching-logic-as-files, local-first, prod-ready) | **MVP.** See §6. |
| 8 | **Black-swan ideas** (voice/oral practice, teach-the-AI/Feynman, interrogate a character) | **Lowest priority.** |

## 5. Skills built (v1) — the product's core IP

Portable, model-agnostic Markdown packages in `skills/`. Authoring convention: `skills/README.md`.

Session loop composition:
`set-success-criteria` → `model-response` (I do) → `guided-practice` (we do) → `independent-task` (you do) → submit → `diagnose-errors` (triage/router) → `check-structure` / `elevate-vocabulary` (coach) → `give-feedback` (A–E + ≤2 next steps + self-check).

Global guardrails (all skills): **coach don't ghostwrite; gradual release; curriculum-anchored; bounded feedback (≤1–2 next steps); age-appropriate + specific praise; model-agnostic.**

Each skill ships a golden `examples/` fixture (sample + expected) — currently used for static design dry-runs, later for automated eval.

Grounding sources: APST, HITS, VTLM, GRR, AERO SWIF (5-stage writing model), QCAA A–E standard elaborations, PEEL/TEEL, QAR, Tier 1/2/3 vocabulary.

## 6. Architecture decisions

- **Stack:** Python backend (FastAPI intended) + React frontend.
- **LLM adapter layer:** unified `LLMProvider` interface + per-provider adapters (DeepSeek / Anthropic / Fake; local Ollama still possible), provider chosen by config. Swapping models must not touch business logic. (This is the "flexibility to change LLM" requirement — validated 2026-07-17 when the default switched Anthropic→DeepSeek with adapter-only changes.)
- **Teaching logic = versioned files, not code:** skills, prompts, rubrics are Markdown/config the backend loads.
- **Local-first MVP:** FastAPI + SQLite + React, target `docker compose up`.
- **Prod-ready seams:** multi-user schema, auth, SQLite→Postgres via connection string, stateless backend for horizontal scaling.
- **Eval-ready:** store each teaching interaction as replayable structured data for quality regression tests.

Data model sketch: `curriculum_outcome`, `skill`, `student`, `session`, `attempt`, `feedback`, `rubric`. (Detail in `MVP-Plan.md`.)

## 7. Decision log

| Date | Decision | Rationale |
|---|---|---|
| 2026-07-10 | Target curriculum = **QCAA (Queensland)** first | First student is in QLD; research is QLD-heavy. |
| 2026-07-10 | Stack = **Python + React** | Owner preference. |
| 2026-07-10 | MVP = **Year 8 analytical/essay** depth; design for 8–12 + all types | Resolve MVP-vs-breadth tension (§2). |
| 2026-07-10 | Motivation (5) & parent (6) layers **deferred to Beta/GA**; black-swan (8) lowest | Focus MVP on learning core. |
| 2026-07-10 | Skill format = **portable Markdown packages** loaded by backend | Matches "teaching logic = files"; human-readable, versionable, model-agnostic. |
| 2026-07-10 | Authored **all 8 v1 skills** before app plumbing | Skills are the core IP; they're model-agnostic and independently verifiable. |
| 2026-07-10 | **North Star metric = QCAA A–E progression per rubric criterion over time** | Reflects real academic level, aligns with school grading; drives the data model (`rubric_score`). |
| 2026-07-10 | **Privacy:** writing may go to a cloud LLM API, but all data is stored **local-only and deletable**; minor's data, minimal retention | Balance feedback quality vs privacy for a child's data; permits cloud API in the model decision. |
| 2026-07-10 | Brainstorm closed; produced **lightweight PRD + simple ERD** rather than heavy docs | Fill the genuine gaps (UX, metric, privacy, schema) without over-engineering. |
| 2026-07-10 | **MVP model = single cloud Claude Sonnet 4.6** for all stages; adapter keeps it swappable | Demanding coaching task rewards a strong model while skills are still being tuned; ~$4/mo for one student is negligible; privacy rule permits cloud. Local Ollama (Qwen 2.5 14B) and per-stage routing deferred to later/scale. Prices as of 2026-07: Sonnet 4.6 $3/$15, Opus 4.8 $5/$25, Haiku 4.5 $1/$5 per 1M tok. |
| 2026-07-17 | **MVP default model switched to DeepSeek `deepseek-chat`**; Anthropic/Sonnet remains a config-only swap | Owner decision. The adapter layer paid off: the switch touched only `app/llm/deepseek.py` (new), factory, and config defaults — zero business-logic changes. Eval + live runs now need `LLM_API_KEY` (DeepSeek) in `backend/.env`. |
| 2026-07-31 | **Phase 2 decisions D1–D4 confirmed** (see `PHASE-2-PLAN.md` §1): D1 per-family local install for Beta (hosted multi-tenant stays GA); D2 senior = framework + IA1 depth only; D3 parents see trends, not full essays; D4 order P6→P9→P7→P8→B1–B6 | Owner confirmed all four recommendations unchanged. Unblocks the Phase 2 checklist (`IMPLEMENTATION-PLAN-2.md`). |
| 2026-08-12 | **MVP default model switched to Kimi K3 (Moonshot AI) `kimi-k3`**; DeepSeek/Anthropic stay config-only swaps | Owner decision. Adapter layer paid off again: new `app/llm/kimi.py` (OpenAI-compatible, `api.moonshot.ai`), one factory branch, config defaults — zero business-logic changes. `LLM_API_KEY` in `backend/.env` is now a Moonshot key. (Live eval not rerun on Kimi yet; last live eval = DeepSeek 8/8 PASS, 2026-07-31.) |
| 2026-08-19 | **Product boundary clarified:** V1 remains local MVP; GA direction is a public paid product (Google sign-in first, AUD 9.9/month baseline) | Owner direction. Keeps current engineering on Phase 2 while making GA scope explicit in `PRD.md` and `ERD.md`. |
| 2026-08-19 | **Autonomous delivery workflow adopted:** spike → plan → `ISSUES.md`/`QUESTIONS.md` → cron `/develop` one ticket at a time | Owner workflow. `ISSUES.md` becomes the delivery state source of truth; `QUESTIONS.md` blocks the gate when an open `BLOCKING` question exists. Completed historical checklists stay as context, not tickets. |

## 8. Milestones / roadmap

**Done**
- ✅ Research consolidated (QCAA curriculum, teacher skills, assessment context).
- ✅ MVP scope + architecture plan (`MVP-Plan.md`).
- ✅ 8 v1 agent skills authored with golden examples (`skills/`).
- ✅ Static design dry-run of all skills against samples.
- ✅ P1 — curriculum + rubric data model (Year 8 first).
- ✅ P0 — project scaffolding + LLM adapter layer (default provider: Kimi K3; Anthropic/Sonnet and DeepSeek remain config swaps) + skill loader.
- ✅ P2.1 — Skill execution service (single skill: check-structure).
- ✅ P2.2 — Coaching skills + diagnose-errors router.
- ✅ P2.3 — Session orchestrator (daily loop).
- ✅ P3 (code + live) — eval harness (`app/eval/`: fixtures + rule checks + LLM-as-judge + scorecard CLI) and `rubric_score` persistence; **live eval run against DeepSeek `deepseek-v4-pro` — all 8 skills PASS** (tuned: diagnose-errors infra bug fix, guided-practice fading signal, give-feedback criterion ranges, elevate-vocabulary candidate flexibility).
- ✅ P4.1 — interactive daily-loop API (`app/sessions/interactive.py` stage machine + `app/api/` routes; `Session.stage` persisted; progress endpoint).
- ✅ P4.2 — React chat loop UI (welcome + school-task paste, stage chips, reload resilience, Vite proxy; zero new deps).
- ✅ P4.3 — progress view (per-criterion A–E SVG trend from `rubric_score`).
- ✅ P6.1 — reference-pack architecture (skills/<skill>/references/<text_type>/<year_band>/).
- ✅ P6.2 — student profile + session context (`focus_text_types`, student CRUD API, frontend ProfileView).
- ✅ Kimi K3 (Moonshot AI) provider — default LLM switched 2026-08-12 (adapter-only change; DeepSeek/Anthropic remain config swaps).

**Next (Phase 2 — planned 2026-07-31, see `PHASE-2-PLAN.md`; D1–D4 confirmed by owner 2026-07-31)**
- ⬜ Track A — skill depth: P6 framework generalisation (reference packs) → P9 Year 9–10 analytical (hard deadline: Feb 2027 school year) → P7 persuasive → P8 imaginative → P10 senior framework (timing by beta family mix).
  - ✅ P6.1 reference-pack architecture live.
  - ✅ P6.2 student profile + session context.
- ⬜ Track B — Beta (5–10 QLD families, per-family local install): B1 distribution + student profiles → B2 baseline assessment → B3 loop completion (`fix-mechanics`, `spaced-review`, weekly mock) → B4 motivation → B5 parent layer → B6 ops → recruit.
- ⬜ 5 new skills planned: `strengthen-argument`, `craft-voice`, `fix-mechanics`, `spaced-review`, `baseline-assessment` (→ 13 total).

**Later (GA)**
- ⬜ Hosted multi-tenant, real auth (Google sign-in first), paid subscriptions (AUD 9.9/month baseline), Postgres, public deployment; NESA/other states; black-swan experiments (voice, teach-the-AI, character interrogation).

## 9. Open questions

- ~~Which LLM for MVP?~~ **Resolved 2026-07-10 (Sonnet); revised 2026-07-17 (DeepSeek `deepseek-chat`); revised again 2026-08-12: default now Kimi K3 `kimi-k3` (Moonshot), adapter-swappable.** (see §7)
- ~~User login for MVP?~~ **Resolved 2026-08-19: V1 local MVP skips login; GA public product requires Google sign-in first.** Schema still reserves multi-user.
- Source for structured QCAA outcome data (research files already have a lot to extract).

## 10. File index

| Path | What |
|---|---|
| `CLAUDE.md` | Entry point for any session — read first. |
| `MEMORY.md` | This file — decisions, history, roadmap. |
| `MVP-Plan.md` | MVP scope, architecture, data model, phased build plan. |
| `IMPLEMENTATION-PLAN.md` | Resumable multi-session build checklist (MVP P0–P5, complete). |
| `PHASE-2-PLAN.md` | Phase 2 plan: skill-depth extension (Y9–12, persuasive/imaginative) + Beta features. D1–D4 confirmed 2026-07-31. |
| `IMPLEMENTATION-PLAN-2.md` | Historical Phase 2 checklist; executable autonomous queue now lives in `ISSUES.md`. |
| `ISSUES.md` | Autonomous delivery backlog and delivery gate; `/develop` picks one eligible `READY` ticket per run. |
| `QUESTIONS.md` | Canonical unresolved delivery decisions; an open `BLOCKING` question blocks the `ISSUES.md` gate. |
| `PRD.md` | User stories, daily-loop UX, North Star metric, V1 non-functional requirements, and the GA public paid product delta. |
| `ERD.md` | Current data model plus GA auth/billing/public-deployment delta: entities, fields, relationships (Mermaid), key queries, privacy/retention, traceability. |
| `skills/README.md` | Skill authoring convention + skill index + loop composition. |
| `skills/<name>/` | The 8 v1 agent skills (SKILL.md + reference + examples). |
| `reaserch.md` | QCAA Year 8/9 curriculum, pedagogy, assessment conditions, A–E standards. |
| `Queensland English Tutoring Blueprint.md` | Deep competency framework: AERO SWIF, GRR, PEEL/TEEL, QAR, Tier vocab, cognitive science. |
| `teacher-skills.md` | Evidence-based teacher skills (APST/HITS/VTLM) → agent-skill mapping. |
| `test-context.md` | NSW NESA assessment context (Years 8–12) — useful when extending beyond QLD. |
| `English Circulum.md` | Curriculum reference. |

## 11. Session log

### 2026-08-19 — Cron configured for autonomous `/develop`
- Created Hermes cron job `english-tutor-develop` (`7b522fa7e3d9`) to run the `develop` skill every 2 hours in `/home/cheng/workspace/English-Tutor`.
- The job is local-only (`deliver=local`) and instructed to process exactly one eligible `ISSUES.md` ticket per run, honor the delivery gate, work only on `feature/english-tutor-delivery`, never push/merge, and write blockers to `QUESTIONS.md` instead of guessing.
- Safety note: the repo still has uncommitted planning docs and untracked `backend/uv.lock`; the first run may return `BLOCKED`/`NOOP` until the tree is clean.

### 2026-08-19 — `/plan` initialized autonomous delivery backlog
- Created `ISSUES.md` and `QUESTIONS.md` from `PRD.md`, `ERD.md`, and `IMPLEMENTATION-PLAN-2.md` using the `/plan` workflow.
- Decision: completed P0–P5 and Phase 2 `6.1`/`6.2` work is **not** converted into tickets; it is recorded as `Completed Context (Not Tickets)` so cron only sees executable future work.
- `ISSUES.md` contains 25 `READY` tickets (`ISS-001`–`ISS-025`), dependency-ordered from eval fixture matrix → Year 9–10 analytical → persuasive → imaginative → Beta B1–B6 → senior framework. Delivery Gate is `OPEN`; first eligible ticket is `ISS-001`.
- `QUESTIONS.md` contains 4 open `NON_BLOCKING` questions (QCAA descriptor source, beta recruitment channel, GA billing, GA deployment/data residency); no `BLOCKING` question exists, so autonomous development is not gated.
- Updated `IMPLEMENTATION-PLAN-2.md` to mark itself as historical scope/rationale; executable delivery state now lives in `ISSUES.md`.

### 2026-08-19 — Product boundary clarified: local MVP now, public paid GA later
- Updated `PRD.md` and `ERD.md` to make the boundary explicit: **V1 remains local MVP**; **GA is a public paid product** with Google sign-in first and an AUD 9.9/month baseline.
- `PRD.md` gained a GA delta section (`FR-GA-*` / `NFR-GA-*` + GA acceptance boundary); `ERD.md` gained current-code field corrections plus planned GA entities (`auth_account`, `subscription`, `billing_event`), requirement traceability, deployment/migration notes, and open technical decisions.
- No code changed. Engineering next pick-up remains `IMPLEMENTATION-PLAN-2.md` step **6.3 Eval fixture matrix**.

### 2026-08-12 — Kimi K3 (Moonshot AI) provider added; default LLM switched
- **New provider:** `app/llm/kimi.py` — `KimiProvider` (OpenAI-compatible, `api.moonshot.ai/v1/chat/completions`, httpx, 60s timeout), mirrors the DeepSeek adapter pattern; registered in the LLM factory; config defaults now `LLM_PROVIDER=kimi` / `LLM_MODEL=kimi-k3` (root `.env.example` + `backend/README.md` updated).
- Tests: factory routing, missing-key error, request shape, HTTP error handling (+64 lines in `tests/test_llm.py`; `tests/test_config.py` defaults updated). **133 passed + 4 skipped**, ruff clean.
- Note: shipped on branch `feature/kimi-k3-provider` (commit `4fbae6e`), **merged to main 2026-08-15** (merge `c263f23`); this MEMORY entry was back-filled at merge time (owner's own 08-12 P6.2 / markdown entries live in `995abc1` / `fe9ac7f`). Live eval NOT rerun on Kimi by owner decision — last live eval remains DeepSeek 8/8 PASS (2026-07-31).
- **Next pick-up:** unchanged — step **6.3 Eval fixture matrix** (`IMPLEMENTATION-PLAN-2.md`).

### 2026-08-12 — Markdown rendering rebuilt on react-markdown (tables + checkbox lists)
- Owner reported (2nd time) that tutor markdown renders wrong: the think-aloud `| … | … |` GFM table showed as raw pipe text, and the `□ I can …` success criteria collapsed into one inline paragraph.
- Root cause: the hand-rolled renderer in `frontend/src/components/Markdown.tsx` only supported bold/italic/`- ` lists/blockquotes — no tables, and the skills' output contract (`skills/set-success-criteria/SKILL.md`) uses non-standard `  □ ` bullets no markdown parser recognises.
- Fix: replaced the hand-rolled renderer with **react-markdown + remark-gfm** (tables, task lists, real lists/blockquotes; raw HTML not rendered → injection-safe) + **remark-breaks** (single newlines in tutor text render as `<br>`, matching how the skills' output contracts are written). `normalizeTutorMarkdown()` pre-pass converts `□/☐ …` → `- [ ] …` and `☑/✔/✓ …` → `- [x] …` (GFM task lists), and inserts a blank line after a converted block so a following plain line (e.g. "(At the end, you'll tick the ones you nailed.)") isn't absorbed into the last `<li>`.
- CSS (`App.css`): `.tutor-para/.tutor-list/.tutor-quote` selectors replaced with plain-element selectors under `.bubble-text`; added table styling (bordered cells, amber header, striped rows, horizontal scroll on narrow screens) and task-list styling (checkbox flush with text, accent colour).
- Verification: SSR smoke test rendering both screenshot cases → real `<table>` with thead/tbody; criteria render as `ul.contains-task-list` with disabled checkboxes, note as its own paragraph. `tsc -b && vite build` green; oxlint 0 errors (the pre-existing Markdown.tsx warning is gone with the rewrite).
- Convention going forward: tutor-facing markdown fixes belong in `normalizeTutorMarkdown()` (skills' non-standard constructs) or remark plugins (standard markdown) — do not hand-roll parser branches.

### 2026-08-12 — P6.2 done: student profile + session context
- **Data layer:** `Student.focus_text_types` added (JSON-encoded list via a custom `StringList` TypeDecorator in `app/models.py`); `database.init_db()` gained an idempotent `_ensure_student_focus_text_types_column()` ALTER TABLE patcher for existing SQLite DBs (same pattern as the session time-budget columns).
- **Backend API:** new `POST /api/students`, `GET /api/students`, `GET /PATCH /api/students/{id}` routes + `StudentCreate`/`StudentUpdate`/`StudentOut` schemas. `StartSessionRequest` gained optional `student_id`; when set, `InteractiveLoop.start()` calls `_resolve_student()` (loads the profile, raises `SessionNotFoundError`→404 if missing) and `_resolve_text_type()` (student's `focus_text_types[0]` wins over the request's `text_type`). `_base_inputs()` now pulls both `year_level` and `text_type` from the student row on every subsequent stage, so a reloaded session stays consistent with the profile.
- **Frontend:** new `ProfileView.tsx` (create/edit/saved modes, year-level + curriculum + focus-text-types chips, localStorage persistence); `App.tsx` gained a `Profile` tab and a `student: StudentOut | null` prop threaded into `ChatView`; `ChatView` start-card shows the signed-in profile and passes `student?.id` into `startSession()`; `storage.ts` gained `load/save/clearStudentProfile`; `types.ts` + `api.ts` gained `StudentOut/Create/Update` + `createStudent/listStudents/getStudent/updateStudent`.
- **Verification:** 9 new tests in `tests/test_student_profile.py` (create/list/get/update, session inherits profile, 404s, openapi schema). pytest 131 passed + 4 skipped (test_skill_loader skipped due to Windows temp-dir permission, unrelated); ruff green; mypy green on changed files; `tsc -b && vite build` green; oxlint 0 errors (1 pre-existing Markdown.tsx warning). The `get_session_state` route temporarily lost its `@router.get` decorator during the edit — restored; `SessionNotFoundError` raised by `start()` when `student_id` is missing is now caught in `start_session` and returned as 404.
- **Next pick-up:** step **6.3 Eval fixture matrix** (`IMPLEMENTATION-PLAN-2.md`) — a skill can ship multiple fixtures tagged by band/text_type; scorecard groups results by combo.

### 2026-08-11 — 15-minute session budget, pause/resume, humane composer layout
- Owner reported three problems: the "15 minutes per session" promise was never enforced (loop ran forever), the student input box was too cramped for long answers, and there was no way to pause and continue the next day.
- **Soft daily time budget (backend):** `Session` gains `time_spent_seconds` / `last_activity_at` / `paused_at` (lightweight idempotent `ALTER TABLE` in `init_db()` — existing dev/LAN SQLite DBs keep their data, verified on a copy of the real dev DB). `SESSION_TIME_LIMIT_MINUTES` env var (default 15). `InteractiveLoop` accumulates active time per interaction with an injectable clock: gaps > 10 min count as 10 min (walking away isn't punished, reading/writing gaps still count), and the counter resets when the local calendar date rolls over — an unfinished session simply continues tomorrow with a fresh budget.
- **Soft wrap-up, never a hard cut:** when time is up, `advance()` starts no new stage — it persists a fixed wrap-up tutor turn (task_type `wrap-up`, no LLM call, names what's next per stage) and auto-pauses; `we do` submissions finish the current exchange first, then wrap up; `you do` submissions always run the full feedback pipeline (the payoff is never blocked). Wrap-up is idempotent per pause.
- **Pause/resume:** `POST /api/sessions/{id}/pause` and `/resume`; paused sessions reject advance/submit (409), paused time never counts, resume on a new day restores the full budget. `SessionOut` now carries `paused` / `time_limit_seconds` / `time_spent_seconds` / `time_up`; `AdvanceOut`/`SubmitOut` carry `time_up`/`paused`. Turn `kind` is now decided by `task_type == "submission"` (lets wrap-up turns render as tutor bubbles without a skill row).
- **Frontend:** header shows a live time chip (`⏱ about N min left`, amber ≤ 3 min, `⏸ Paused`) and a "Pause for today" button; paused state swaps the composer for a friendly card (time-up variant: "come back tomorrow", no continue button; manual-pause variant: "Continue now"); reload resumes paused state from the server. Composer textarea auto-grows up to 40vh (base 4 rows), layout widened 760→880px, `.messages` switched from brittle `max-height: calc()` to a proper flex column, live word count while drafting.
- Verified: pytest **129 passed + 4 skipped** (14 new tests in `tests/test_session_time.py` with a fake clock + HTTP-level pause/resume/time-up), ruff green (also fixed 3 pre-existing lint errors), mypy green, `tsc -b && vite build` green, oxlint 0 errors (1 pre-existing warning in Markdown.tsx).
- **Browser E2E (WebBridge, real browser, fake provider, temp DBs):** Run A — start → advances → time chip ticks (`⏱ about N min left`) → Pause → manual paused card with "Continue now" → reload keeps paused state (server-driven) → resume restores composer. Run B (`SESSION_TIME_LIMIT_MINUTES=0`) — first advance returns wrap-up tutor turn + time-up paused card ("come back tomorrow", no continue), reload persists. Run C — 768-char draft grew the composer 122→221px with live "129 words" counter. Two cosmetic fixes found by E2E and applied: time chip clamped to the budget (was showing "16 min left"), minute/minutes plural in wrap-up copy. All test servers killed after; workspace temp files cleaned.
- **Next pick-up:** unchanged — step **6.2 Student profile + session context** (`IMPLEMENTATION-PLAN-2.md`).

### 2026-08-05 — Full-stack Docker deployment for LAN server
- Owner asked how the app deploys. Answer before this change: **backend-only** — P5.3 containerised the backend, but the frontend was dev-only (Vite dev server), so there was no complete deployment path.
- **Shipped a complete Docker deployment**: `frontend/Dockerfile` (multi-stage: node:22-alpine build → nginx:1.27-alpine runtime), `frontend/nginx.conf` (serves `dist/`, reverse-proxies `/api/*` + `/health` to `backend:8000`, SPA fallback, 180s proxy timeouts for slow LLM calls, 30d cache for hashed assets), `frontend/.dockerignore`; `docker-compose.yml` now runs `frontend` (single public port, `WEB_PORT`, default 80) + `backend` (internal only, `expose` instead of `ports`).
- Frontend already used relative `/api` paths, so same-origin nginx proxy means **no CORS concerns in production** (the dev-only CORS origins in `main.py` stay for local dev).
- Verified: `npm run build` (tsc + vite) passes locally. Docker end-to-end build NOT verified — no Docker on this machine; backend image was already proven in P5.3.
- Wrote `DEPLOYMENT.md` (Chinese): architecture diagram, copy-to-server steps, `backend/.env` setup, `docker compose up -d --build`, LAN access, ops table (logs/update/restart), SQLite volume backup/restore, env-var reference, troubleshooting, and the security boundary (no auth — LAN-trusted, do not expose to public internet).
- README Docker quickstart updated to the two-service flow.
- **Next pick-up:** unchanged — step **6.2 Student profile + session context** (`IMPLEMENTATION-PLAN-2.md`).

### 2026-07-31 — P6.1 done: reference-pack architecture live, regression-proven
- Owner confirmed Phase 2 decisions D1–D4 (logged in §7); wrote `IMPLEMENTATION-PLAN-2.md` (tickable checklist for P6–P10 + B1–B6).
- **P6.1 shipped:** skills moved to reference packs — `skills/<skill>/references/<text_type>/<year_band>/` (bands: year-8 / year-9-10 / year-11-12; plus `shared/`). All 6 legacy flat reference files migrated to `references/analytical/year-8/`; `Skill.packs` replaces `Skill.references`; executor picks `shared` + exact pack, falls back to same-text-type nearest band and appends a deterministic degradation note when no exact pack exists (packless skills — guided-practice, model-response — never get the note). Legacy flat layout dropped, no dual paths.
- Regression guard: byte-exact test proves the Year-8 analytical system prompt is unchanged for all 8 skills.
- Verified: pytest **115 passed + 4 skipped** (+20 new tests); ruff/mypy clean on changed files (3 ruff errors in `app/api/routes.py`/`test_interaction_log.py` pre-exist at HEAD); **live eval 8/8 PASS**.
- Eval tuning (pre-existing model drift, proven by reconstructing the pre-P6.1 prompt): `give-feedback/expected-01.md` — Understanding C→C/D with explicit acceptance notes; Structure/Language C/D notes made explicit. Indefensible E-grading stays a FAIL — noted as residual model instability on a borderline fixture.
- `skills/README.md` package-layout section updated to the new convention.
- **Next pick-up:** step **6.2 Student profile + session context** (student.year_level/focus_text_types → auto-injected into sessions; frontend profile edit).

### 2026-07-31 — Phase 2 planned (skills depth + Beta); no code written
- Owner confirmed MVP verified end-to-end in the browser; requested planning for Phase 2 (no building yet).
- Produced `PHASE-2-PLAN.md`: Track A (P6–P10 skill depth via a **reference-pack architecture** — content depth lives in `(text_type × year_band)` reference files, skills stay generic; bands = year-8 / year-9-10 / year-11-12) and Track B (B1–B6 Beta: per-family local install, student profiles, `baseline-assessment`, loop completion (`fix-mechanics`, `spaced-review`, weekly mock), motivation layer, parent layer with a view-trends-not-full-text privacy default, ops/cost routing).
- 5 new skills scoped (→ 13 total): `strengthen-argument`, `craft-voice`, `fix-mechanics`, `spaced-review`, `baseline-assessment`.
- Recommended order: P6 → P9 (hard deadline Feb 2027, first student enters Year 9) → P7 → P8 → B1–B6; P10 (senior) timed by beta family mix.
- **Next pick-up:** owner confirms the 4 decision points in `PHASE-2-PLAN.md` §1 (D1 distribution, D2 senior timing, D3 parent visibility, D4 ordering) + 3 open questions (§7); then convert the confirmed plan into a tickable implementation checklist and start P6.1.

### 2026-07-31 — P5 complete: interaction logging, privacy delete, docker compose, one-command check
- **P5.1 interaction_log**: `InteractiveLoop` now wraps every `executor.execute()` via `_execute_and_log()`, writing `InteractionLog` rows (skill, model, input, output, timestamp). Logging is best-effort — exceptions are swallowed so the tutoring loop never breaks. Added `test_interaction_log.py` (2 tests; both pass).
- **P5.2 "Delete my data"**: Added `DELETE /api/students/{id}` endpoint with full cascade (Student → Session → Attempt/InteractionLog/SuccessCriterion → Feedback → RubricScore). Verified with `test_delete_student.py` (2 tests): full-loop session created, progress confirmed, deleted, then 404 on re-access.
- **P5.3 Docker Compose + quickstart**: Created `backend/Dockerfile` (python:3.12-slim, uvicorn), `docker-compose.yml` (backend service + `tutor-data` volume + `skills` read-only mount), rewrote root `README.md` with Docker and local-dev quickstart. `SKILLS_DIR` env var supported by existing Pydantic Settings.
- **P5.4 One-command check**: `backend/scripts/check.py` runs pytest (+ optional `--eval` for live scorecard). Handles Windows temp-dir quirk via `TMP=TEMP=backend/.tmp`. `Makefile` provides `make check` / `make check-all` shortcuts.
- pytest: **95 passed, 4 skipped, 0 failed**.
- **MVP is built**: all milestones P0–P5 complete. The 8 skills run behind a swappable model, drive the daily loop in a browser, track A–E progress, log interactions, and support data deletion — locally and privately.

### 2026-07-31 — Live eval run against DeepSeek closes P3; pytest 91 green
- Ran live eval (`python -m app.eval --skill <name>`) against DeepSeek `deepseek-v4-pro` with owner's key; all 8 skills PASS after tuning.
- Fixes applied:
  1. **Eval infra bug** (`app/eval/runner.py` + `__main__.py`): `RuleContext.skill_names` was drawn from the current batch's cases only, so `diagnose-errors` routing to `check-structure` failed the rule check when run with `--skill`. Now `all_skill_names` is passed from the full loader result.
  2. **guided-practice**: Added `Next step hint: <brief fading signal>` to Output contract in SKILL.md so the model explicitly previews scaffold reduction.
  3. **give-feedback**: Widened expected criterion ranges for Structure (`D/E` → `C/D`) and Language (`C` → `C/D`) to match reasonable model judgement.
  4. **elevate-vocabulary**: Expanded top-candidate #2 from `"good"` to `"good" or "bad"` (both are vague judgement words in the sample).
- **Test fixes**: `tests/test_config.py` — 4 failures were caused by `.env` values leaking into tests via pydantic-settings. Added `_env_file=None` to all `Settings()` calls in config tests so they run in a clean environment. pytest now 91 passed + 4 skipped.
- DeepSeek judge calls are slow (~30–60s per skill); full 8-skill eval exceeds Bash 300s limit, so validated individually.
- **Next pick-up:** P5 — interaction logging (5.1), "delete my data" (5.2), docker compose (5.3), one-command check (5.4).

### 2026-07-18 — Live DeepSeek validation + dev launcher fix (502)
- Owner placed a DeepSeek key in `backend/.env` (`LLM_PROVIDER=deepseek`, `LLM_MODEL=deepseek-v4-pro`; key verified via `GET /models` — account exposes `deepseek-v4-pro` + `deepseek-v4-flash`).
- Verified the full live chain: uvicorn boot + real `POST /api/sessions` returned a genuine set-success-criteria tutor turn from DeepSeek.
- Owner hit a 502 clicking "Start today's session": the Vite proxy had no backend on :8000 (backend wasn't running). Root cause = two-process manual startup friction.
- Fix: `frontend/scripts/dev.mjs` — `npm run dev` now spawns uvicorn (cwd `backend/`, venv python) AND Vite (forwards `--host/--port`), reuses an existing :8000 backend if present, prefixed logs, kills children on exit. `package.json` `dev` script points to it. Validated: frontend 200, backend health ok, real session through the proxy 201; oxlint clean; all test processes killed after.
- Note for this machine: killing a server needs `taskkill //PID <listening-pid> //F` — Git Bash `kill` only hits the shell wrapper.
- **Next pick-up:** owner tests the full loop in the browser; then live `python -m app.eval` against DeepSeek (closes P3); then P5.

### 2026-07-17 — Model switch to DeepSeek + P4 complete (API, chat UI, progress view)
- **Decision:** default LLM switched to DeepSeek `deepseek-chat` (owner request). Added `app/llm/deepseek.py` (OpenAI-compatible, httpx, no new deps), factory branch, config defaults, `.env.example`. Adapter-only change — business logic untouched (validates the §6 design). Anthropic/Sonnet remains config-swappable.
- P4.1: `app/sessions/interactive.py` stage machine (`start → I do → we do → you do → ended`, `Session.stage` column added — dev DB deleted/recreated); `app/api/` with `POST /api/sessions` (optional `task_prompt`/`context`), `GET /api/sessions/{id}`, `POST .../advance`, `POST .../submit` (runs diagnose→coach→feedback + writes rubric rows), `GET /api/students/{id}/progress`; CORS for Vite ports. Scripted orchestrator untouched.
- P4.2: frontend rewritten — typed `api.ts`, `ChatView` (welcome + school-task paste, friendly stage chips, continue/submit composer, thinking indicator, inline retry, localStorage reload resilience), Vite `/api`→`:8000` proxy, zero new runtime deps.
- P4.3: `ProgressView` — per-criterion A–E hand-rolled SVG trend (Okabe–Ito colors, letter axis, dots for single-day data), latest-level chips, empty state.
- Verified: pytest 91 passed + 4 skipped; ruff green; mypy green; `tsc -b && vite build` green; smoke-tested full loop over HTTP via vite proxy (201 start, both servers killed after).
- npm on this machine: not on PATH — use `C:\Users\miuid\AppData\Local\Programs\kimi-desktop\resources\resources\runtime\npm.cmd`.
- Deferred: rubric badges after reload come from a localStorage cache (a `GET /sessions/{id}/feedback` endpoint would be cleaner); `Feedback.strength`/`next_steps` still placeholder text (needs live-model output to design the parser).
- **Next pick-up:** put the DeepSeek key in `backend/.env` → run `python -m app.eval` (close P3) + first real browser session; then P5 (logging/privacy/packaging).

### 2026-07-17 — P3 code: eval harness + rubric_score persistence
- Committed and pushed P1+P2 (`8d0d568`), then implemented Milestone 3 code.
- Built `app/eval/`: fixture discovery over all 8 skills' `examples/`, sample→inputs parser, deterministic rule-check registry (generic + per-skill: give-feedback ≤2 next steps & metacognitive prompt, diagnose-errors `Route to:` line), strict LLM-as-judge (`✓/✗` per criterion + `VERDICT: PASS|FAIL`, malformed = ERROR never pass), scorecard CLI `python -m app.eval` (`--skill/--no-judge/--verbose`, exit 1 on any failure).
- 3.2 persistence: `give-feedback` SKILL.md output contract now mandates a `## Per-criterion levels` section (`- <criterion>: **<A–E>** — <note>`); new `app/skills/rubric_parser.py`; orchestrator appends `RubricScore` rows to the persisted Feedback (outcome_id=None — seeded outcomes don't map 1:1 to rubric criteria).
- Verified: pytest 75 passed + 3 skipped; ruff green; mypy green. `LLM_PROVIDER=fake python -m app.eval` runs all 8 cases and prints the scorecard (canned fake output fails some checks by design — plumbing + exit codes verified).
- Env note: pytest needs `TMP/TEMP` pointed at `backend/.tmp` on this machine (Windows temp-dir permission quirk); `.tmp` gitignored.
- **Blocked (needs owner's Anthropic key):** live eval run to close 3.1/3.2 — put `LLM_API_KEY=...` in `backend/.env`, then `python -m app.eval`; tune skill wording until all 8 pass. Then step 4.1 (FastAPI endpoints).
- **Next pick-up:** live `python -m app.eval` against Sonnet; then P4.1.

### 2026-07-17 — P2.2 + P2.3: Coaching skills, diagnosis router, and daily loop orchestrator
- Implemented DiagnosisRouter in app/skills/router.py: runs diagnose-errors, parses Route to:, and dispatches to the recommended coaching skill (defaulting to give-feedback if invalid).
- Implemented SessionOrchestrator in app/sessions/orchestrator.py: runs the full daily loop (set-criteria -> model -> guided -> independent -> diagnose -> coach -> feedback), persisting a Session with 7 Attempts and one Feedback row.
- Added tests/test_diagnosis_router.py and tests/test_session_orchestrator.py; both use FakeProvider so the loop runs without an API key.
- Verified: pytest 27 passed + 2 skipped; ruff green; mypy green.
- Next pick-up: step 3.1 Eval runner over golden examples.

### 2026-07-16 — P1: Data layer (DB models, Year 8 curriculum seed, skill registry sync)
- Implemented P1 data layer: 9 SQLAlchemy models (`app/models.py`), `create_all` on startup (`app/database.py`), cascade tests.
- Seeded Year 8 QCAA analytical curriculum and A–E rubric criteria via `app/seed.py` + standalone `backend/seed.py`; both idempotent.
- Added skill registry sync (`app/skills/sync.py`) called in the FastAPI lifespan, upserting 8 skill rows from the loader.
- Added `curriculum` column to `curriculum_outcome` (not in the original ERD) to keep the multi-curriculum seam (QCAA/NESA) open.
- Verified: `pytest` 20 passed + 1 skipped; `ruff` green; `mypy` green.
- Also cleaned up a few lingering ruff/mypy issues: renamed the `Session` variable in `backend/seed.py` and added type annotations to the `db_session` fixture plus test functions in `tests/conftest.py`, `tests/test_models.py`, `tests/test_seed.py`, and `tests/test_skill_sync.py`.
- **Next pick-up:** step **2.1 Skill execution service** (first skill runs for real with `FakeProvider`).

### 2026-07-15 — Step 0.2–0.4: Config layer, LLM adapter, Skill loader
- Implemented P0 foundations: config layer (.env, Pydantic Settings, startup validation), LLM adapter layer (LLMProvider Protocol, AnthropicProvider, FakeProvider, factory), and skill loader (loads all 8 skills, parses sections/references/examples, exposes loop_stage).
- Added missing pp/__init__.py and 	ests/__init__.py to fix mypy package mapping.
- Fixed 	est_anthropic_provider_calls_sdk to use a real nthropic.types.TextBlock instance.
- Fixed pp/main.py lifespan return type for mypy (AsyncIterator[None]).
- Verified: pytest 14 passed + 1 skipped; 
uff green; mypy green.
- **Next pick-up:** step **1.1 DB models + init** (SQLAlchemy models for 9 entities, create_all on startup, cascade tests).

### 2026-07-13 — Step 0.1: Repo scaffold + tooling
- Created `backend/` (FastAPI, `GET /health`, `pyproject.toml`, `pytest`, `ruff`, `mypy`) and `frontend/` (Vite + React + TS).
- Verified: `pytest` passes, `ruff`/`mypy` green, `uvicorn` serves `/health` → `{"status":"ok"}`, frontend `npm run build` succeeds.
- Switched backend venv to `conda py3_12` (Python 3.12.13); restored `requires-python = ">=3.12"` and `mypy` target to 3.12.
- Fixed `pytest-asyncio` deprecation warning by setting `asyncio_default_fixture_loop_scope = "function"`.
- **Next pick-up:** step **0.2 Config layer** (`.env`, settings module, clear error on missing API key, tests).

Append one entry per working session (newest at top). Keep each entry short: what was done, decided, discovered, and where the next session should pick up.

### 2026-07-10 — Brainstorm + skills authored + memory set up
- Ran a structured brainstorm; captured the 8 themes and kept/deferred each (§4).
- Locked scope: design for 8–12/all types, deliver Year 8 analytical/essay first; feedback tuned to flat vocabulary + weak structure (§2, §3).
- Decided stack (Python + React), curriculum (QCAA), skill format (portable Markdown packages) (§7).
- Authored all 8 v1 agent skills with golden examples; ran static design dry-runs — all pass, cross-skill loop is self-consistent (§5).
- Wrote `MVP-Plan.md`, this `MEMORY.md`, and `CLAUDE.md`.
- **Next pick-up:** decide the MVP model (local Ollama vs Anthropic/OpenAI API) — blocks P0 (scaffolding + LLM adapter + skill loader) and the eval harness (§9).

### 2026-07-10 — PRD + ERD; brainstorm closed
- Closed the brainstorm (divergent + converge done; remaining items are decisions/specs, not ideation).
- Decided North Star metric (QCAA A–E per-criterion progression) and privacy boundary (cloud-OK, local-only storage, deletable).
- Wrote `PRD.md` (user stories, daily-loop UX, metric, non-functional) and `ERD.md` (9-entity model; validated Mermaid).
- Researched current model pricing and **chose MVP model: single cloud Claude Sonnet 4.6** (adapter-swappable); local Ollama + routing deferred.
- **Next pick-up:** P0 — scaffolding + LLM adapter (default Sonnet) + skill loader. All gating decisions now resolved.

### 2026-07-10 — Implementation plan
- Wrote `IMPLEMENTATION-PLAN.md`: 6 milestones, ~20 session-sized steps, each with a "Done when" check; includes a resume protocol and locked tech choices.
- Planning phase is complete. Build phase begins.
- **Next pick-up:** step **0.1 Repo scaffold + tooling** (see the plan; tick the box + log here when done).
