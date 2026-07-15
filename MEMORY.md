# English Tutor — Project Memory

> Long-term memory for this project. It records the vision, every meaningful decision (with dates and rationale), what's been built, the roadmap, and open questions. **Update this file whenever a decision is made, a milestone is hit, or something important is discovered — and append a dated entry to the Session log (§11) at the end of each working session.** New sessions should read this first.

Last updated: 2026-07-13

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
- **LLM adapter layer:** unified `LLMProvider` interface + per-provider adapters (Anthropic / OpenAI / local Ollama), provider chosen by config. Swapping models must not touch business logic. (This is the "flexibility to change LLM" requirement.)
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

## 8. Milestones / roadmap

**Done**
- ✅ Research consolidated (QCAA curriculum, teacher skills, assessment context).
- ✅ MVP scope + architecture plan (`MVP-Plan.md`).
- ✅ 8 v1 agent skills authored with golden examples (`skills/`).
- ✅ Static design dry-run of all skills against samples.

**Next (model chosen: Claude Sonnet 4.6 — P0 unblocked)**
- ⬜ P0 — project scaffolding + LLM adapter layer (default provider: Anthropic/Sonnet) + skill loader.
- ⬜ Eval harness — run each SKILL.md through the model against `examples/`, score vs expected (turns dry-run into automated verification).
- ⬜ P1 — curriculum + rubric data model (Year 8 first).
- ⬜ P2 — daily loop orchestration (compose the skills end to end).
- ⬜ P3 — feedback engine tuned to structure + vocabulary.
- ⬜ P4 — React UI for the daily loop.
- ⬜ P5 — interaction logging + eval regression set.

**Later**
- ⬜ Extend skill depth to Years 9–12 and persuasive/imaginative.
- ⬜ Fill remaining skills: `fix-mechanics`; spaced-review / retrieval; metacognition coaching.
- ⬜ Beta: motivation layer, parent layer. GA: multi-tenant, Postgres, deploy.

## 9. Open questions

- ~~Which LLM for MVP?~~ **Resolved 2026-07-10: single cloud Claude Sonnet 4.6, adapter-swappable.** (see §7)
- User login for MVP? (Single-user can skip; schema still reserves it.)
- Source for structured QCAA outcome data (research files already have a lot to extract).

## 10. File index

| Path | What |
|---|---|
| `CLAUDE.md` | Entry point for any session — read first. |
| `MEMORY.md` | This file — decisions, history, roadmap. |
| `MVP-Plan.md` | MVP scope, architecture, data model, phased build plan. |
| `IMPLEMENTATION-PLAN.md` | Resumable multi-session build checklist (~20 steps, 6 milestones). The working to-do when building. |
| `PRD.md` | User stories, daily-loop UX, North Star metric, non-functional (privacy) requirements. |
| `ERD.md` | Data model: entities, fields, relationships (Mermaid), key queries, privacy/retention. |
| `skills/README.md` | Skill authoring convention + skill index + loop composition. |
| `skills/<name>/` | The 8 v1 agent skills (SKILL.md + reference + examples). |
| `reaserch.md` | QCAA Year 8/9 curriculum, pedagogy, assessment conditions, A–E standards. |
| `Queensland English Tutoring Blueprint.md` | Deep competency framework: AERO SWIF, GRR, PEEL/TEEL, QAR, Tier vocab, cognitive science. |
| `teacher-skills.md` | Evidence-based teacher skills (APST/HITS/VTLM) → agent-skill mapping. |
| `test-context.md` | NSW NESA assessment context (Years 8–12) — useful when extending beyond QLD. |
| `English Circulum.md` | Curriculum reference. |

## 11. Session log

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
