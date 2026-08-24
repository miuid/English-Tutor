# English Tutor — Project Memory

> Long-term memory for this project. It records the vision, every meaningful decision (with dates and rationale), what's been built, the roadmap, and open questions. **Update this file whenever a decision is made, a milestone is hit, or something important is discovered — and append a dated entry to the Session log (§11) at the end of each working session.** New sessions should read this first.

Last updated: 2026-08-22

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
| 2026-08-21 | **All four delivery questions answered (Q-001–Q-004):** Q-001 import official QCAA syllabus PDFs before senior depth claims (ISS-024/025 constraint); Q-002 beta recruitment = friend families first; Q-003 GA billing deferred, likely Stripe; Q-004 GA deployment/residency deferred | Owner decisions recorded in `QUESTIONS.md` with constraints propagated to ISS-023/ISS-024. Delivery Gate stays `OPEN`. |
| 2026-08-24 | **Q-005 answered: ISS-025 re-scoped to "Senior analytical pack (IA2 + EA framework)"** | Owner confirmed Option 1. Official QCAA English 2025 v1.3 syllabus defines IA1 as a spoken persuasive response; analytical depth belongs to IA2 (internal written) with EA as exam-mode analytical. ISS-025 unblocked; gate back to `OPEN`. |
| 2026-08-21 | **Official QCAA English 2025 v1.3 syllabus imported; senior framework modelled (ISS-024).** Discovery: official IA1 = *spoken persuasive response*; analytical senior instruments are IA2 + EA → Q-005 raised to re-scope ISS-025 | Q-001 sourcing constraint satisfied for senior rows: extracted official syllabus archived at `research/official/` (CC-BY 4.0, provenance header). ISS-025 must be re-scoped before it starts (pending owner answer on Q-005). |

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

### 2026-08-22 — `/develop` BLOCKED: ISS-025 awaits Q-005 re-scope decision
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN, Active issue None. Found ISS-024 index row stale (`READY` vs authoritative `DONE` block) — synced. Only remaining ticket: ISS-025.
- **No implementation.** ISS-025's acceptance criteria require an "IA1 analytical pack", but the official QCAA English 2025 v1.3 syllabus (imported in ISS-024) defines IA1 as a *spoken persuasive response*; the analytical instruments are IA2 + EA. Building as written would model a non-existent instrument and violate the Q-001 sourcing constraint. Q-005 (the re-scope decision) is OPEN and is an owner decision — not self-answered.
- **Tracker updates only:** Q-005 severity escalated `NON_BLOCKING` → `BLOCKING` (it now blocks the only remaining ticket); ISS-025 set `BLOCKED` (`Blocked by: Q-005`); Delivery Gate set `BLOCKED` (Blocking questions: `Q-005`). No code touched; no tests run (nothing to verify).
- **Needs Cheng:** answer Q-005. Recommendation stands at Option 1 — retitle ISS-025 to "Senior analytical pack (IA2 + EA framework)": IA2 is the internal analytical written instrument, EA the exam-mode analytical one. Once answered, re-scope the ticket's title/acceptance criteria and reopen the gate (or run `/plan`). After ISS-025 the backlog is complete.

### 2026-08-21 — ISS-024 done: QCE senior instrument modelling
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-024 (P2, dep ISS-023 DONE).
- **Official source imported (Q-001 satisfied):** QCAA English General Senior Syllabus 2025 v1.3 (January 2026, © State of Queensland (QCAA) 2026, CC-BY 4.0) archived as extracted text at `research/official/english-2025-v1.3-syllabus.md` with a provenance header. The QCAA site is Cloudflare-gated (curl + headless browser both blocked); extraction went through a rendering proxy and was verified against the official document metadata (53 pages, v1.3).
- **Shipped:** 8 senior `curriculum_outcome` framework rows in `app/seed.py` — Units 1-4 (`QCAA-Y11-U1/U2`, `QCAA-Y12-U3/U4`, text_type `framework`) + instruments (`QCAA-Y12-IA1` persuasive spoken, `IA2` analytical written, `IA3` imaginative exam, `EA` analytical exam; each 25%, three ISMG criteria with mark allocations). Year 8-10 rows byte-identical; no loop code touched.
- **Shipped:** `research/qce-senior-instrument-modelling.md` — course structure, instrument table, ISMG structure, and the ISMG→A-E mapping strategy (three official criterion names; shared qualifier ladder fragmented→…→discerning bridges ISMG and reporting standards; /25 per instrument → /100 subject result; A-E always provisional until QCAA confirmation).
- **Key finding → Q-005 (`NON_BLOCKING`):** official IA1 is a *spoken persuasive response*, not analytical. ISS-025 "Senior IA1 analytical pack" matches no official instrument and needs re-scoping to IA2/EA before it starts (recommendation recorded; note added to ISS-025).
- Verified: seed tests 7 passed; full suite **263 passed/4 skipped** (+1); ruff clean; mypy unchanged vs baseline.
- **Next pick-up:** ISS-025 — but only after Q-005 is answered (re-scope to IA2/EA). Queue otherwise complete after ISS-025.

### 2026-08-21 — ISS-023 done: beta handbook (B6.3)
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-023 (P2, dep ISS-022 DONE).
- **Shipped:** root `BETA-HANDBOOK.md` (English, friend-family tone per Q-002) — §1 parent one-pager (15-min daily loop, never ghostwrites, beta honesty), §2 non-technical install guide (Docker Desktop → unzip → `backend/.env` key → `docker compose up -d --build` → first-run wizard) + everyday-use/troubleshooting/uninstall, §3 privacy expectations (local-first; only student writing leaves the machine, to the LLM API; delete any time), §4 feedback channel (Profile → Report a problem → email the package), §5 weekly check-in template. README links to it.
- Docs-only change. Verified: every command reviewed against DEPLOYMENT.md/README (all match); full backend suite **262 passed/4 skipped** — baseline unchanged. No physical clean-machine run in this env; the install-alone criterion rests on the doc review + ISS-010 wizard smoke evidence.
- **Next pick-up:** ISS-024 — QCE senior instrument modelling (gated by Q-001: official QCAA syllabus PDFs must be imported and cited before it can complete).

### 2026-08-21 — ISS-021 done: per-stage model routing (B6.1)
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-021 (P2, dep ISS-020 DONE).
- **Shipped:** `Settings.llm_stage_models` (env `LLM_STAGE_MODELS`, JSON object mapping loop_stage -> model override) + new `app/llm/routing.py::StageProviderRouter` (cached `(provider, model)` per stage via the existing factory). Routing stays within the configured provider family — one API key, only the model tier changes per stage (e.g. heavy triage/coach/end on the strong model, light retrieval/start/I do/we do/you do on a cheaper tier).
- **Opt-in wiring:** `SkillExecutionService` gains an optional `stage_router`; `get_executor` attaches one only when the table is non-empty. Empty table -> byte-identical legacy behaviour, and `get_provider` dependency overrides in tests plus the router-free eval harness are untouched. Skill contracts unchanged.
- **Honest logging:** `interaction_log.model` now records the actual per-stage model (`executor.model_used_for(skill)`).
- Mid-run defect caught by the suite: unconditional router wiring bypassed provider overrides (22 API-test failures) — fixed by making routing opt-in; documented in ISSUES.md evidence.
- Verified: targeted 59 passed/3 skipped (62/3 with interaction-log tests); full suite **253 passed/4 skipped** (+11 new tests); ruff clean; mypy `app` clean, touched test files byte-identical to baseline (stash-verified). Frontend untouched.
- **Next pick-up:** ISS-022 — privacy-safe telemetry + feedback package.

### 2026-08-21 — ISS-020 done: shared parent-student goal setting (B5.2)
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-020 (P2, dep ISS-019 DONE).
- **Shipped:** `student.shared_goal` (nullable VARCHAR(280)) — the family's agreed qualitative weekly focus, distinct from the numeric `weekly_goal` (ISS-016). Set/edit/clear via the profile API (PATCH `""` clears; omitted field untouched); idempotent SQLite column patch follows the established `_ensure_student_*` pattern.
- **Session opening:** `InteractiveLoop.start()` injects `shared_goal` into both opening skill inputs (spaced-review + set-success-criteria) only when set — goal-less openings stay byte-identical. The ChatView start card surfaces it before the session begins.
- **Privacy (D3):** the goal crosses into the parent report deliberately (JSON field, printable chip, Parent tab chip) because it is a goal, not student content; D3 marker tests unchanged and green. Export/import round-trips it; pre-ISS-020 exports default to None (format version unchanged).
- Verified: full suite **242 passed/4 skipped** (+5 new tests); ruff clean; mypy 29 errors in the same 4 unrelated baseline files, changed files clean; frontend tsc+vite+oxlint clean.
- **Next pick-up:** ISS-021 — per-stage model routing.

### 2026-08-21 — ISS-019 done: weekly parent report with privacy boundary (B5.1)
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-019 (P2, dep ISS-018 DONE).
- **Shipped:** `backend/app/parent_report.py::build_parent_report` — **derived, never stored** (mirrors streak/level-up decisions): Monday–today local week window, sessions + practice-time counts, weekly-goal state, per-criterion trends (latest/previous level, up/down/steady/new direction, dated points), one honest highlight (this week's level-up, else goal-met), one supportive next-week suggestion (goal nudge → dip revisit → weakest growth area → keep going). Endpoints: `GET /api/students/{id}/parent-report` (JSON) + `GET /api/students/{id}/parent-report/print` (server-rendered printable HTML from the **same** `ParentReport` value; browser prints to PDF — no new dependency, PDFs can never disagree with the app).
- **Privacy (D3):** boundary enforced in exactly one module — the builder reads `Attempt`/`Feedback` only to reach rubric scores; no `student_text`, `task_prompt`, feedback prose, or rubric notes ever leave it. Tests assert marker strings absent from both JSON and HTML; the print page states the boundary to parents.
- **Frontend:** new **Parent** tab + `ParentView.tsx` (week strip, highlight card, trend table, suggestion, privacy note, Print/PDF button opening the server page); types + `getParentReport`/`parentReportPrintUrl` + CSS tokens.
- Verified: targeted 12 passed; full suite **237 passed/4 skipped** (+12 new); ruff clean; mypy 29 errors in the same 4 unrelated baseline files, changed files clean; frontend tsc+vite+oxlint clean; HTTP smoke (FakeProvider, tmp SQLite): JSON report 200 with correct weekly counts + goal nudge, print page 200 `text/html` with same data.
- **Next pick-up:** ISS-020 — shared parent-student goal setting.

### 2026-08-21 — ISS-018 done: coach persona tone setting (B4.3)
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-018 (P2, dep ISS-017 DONE).
- **Shipped:** per-profile `coach_tone` (`warm`/`strict`/`humorous`, default `warm`; `CoachTone` Literal in `models.py` as the single source of truth) + idempotent SQLite column patcher. Executor appends a `--- Coach tone ---` section (directive + "never what you teach" contract note) to the **system prompt** only when a `coach_tone` input is present — opt-in, so eval fixtures and the year-8 byte-identical regression guard are untouched; unknown tones fall back to warm. Wired through every tutor turn in both loops (`InteractiveLoop` incl. baseline/mock, `SessionOrchestrator`). API validates (422), export/import round-trips (400 on invalid, legacy exports default warm). ProfileView tone chips; FirstRunWizard untouched (defaults warm).
- **Design call:** tone is an opt-in executor input rather than an always-on default section — this keeps prompt bytes stable for every caller that hasn't opted in (eval harness), which the byte-identical regression test enforces.
- Verified: declared tests 46 passed/1 skipped; full suite **225 passed/4 skipped** (+13 new); ruff clean; mypy 29 errors in the same 4 unrelated baseline files; frontend tsc+vite+oxlint clean; no-judge eval 26 cases 22/4 — unchanged canned-fake baseline. Live tone-perception check deferred with the other pre-beta live-eval follow-ups (no API credential in this env).
- **Next pick-up:** ISS-019 — weekly parent report with privacy boundary.

### 2026-08-21 — ISS-017 done: criterion level-up celebration (motivation layer B4.2)
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-017 (P2, dep ISS-016 DONE). Tracker hygiene: the ISSUES.md index row for ISS-016 still said `READY` although the authoritative detail block said DONE — index corrected.
- **Shipped:** `backend/app/level_ups.py::build_level_ups` — **derived, never stored** (mirrors the ISS-016 streak decision): a level-up fires when a criterion reaches a personal-best A–E band (`+`/`-` ignored via `band_of`), so within-band moves (C → C+) and dip-recovery re-crossings never re-celebrate; only observed first-arrival progress counts. Events carry criterion, from → to, the rubric note recorded with the new score (the improvement mechanism), scored_at/session_id/feedback_id, oldest first. New `GET /api/students/{id}/level-ups` (404 on unknown student); no schema change.
- **Frontend:** `LevelUpCard` in ProgressView renders the most recent crossing — 🎉 `Level up — <criterion>: <from> → <to>` + the rubric note line, so praise names the real change and its mechanism. `getLevelUps` client + types; fetch failure never blocks the chart.
- Verified: full suite **212 passed/4 skipped** (+12 new in `test_level_ups.py`); ruff clean; mypy 29 errors in the same 4 unrelated baseline test files; frontend tsc+vite build + oxlint clean. HTTP smoke against a real backend (FakeProvider, tmp SQLite): cold start empty → 404 unknown student → D→C crossing served with from/to + mechanism note.
- **Next pick-up:** ISS-018 — coach persona tone setting.

### 2026-08-21 — ISS-016 done: streaks + weekly goal (motivation layer B4.1)
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-016 (P2, dep ISS-015 DONE).
- **Shipped:** `Student.weekly_goal` (default 4, validated 1–14, settable on create/PATCH, export/import round-trips with legacy default; idempotent SQLite patcher for existing DBs) + **derived** streak in `app/motivation.py` — a practice day is any local date with ≥1 session (loop/baseline/mock); streak alive through yesterday, counts back consecutive local days; week = Monday–today, goal counts sessions not days. New `GET /api/students/{id}/motivation` (`MotivationOut`: current_streak, streak_broken, weekly_goal, sessions_this_week, goal_met, last_activity_date).
- **Recovery, never penalty:** a lapsed run reports `streak_broken=True`; the new ProgressView `MotivationStrip` answers with 🌱 "Welcome back — no catching up needed. One session today starts a fresh streak." 🔥 streak chip + weekly chip (⭐ on goal met) render in both empty and populated progress states; ProfileView gains a Weekly goal row + edit select (2–7). No points/shop/leaderboard — per the ticket constraint.
- **Design note:** streak deliberately derived, not stored — one source of truth (session history), mirrors the spaced-review digest pattern.
- Verified: full suite **200 passed/4 skipped** (+12 new in `test_motivation.py`); ruff clean; mypy 29 errors in the same 4 unrelated baseline test files; frontend tsc+vite build + oxlint clean. HTTP smoke against a real backend (FakeProvider, tmp SQLite): cold start 0/4 → session start 201 → streak 1, 1/4 → PATCH goal=1 → goal_met true; 404 unknown student; 422 out-of-range goal; local date correct (Brisbane).
- **Next pick-up:** ISS-017 — criterion level-up celebration.

### 2026-08-21 — ISS-015 done: weekly timed mock mode
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-015 (P1, dep ISS-014 DONE). **Notable:** the tree held uncommitted edits matching this ticket exactly (`run_mock`, `/mock` route, `MockRequest`/`MockOut`, progress `mode`), dated ~00:02 local — a prior cron attempt interrupted before tests/tracker update. Verified green (185 passed/4 skipped) and adopted rather than discarded; no user work overwritten. Recorded in the ISS-015 work log.
- **Shipped:** `InteractiveLoop.run_mock()` — one exam-conditions write → an already-ended mock session (submission `attempt.mode='assessment'` + a summative give-feedback turn with `mode: summative` input so the overall A–E is attached) → per-criterion levels parsed into RubricScore rows. No retrieval/modelling/coaching — QCAA-like conditions mean no scaffolds; feedback stays bounded (one strength, 1–2 next steps) per the give-feedback contract. Route `POST /api/students/{id}/mock` (201 → MockOut with session id, feedback, and the full report; 404 on unknown student). Progress endpoint now returns `mode` per score.
- **Frontend:** ProgressView renders weekly-mock points as ◆ diamonds (daily practice stays ● circles) with a conditional legend note; ChatView start card gains a "Sit this week's timed mock" entry → new `MockView` (exam-conditions explainer → paste timed piece → level badges + Markdown report). `runMock` API client + `MockOut`/`ProgressScoreOut.mode` types.
- Verified: declared verification `pytest tests/test_api_daily_loop.py tests/test_session_time.py` — 33 passed (+3 new: assessment-mode persistence + summative inputs + pack citation, daily-vs-mock mode distinction in progress, 404); full suite **188 passed/4 skipped**; ruff clean; mypy 29 errors in the same 4 unrelated test files as the ISS-014 baseline; `npm run build` + oxlint clean. HTTP smoke against a real backend (FakeProvider): create student → POST /mock 201 → session ended, time_spent 0, submission mode `assessment` → progress endpoint green.
- Live LLM judge eval not run (no valid API credential in this environment); consistent with ISS-005/008/012/013/014, the no-judge harness is the declared verification.
- **Next pick-up:** ISS-016 — streaks + weekly goal.

### 2026-08-20 — ISS-014 done: thirteenth skill `spaced-review` + retrieval stage
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-014 (P1, dep ISS-013 DONE).
- **Shipped:** `skills/spaced-review/` per the authoring convention — SKILL.md (8 required sections; read digest → pick 2–3 targets: weakest criterion first, then the recently coached pattern when days have passed → one short recall/spot/apply-in-one-line item each → self-check answers → onward line; cold start honestly declared) and one **shared-only** reference pack `retrieval-guide.md` (digest shape, three item types, cold-start menu per text type, band calibration with Q-001 derived note for seniors, 3-minute time/tone box). Traced to teacher-skills.md (HITS/VTLM "quick retrieval" lesson opening; AERO SWIF spaced repetition), Blueprint (cognitive load), MVP-Plan §2 (热身 retrieval).
- **Loop change:** retrieval is now loop step 1 in BOTH drivers — `InteractiveLoop.start()` and `SessionOrchestrator.run_daily_loop()` run spaced-review before set-success-criteria and persist a `task_type="retrieval"` tutor turn; the GRR stage machine itself is unchanged. Daily loop is now retrieval → criteria → I do → we do → you do → feedback, the MVP-Plan §2 promise delivered.
- **New module:** `app/sessions/review.py::build_review_history(db, student_id)` — the only history the skill ever sees: days since last ended session, latest rubric level per criterion (weakest first, max 6), most recent coach skills with local dates (max 3); cold-start line when no ended session exists.
- **Fixtures:** sample-01 analytical/year-8 (real digest: Analysis at D + elevate-vocabulary coached 3 days prior; items must trace to the digest, never invent history), sample-02 imaginative/year-9-10 (cold start; must use the fundamentals menu and declare first session).
- Verified: targeted 19 passed; full suite **185 passed/4 skipped** (+3 tests: loader shared-guide, retrieval cold-start, retrieval history inputs); ruff clean; mypy 29 errors in the same 4 unrelated test files as baseline (verified line-by-line for the edited test_interaction_log.py); skill eval 2/2 PASS; full no-judge eval 26 cases, 22 passed/4 failed — unchanged canned-fake baseline; `npm run build` + oxlint clean.
- **Next pick-up:** ISS-015 — weekly timed mock mode.

### 2026-08-20 — ISS-013 done: twelfth skill `fix-mechanics` shipped
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-013 (P1, dep ISS-012 DONE). (Note: the ISS-012 run landed the same day but left no session-log entry — see ISSUES.md ISS-012 for its evidence.)
- **Shipped:** `skills/fix-mechanics/` per the authoring convention — SKILL.md (8 required sections; scan → group errors into *patterns* → coach top 1–2 by frequency × cost-to-reader → rule + quoted student sentence + modelled fix on an *invented* sentence → student repairs own text with instance counts) and one **shared-only** reference pack `mechanics-guide.md` (error classes, band ceilings year-8/9-10/11-12 with senior calibration marked derived per Q-001, errors-vs-stylistic-choices boundary, tone rules). Shared-only by design: mechanics coaching is text-type-agnostic, so no banded packs and no degradation note.
- **Routing:** `diagnose-errors` now dispatches to `fix-mechanics` — SKILL.md route list + contract, plus all six taxonomy packs updated from "(future)" to live. Guard preserved: mechanics routes only when it's the primary major issue AND higher-leverage categories are sound. `DiagnosisRouter` needed no code change (validates against loaded skills); loader `LOOP_STAGES` gains `fix-mechanics: coach`.
- **Fixtures:** sample-01 analytical/year-8 (comma splices + its/it's on a structurally sound paragraph), sample-02 imaginative/year-9-10 (dialogue punctuation + apostrophes; the deliberate fragment "Nothing." must NOT be flagged — that's a fail condition).
- Verified: targeted 23 passed; full suite **182 passed/4 skipped** (+2 tests: loader shared-guide, router mechanics route); ruff clean; mypy 29 errors in the same 4 unrelated test files as baseline; skill eval 2/2 PASS; full no-judge eval 24 cases, 20 passed/4 failed — unchanged canned-fake baseline.
- **Next pick-up:** ISS-014 — new skill `spaced-review` + retrieval stage.

### 2026-08-20 — ISS-011 done: student data export and restore
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-011 (P1, dep ISS-010 DONE).
- **Shipped:** `backend/app/student_transfer.py` — versioned JSON export (`english-tutor-student-export` v1: profile + sessions + success criteria + attempts with feedback/rubric scores + interaction logs, ISO timestamps) and validated import that restores as a NEW student (fresh UUIDs everywhere, references remapped, timestamps preserved so A–E trends survive; skill/outcome FKs kept only when resolvable locally, else NULL). Routes: `GET /api/students/{id}/export` (attachment download) + `POST /api/students/import` (declared before `/students/{student_id}`).
- **Frontend:** ProfileView saved card gains **Export my data** (one-click download + privacy hint); FirstRunWizard gains **Restore from a backup file** so the export → delete → import round-trip works on a clean browser. No cloud sync — file stays local (PRD §6).
- **Design decision:** import always creates a fresh profile (never overwrites) — restoring while the original exists yields a second profile, no PK collisions.
- **Discovery:** the interactive loop never persists `SuccessCriterion` rows, so exported `success_criteria` is legitimately empty for loop sessions; field still round-trips.
- Verified: targeted 17 passed (6 new round-trip/export tests); full suite **175 passed/4 skipped**; ruff clean; mypy 29 errors in the same 4 unrelated test files as baseline; `npm run build` + oxlint clean.
- **Next pick-up:** ISS-012 — new skill `baseline-assessment`.

### 2026-08-20 — ISS-010 done: beta first-run wizard + profile UX
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-010 (P1, dep ISS-009 DONE). First frontend-facing ticket of the ISSUES queue.
- **Shipped:** `FirstRunWizard.tsx` — gated in `App.tsx` on `studentId === null`, so a fresh browser always hits the wizard before the tabbed UI. Wizard lists existing server profiles (`GET /api/students`, pick one — shared family server / new device) or creates a new one (name, year 8–12, QCAA/NESA, optional focus text types); on success it persists id + profile and lands on the Today tab. App now also hydrates `student` from the cached profile on load, so the start card greets by name immediately.
- **Profile UX fix:** ProfileView **Clear** previously removed only the cached profile object and left a stale student id linked; it now clears the id too (`storage.ts` gains `clearStudentId()`) and calls a new `onClear` prop, returning the app to the wizard (siblings sharing a device). Edit-after-first-run unchanged in the Profile tab.
- **Docs:** README "First run (guided)" section + DEPLOYMENT.md 首次使用（首跑向导）; README skills count corrected 8 → 10.
- Verified: `npm run build` + oxlint clean; backend `test_student_profile.py` 9 passed; full backend suite **169 passed/4 skipped** + ruff clean (backend untouched); HTTP smoke of the wizard's exact call chain (list → create → list) green against a real backend with FakeProvider. No physical clean-machine run — the <15-min criterion rests on the documented path + build/API evidence.
- **Next pick-up:** ISS-011 — student data export and restore.

### 2026-08-20 — ISS-009 done: imaginative daily loop seeded and proven
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-009 (P1, dep ISS-008 DONE).
- **Shipped:** `app/seed.py` now idempotently seeds 36 QCAA outcomes — 12 analytical + 12 persuasive (both unchanged) + 12 imaginative across Year 8/9/10 (`QCAA-Y*-IMA-*` codes: Year 8 one-complication/rising-tension + show-don't-tell + consistent POV traced to reaserch.md Year 8 criteria + NAPLAN narrative criteria + the ISS-007 year-8 criteria bank; Year 9 structural experimentation/distinct voice/motif traced to Year 9 criteria + the year-9-10 bank; Year 10 derived one band up per Q-001).
- **No loop code changed:** P6.2's `_resolve_text_type` (profile `focus_text_types[0]` wins on every stage) already wires text_type through the whole loop — the imaginative loop worked end-to-end on the first HTTP test run. Diagnosis routes to `craft-voice`, all pack-bearing prompts cite the imaginative/year-8 packs, 5 rubric scores persist with imaginative criterion names (Story & tension, Character & setting, Showing & voice, Language & vocabulary, Structure & cohesion).
- Verified: targeted 20 passed; full suite **169 passed/4 skipped** (+2 new tests); ruff clean; mypy 29 errors in the same 4 unrelated test files as baseline. One ruff E501 (seed docstring) found and fixed during the run.
- **Next pick-up:** ISS-010 — beta first-run wizard and profile UX.

### 2026-08-20 — ISS-008 done: tenth skill `craft-voice` shipped
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-008 (P1, dep ISS-007 DONE).
- **Shipped:** `skills/craft-voice/` — SKILL.md (three craft dials: key moment shown/told → emotion shown/named → narrator steady/drifting; ONE craft move per turn; model on a different scene; hand back with an "I can…" criterion), two imaginative reference packs (`voice-craft.md` × year-8/year-9-10: Year 8 types — summarised key moment / named emotions / POV drift; Year 9–10 adds thin-or-clichéd imagery at the key beat, the design-vs-drift POV rule, and tone whiplash — with priority rules + band calibration, Q-001 note for Year 10), and two golden fixtures (Year 8 bush story — noise-in-the-dark told in one sentence; Year 9 moving-away opening — shown beats inside the lens but unsignalled drift into Mum's head + third-person "Marcus").
- **Routing wired:** diagnose-errors SKILL.md route list + both imaginative taxonomy packs route showing/immediacy and voice/POV/tone to `craft-voice`; plot/arc/structural control stays with `check-structure`. "planned ISS-008" notes removed from the taxonomies and both give-feedback imaginative rubrics. `LOOP_STAGES` gains the skill as `coach`; skills/README.md index now lists ten skills.
- Lane discipline decision: check-structure keeps plot arc, complication, scene order, structural control; craft-voice owns showing strategy, key-moment craft, narrator/POV/tone; elevate-vocabulary keeps individual word choice.
- Verified: targeted 22 passed; full suite **167 passed/4 skipped** (+2 new tests); ruff clean; mypy 29 errors in the same 4 unrelated test files as baseline; `--skill craft-voice --no-judge` eval 2/2 PASS (imaginative/year-8 + year-9-10 combos); full no-judge eval 20 cases 16 passed/4 failed — unchanged canned-fake baseline. Live LLM judge eval not run (the `.env` Kimi key returns 401 — needs a fresh credential); remains a pre-beta follow-up.
- **Next pick-up:** ISS-009 — seed imaginative outcomes + wire the imaginative daily loop.

### 2026-08-20 — ISS-007 done: imaginative reference packs for Year 8-10
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-007 (P1, dep ISS-006 DONE).
- **Shipped:** twelve imaginative packs — six pack-bearing skills (check-structure, diagnose-errors, elevate-vocabulary, give-feedback, independent-task, set-success-criteria) × `year-8` + `year-9-10`, filenames mirroring the analytical/persuasive packs. Content: narrative-arc rubric (orientation → complication → rising tension → climax → resolution; 9-10 adds structural control + tone play), error taxonomy routing plot/structure to check-structure and showing/POV to `craft-voice` (planned ISS-008, mirroring how ISS-004 pre-noted strengthen-argument), show-don't-tell upgrade tables + Tier 3 narrative metalanguage (9-10: tonal control, motif/symbolism/foreshadowing), A–E imaginative descriptors mapped to QCAA criteria + NAPLAN narrative criteria (Character & Setting!), QCAA task specs per band with copyright-safe stimulus rules (public-domain sources only for interventions/transformations), "I can…" criteria banks.
- Traceability: every pack cites `reaserch.md` (imaginative domain, Year 8 formats — short stories/narrative interventions/text transformations/memoirs/diaries; Year 9 formats — multi-text narratives/monologues/script transformations with structural experimentation/voice/POV/tone; conditions; marking criteria; NAPLAN narrative criteria) + `teacher-skills.md` (AERO). Year 10 descriptors carry Q-001 derived-not-verbatim notes. No backend source changed; analytical/persuasive packs untouched (behaviour byte-identical).
- Verified: targeted 37 passed/1 skipped; full suite **165 passed/4 skipped** (+4 new tests); ruff clean; mypy 29 errors in the same 4 unrelated test files as baseline; `python -m app.eval --no-judge` (fake) 18 cases 14 passed/4 failed — unchanged baseline. Fallback proven: exact for imaginative 8-10, nearest-band note for 11-12, instructions-only for unknown text types (no-pack test retargeted to `poetry`).
- **Next pick-up:** ISS-008 — new skill `craft-voice` (tenth skill; golden examples + diagnose-errors routing for imaginative).

### 2026-08-20 — ISS-006 done: persuasive daily loop seeded and proven
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-006 (P1, dep ISS-005 DONE).
- **Shipped:** `app/seed.py` now idempotently seeds 24 QCAA outcomes — 12 analytical (unchanged) + 12 persuasive across Year 8/9/10 (`QCAA-Y*-PER-*` codes: Year 8 hook/contention/call-to-action + develop-one-reason traced to reaserch.md Year 8 criteria + NAPLAN persuasive criteria; Year 9 escalating viewpoint/substantiating evidence/deliberate rhetoric/rebuttal traced to Year 9 criteria; Year 10 derived one band up per Q-001).
- **No loop code changed:** P6.2's `_resolve_text_type` (profile `focus_text_types[0]` wins on every stage) already wires text_type through the whole loop — the persuasive loop worked end-to-end on the first HTTP test run. Diagnosis routes to `strengthen-argument`, all pack-bearing prompts cite the persuasive/year-8 packs, 5 rubric scores persist with persuasive criterion names.
- Verified: targeted 18 passed; full suite **161 passed/4 skipped** (+2 new tests); ruff clean; mypy 29 errors in the same 4 unrelated test files as baseline. Two pre-existing seed tests now filter by text_type (year-only filtering caught the new persuasive rows).
- **Next pick-up:** ISS-007 — imaginative reference packs for Year 8-10.

### 2026-08-20 — ISS-005 done: ninth skill `strengthen-argument` shipped
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-005 (P1, dep ISS-004 DONE).
- **Shipped:** `skills/strengthen-argument/` — SKILL.md (chain-trace method: contention → reason → elaboration → evidence → link; ONE broken link per turn; model on a different topic; hand back with an "I can…" criterion), two persuasive reference packs (`argument-chains.md` × year-8/year-9-10: four break types — contention w/o reasons, reason w/o elaboration, decorative evidence, missing/token rebuttal — with priority rules + band calibration, Q-001 note for Year 10), and two golden fixtures (Year 8 speech, Year 9 letter to the editor).
- **Routing wired:** diagnose-errors SKILL.md route list + both persuasive taxonomy packs route category 2 (argument/substantiation) to `strengthen-argument`; contention/architecture stay with `check-structure`. `LOOP_STAGES` gains the skill as `coach`; skills/README.md index now lists nine skills.
- Lane discipline decision: check-structure keeps contention placement + paragraph/response skeleton; strengthen-argument owns chain logic (substantiation, load-bearing evidence, rebuttal); elevate-vocabulary keeps rhetoric/register.
- Verified: targeted 18 passed; full suite **159 passed/4 skipped** (+2 new tests); ruff clean; mypy 29 errors in the same 4 unrelated test files as baseline; `--skill strengthen-argument --no-judge` eval 2/2 PASS (persuasive/year-8 + year-9-10 combos); full no-judge eval 18 cases 14 passed/4 failed — unchanged canned-fake baseline. Live LLM judge eval not run (no credential); remains a pre-beta follow-up.
- Test-convention note: eval fixture tests that iterate "all skills" were pinned to the 8 original core skills — specialist skills (strengthen-argument now, craft-voice later) intentionally ship no analytical fixtures.
- **Next pick-up:** ISS-006 — seed persuasive outcomes + wire the persuasive daily loop.

### 2026-08-19 — ISS-004 done: persuasive reference packs for Year 8-10
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-004 (P1, dep ISS-003 DONE).
- **Shipped:** twelve persuasive packs — six pack-bearing skills (check-structure, diagnose-errors, elevate-vocabulary, give-feedback, independent-task, set-success-criteria) × `year-8` + `year-9-10`, filenames mirroring the analytical packs. Content: argument-structure rubric (contention → reason/elaboration/evidence/link, escalation + rebuttal at 9-10), error taxonomy routing to existing skills, modality ladder + audience register + Tier 3 rhetorical metalanguage (ethos/pathos/logos at 9-10), A–E persuasive descriptors mapped to QCAA criteria + NAPLAN persuasive criteria, QCAA task specs per band with copyright-safe stimulus rules, "I can…" criteria banks.
- Traceability: every pack cites `reaserch.md` (persuasive domain, Year 8/9 formats, conditions, marking criteria, NAPLAN), `teacher-skills.md` (AERO Writing Instruction Model), `Queensland English Tutoring Blueprint.md` (PEEL); Year 10 descriptors carry Q-001 derived-not-verbatim notes. No backend source changed; analytical packs untouched (behaviour byte-identical).
- Verified: targeted 32 passed/1 skipped; full suite **157 passed/4 skipped** (+4 new tests); ruff clean; mypy unchanged vs baseline; `python -m app.eval --no-judge` (fake) 16 cases 12 passed/4 failed — unchanged baseline. Fallback proven: exact for persuasive 8-10, nearest-band note for 11-12, instructions-only for imaginative.
- **Next pick-up:** ISS-005 — new skill `strengthen-argument` (ninth skill; golden examples + diagnose-errors routing for persuasive).

### 2026-08-19 — ISS-003 done: Year 9-10 analytical loop seeded and proven
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-003 (P0, dep ISS-002 DONE).
- **Shipped:** `app/seed.py` now idempotently seeds 12 QCAA analytical outcomes across three year levels — Year 8 unchanged, `YEAR_9_OUTCOMES` (QCAA-Y9-ANL-01..04: discriminating thesis, representations/reader-positioning, formal register/metalanguage, 600–800 word sustained response — traced to `reaserch.md` Year 9 marking criteria + the ISS-002 year-9-10 packs), `YEAR_10_OUTCOMES` (QCAA-Y10-ANL-01..04, derived one band up per Q-001).
- **Loop proven for year_level=9** with FakeProvider at two levels: orchestrator (`test_run_daily_loop_year_9_cites_year_9_descriptors`) and HTTP (`test_year_9_session_runs_loop_and_persists_scores`) — every pack-bearing prompt cites the year-9-10 packs (no degradation note anywhere), and 5 rubric scores persist for the graded Year 9 attempt.
- Verified: targeted 19 passed; full suite **153 passed/4 skipped** (+3); ruff clean; mypy 29 errors in 4 unrelated test files — identical to the ISS-002 baseline. Year 8 outcomes/behaviour untouched.
- **Next pick-up:** ISS-004 — persuasive reference packs for Year 8-10 (research ticket; no copyrighted set texts).

### 2026-08-19 — ISS-002 done: Year 9-10 analytical reference packs + fixtures
- Cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-002 (P0, dep ISS-001 DONE).
- **Shipped:** six `references/analytical/year-9-10/` packs (check-structure, diagnose-errors, elevate-vocabulary, give-feedback, independent-task, set-success-criteria) + one year-9-10 golden fixture per core skill (8 × sample-02/expected-02, `year_level: 9`, Macbeth thread — public domain).
- Band shifts encoded (traced to `reaserch.md`): explanation → **critical analysis** (representation/context/reader-positioning); 600–800 words / 90 min + 10 planning; formal academic register transition; higher Tier 2/3 vocabulary ceiling. Every pack carries a Q-001 provenance note: Year 10 descriptors are **derived** from Year 9 elaborations, not verbatim QCAA text.
- Executor/loader needed zero code changes — the P6.1 pack architecture picked the new packs up by convention. Tests: +3 new (year-9-10 pack loading, per-skill year-9-10 fixture coverage, exact-pack execution without degradation note); eval count/tag assertions updated 8→16; fallback-note test retargeted to year-11-12.
- Verified: targeted 61 passed/2 skipped; full suite 150 passed/4 skipped; ruff clean; mypy 29 errors in 4 unrelated test files — stash-verified identical to pre-change baseline. Year-8 prompt byte-identical regression passes (Year 8 behaviour untouched). `python -m app.eval --no-judge` (fake) runs 16 cases with per-skill `analytical/year-9-10` combo rows.
- **Next pick-up:** ISS-003 — seed Year 9-10 QCAA analytical outcomes and run a year_level=9 loop with FakeProvider.

### 2026-08-19 — ISS-001 done: eval fixture matrix (first autonomous `/develop` ticket)
- First cron `/develop` run on `feature/english-tutor-delivery`. Gate was OPEN; picked ISS-001 (P0, no deps).
- **Shipped:** a skill can now ship multiple golden fixtures as an eval matrix — `EvalCase.tags` (`text_type` + `year_band`) from fixture header, optional `year_band:` frontmatter tag (discovery metadata only, stripped from executor inputs; defaults to the band implied by `year_level` via `year_band_for`). Scorecard gained `render_combo_breakdown()`: pass/fail grouped by skill then `text_type/year_band` combo. `skills/README.md` examples convention documented.
- Existing Year 8 analytical fixtures untouched → prompts byte-identical; default tags `analytical/year-8` regression-tested.
- Verified: targeted eval tests 32 passed/1 skipped (+6 new); full suite 147 passed/4 skipped; ruff + mypy clean; `python -m app.eval --no-judge` prints the combo breakdown (2 canned-fake rule FAILs remain the expected baseline).
- **Next pick-up:** ISS-002 — Year 9-10 analytical reference packs (Q-001 NON_BLOCKING: cite research files, mark uncertain descriptors as derived).

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
- Added missing pp/__init__.py and 	ests/__init__.py to fix mypy package mapping.
- Fixed 	est_anthropic_provider_calls_sdk to use a real nthropic.types.TextBlock instance.
- Fixed pp/main.py lifespan return type for mypy (AsyncIterator[None]).
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
