# CLAUDE.md

Guidance for any Claude session working in this repository. **Read `MEMORY.md` first** — it is the source of truth for decisions, history, and the roadmap.

## What this project is

An AI-powered **after-school English tutor** for Australian secondary students (Year 8–12), built to take a student toward A+. Not a school replacement. A React web app talks to a Python (FastAPI) backend with a **swappable LLM**. MVP runs locally but is designed to scale to production.

MVP focus: **Year 8 · QCAA · analytical/essay writing**, tuned to the first student's weaknesses (flat vocabulary, weak structure). Architecture is designed for Year 8–12 + all text types; only the content depth is narrowed first. See `MEMORY.md` §2.

## Start here (read order)

1. `MEMORY.md` — vision, decision log, what's built, roadmap, open questions.
2. `MVP-Plan.md` — scope, architecture, data model, phased build plan (P0–P5).
3. `PRD.md` — user stories, daily-loop UX, North Star metric, privacy requirements.
4. `ERD.md` — data model: entities, fields, relationships, key queries.
5. `IMPLEMENTATION-PLAN.md` — the resumable, multi-session build plan. **When building, this is the working checklist** — do the first unchecked step, verify, tick it, log it.
6. `skills/README.md` — the agent-skill authoring convention and how the 8 skills compose into a session loop.

## Core idea: teaching logic lives in files, not code

The product's IP is the **agent skills** in `skills/` — portable, model-agnostic Markdown packages, not application code. The backend loads and orchestrates them; the LLM is a swappable dependency behind an adapter layer. When improving teaching quality, edit the skills; when changing models, edit config — the two must stay decoupled.

## Working conventions

- **Authoring skills:** follow `skills/README.md` exactly — required `SKILL.md` sections, a `examples/` golden fixture (sample + expected) per skill, and the six non-negotiable guardrails (coach don't ghostwrite; gradual release; curriculum-anchored; bounded feedback; age-appropriate; model-agnostic).
- **Grounding:** every pedagogical claim traces to the research files (APST / HITS / VTLM / GRR / AERO SWIF / QCAA), not intuition. Cite the source file.
- **Verification:** each skill has golden examples. Today they drive static design dry-runs; once a model is wired, the eval harness runs them for real. Add a fixture when authoring or changing a skill.
- **Keep it simple:** minimum code that solves the problem; no speculative abstractions; surgical changes; state assumptions and surface trade-offs before building.
- **Update `MEMORY.md`** whenever a decision is made, a milestone lands, or something important is discovered.

## Current status (see MEMORY.md §8 for detail)

Done: research consolidated, MVP plan, PRD + ERD, all 8 v1 skills with golden examples, static dry-run, MVP model chosen (Claude Sonnet 4.6, adapter-swappable).
Next: **P0** — project scaffolding + LLM adapter layer (default provider Anthropic/Sonnet) + skill loader. All gating decisions resolved.

## Reference material

| File | Use it for |
|---|---|
| `reaserch.md` | QCAA Year 8/9 curriculum, pedagogy, assessment conditions, A–E standards. |
| `Queensland English Tutoring Blueprint.md` | Deep competency framework: AERO SWIF, GRR, PEEL/TEEL, QAR, Tier vocabulary, cognitive science. |
| `teacher-skills.md` | Evidence-based teacher skills (APST/HITS/VTLM) mapped to agent skills. |
| `test-context.md` | NSW NESA assessment context — for extending beyond Queensland later. |
| `English Circulum.md` | Curriculum reference. |

## Things to get right

- Coach, never ghostwrite. Skills hand work back to the student.
- Bounded feedback: surface the 1–2 highest-leverage next steps, never a laundry list.
- Copyright: never embed copyrighted set texts as stimulus; use public-domain or generated material.
- Respect the design-vs-delivery scope split — build the doors for 8–12/all types, fill Year 8 analytical depth first.
