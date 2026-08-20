# Delivery Backlog

This document is the canonical delivery state for autonomous development. Detailed issue blocks are authoritative; the index is a convenience summary.

## Delivery Gate
- State: `OPEN`
- Blocking questions: `None`
- Reason: No `BLOCKING` questions are open; completed P0-P5/P6.1/P6.2 work is recorded as context only, not as tickets.
- Active issue: `None`
- Integration mode: `delivery-branch`
- Delivery branch: `feature/english-tutor-delivery`
- Last evaluated: `2026-08-20T10:30:00+10:00`

## Automation Policy
- `/develop` processes at most one issue per run.
- A `BLOCKED`, `PAUSED`, or `COMPLETE` delivery gate means no implementation work.
- Only a `READY` issue with all dependencies `DONE` and `Blocked by: None` is eligible.
- At most one issue may have `Status: IN_PROGRESS`.
- `delivery-branch` keeps sequential work on the recorded feature branch; it never merges into `main`.

## Completed Context (Not Tickets)
- P0-P5 from `IMPLEMENTATION-PLAN.md` are complete and are intentionally not converted into `ISS-*` tickets.
- Phase 2 `6.1 Reference-pack architecture` and `6.2 Student profile + session context` are complete and are intentionally not converted into `ISS-*` tickets.
- Completed work remains visible in `MEMORY.md`, `IMPLEMENTATION-PLAN.md`, and `IMPLEMENTATION-PLAN-2.md`; this backlog starts at the next unchecked executable step.

## Status Reference
| State | Meaning |
|---|---|
| `DRAFT` | Needs planning detail. |
| `READY` | Fully specified and awaiting eligible execution. |
| `IN_PROGRESS` | Sole active implementation. |
| `BLOCKED` | Waiting on a linked question. |
| `DONE` | Verified completion evidence recorded. |
| `CANCELLED` | Deliberately abandoned with reason. |

## Issue Index
| ID | Title | Status | Priority | Depends on | Blocked by |
|---|---|---|---|---|---|
| ISS-001 | Eval fixture matrix by year band and text type | `DONE` | `P0` | `None` | `None` |
| ISS-002 | Year 9-10 analytical reference packs | `DONE` | `P0` | `ISS-001` | `None` |
| ISS-003 | Seed and evaluate Year 9-10 analytical loop | `DONE` | `P0` | `ISS-002` | `None` |
| ISS-004 | Persuasive reference packs for Year 8-10 | `DONE` | `P1` | `ISS-003` | `None` |
| ISS-005 | New skill strengthen-argument | `DONE` | `P1` | `ISS-004` | `None` |
| ISS-006 | Seed and wire persuasive daily loop | `DONE` | `P1` | `ISS-005` | `None` |
| ISS-007 | Imaginative reference packs for Year 8-10 | `DONE` | `P1` | `ISS-006` | `None` |
| ISS-008 | New skill craft-voice | `DONE` | `P1` | `ISS-007` | `None` |
| ISS-009 | Seed and wire imaginative daily loop | `DONE` | `P1` | `ISS-008` | `None` |
| ISS-010 | Beta first-run wizard and profile UX | `READY` | `P1` | `ISS-009` | `None` |
| ISS-011 | Student data export and restore | `READY` | `P1` | `ISS-010` | `None` |
| ISS-012 | New skill baseline-assessment | `READY` | `P1` | `ISS-011` | `None` |
| ISS-013 | New skill fix-mechanics | `READY` | `P1` | `ISS-012` | `None` |
| ISS-014 | New skill spaced-review and retrieval stage | `READY` | `P1` | `ISS-013` | `None` |
| ISS-015 | Weekly timed mock mode | `READY` | `P1` | `ISS-014` | `None` |
| ISS-016 | Streaks and weekly goal | `READY` | `P2` | `ISS-015` | `None` |
| ISS-017 | Criterion level-up celebration | `READY` | `P2` | `ISS-016` | `None` |
| ISS-018 | Coach persona tone setting | `READY` | `P2` | `ISS-017` | `None` |
| ISS-019 | Weekly parent report with privacy boundary | `READY` | `P2` | `ISS-018` | `None` |
| ISS-020 | Shared parent-student goal setting | `READY` | `P2` | `ISS-019` | `None` |
| ISS-021 | Per-stage model routing | `READY` | `P2` | `ISS-020` | `None` |
| ISS-022 | Privacy-safe telemetry and feedback package | `READY` | `P2` | `ISS-021` | `None` |
| ISS-023 | Beta handbook | `READY` | `P2` | `ISS-022` | `None` |
| ISS-024 | QCE senior instrument modelling | `READY` | `P2` | `ISS-023` | `None` |
| ISS-025 | Senior IA1 analytical pack | `READY` | `P2` | `ISS-024` | `None` |

## Issues

## ISS-001 - Eval fixture matrix by year band and text type
- Status: `DONE`
- Priority: `P0`
- Type: `chore`
- Depends on: `None`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 6.3; PRD: §5 North Star metric; ERD: Key queries/Replay-eval`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-19T16:08:19+10:00`
- Completed: `2026-08-19T16:17:19+10:00`
- Commit: `9aa7c77`

### Outcome and scope
Extend the eval harness so one skill can ship multiple golden fixtures tagged by year band and text type, and the scorecard groups results by combo.

### Acceptance criteria
- [x] A skill can provide multiple fixtures with band/text_type frontmatter.
- [x] Scorecard output groups pass/fail results by skill and by band/text_type combo.
- [x] Existing Year 8 analytical fixtures still run unchanged.

### Implementation notes
- Likely files or components: backend/app/eval/fixtures.py, backend/app/eval/runner.py, backend/app/eval/scorecard.py, skills/*/examples/.
- Constraints: preserve current fixture discovery behaviour for untagged Year 8 analytical examples; no live LLM required for plumbing tests.

### Verification
- [x] `cd backend && uv run pytest tests/test_eval_fixtures.py tests/test_eval_runner.py tests/test_eval_rules.py` — 32 passed, 1 skipped.
- [x] `cd backend && uv run python -m app.eval --no-judge` — 8 cases run; scorecard prints per-skill combo breakdown; exit 1 on canned fake failures (expected baseline, unchanged).

### Completion evidence
- `EvalCase.tags` (`text_type` + `year_band`) populated in `discover_cases`; optional `year_band:` header line is a discovery tag stripped from executor inputs (never reaches the prompt); band falls back to `year_band_for(year_level)`. `CaseResult` carries the combo; `render_combo_breakdown()` groups pass/fail by skill then `text_type/year_band`. 6 new tests (3 fixture-discovery incl. a tmp 2-fixture/different-band skill, 1 scorecard grouping, 1 runner tag propagation, 1 default-tags regression). Full suite: 147 passed, 4 skipped; ruff + mypy clean. No real fixture files touched, so Year 8 analytical prompts/behaviour are byte-identical.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 6.3; PRD: §5 North Star metric; ERD: Key queries/Replay-eval` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-19T16:08:19+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-19T16:17:19+10:00 - DONE. Eval fixture matrix shipped: multiple tagged fixtures per skill + scorecard combo breakdown. Verification: targeted eval tests 32 passed/1 skipped; full suite 147 passed/4 skipped; ruff/mypy clean; `python -m app.eval --no-judge` runs and groups by combo. Unlocks ISS-002.

## ISS-002 - Year 9-10 analytical reference packs
- Status: `DONE`
- Priority: `P0`
- Type: `research`
- Depends on: `ISS-001`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 9.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-19T18:26:00+10:00`
- Completed: `2026-08-19T18:40:46+10:00`
- Commit: `4f4d6a8`

### Outcome and scope
Add analytical reference packs for year-9-10 across the existing skills, with band-adjusted rubric descriptors, vocabulary ceilings, task specs, and register transition.

### Acceptance criteria
- [x] references/analytical/year-9-10/ exists for the relevant skills.
- [x] Pack content traces to research files rather than intuition.
- [x] Each core skill gains at least one year-9-10 golden fixture.

### Implementation notes
- Likely files or components: skills/*/references/analytical/year-9-10/, skills/*/examples/, reaserch.md, Queensland English Tutoring Blueprint.md.
- Constraints: keep skills generic; content depth lives in reference packs; do not change Year 8 analytical behaviour.

### Verification
- [x] `cd backend && uv run pytest tests/test_skill_loader.py tests/test_skill_executor.py` — pass (part of 61 passed, 2 skipped across the loader/executor/eval files).
- [x] `cd backend && uv run python -m app.eval --no-judge` — with `LLM_PROVIDER=fake`: 16 cases, 12 passed / 4 failed (canned-fake rule failures on give-feedback + diagnose-errors, the expected no-judge baseline); combo breakdown prints `analytical/year-9-10` per skill; exit 1 as expected.

### Completion evidence
- Six year-9-10 packs authored: `check-structure/rubric.md`, `diagnose-errors/taxonomy.md`, `elevate-vocabulary/tiers.md`, `give-feedback/rubric.md`, `independent-task/task-specs.md`, `set-success-criteria/criteria-bank.md`. Every pack cites `reaserch.md` sections (Year 9 assessment conditions, Year 9 A–E elaborations, analytical-essay objectives) and carries a Q-001 provenance note marking Year 10 descriptors as derived, not verbatim. Band shifts encoded: explanation → critical analysis (representation/context/positioning), 600–800 words / 90 min + 10 planning, formal register transition, higher Tier 2/3 ceiling.
- Eight year-9-10 golden fixtures (sample-02/expected-02, `year_level: 9`, analytical, Macbeth thread — public domain) — one per core skill; discovered by the harness as combo `analytical/year-9-10`.
- Tests: new `test_reference_files_load_into_analytical_year_9_10_pack`, `test_each_core_skill_has_a_year_9_10_analytical_fixture`, `test_execute_year_9_10_uses_exact_pack_without_degradation_note`; updated count/tag assertions in eval fixtures/runner tests; fallback-note test retargeted to year-11-12 (year-9-10 now has an exact pack). Full suite 150 passed, 4 skipped; ruff clean; mypy 29 errors in 4 unrelated test files — byte-identical to the pre-change baseline (stash-verified), changed files clean. Year-8 prompt byte-identical regression passes — Year 8 behaviour unchanged.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 9.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-19T18:26:00+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-19T18:40:46+10:00 - DONE. Year 9-10 analytical reference packs shipped for all six pack-bearing skills + one year-9-10 golden fixture per core skill (8 fixtures, Macbeth thread). Content traces to reaserch.md with Q-001 derived-not-verbatim notes for Year 10. Verification: targeted loader/executor/eval tests 61 passed/2 skipped; full suite 150 passed/4 skipped; ruff clean; mypy unchanged vs baseline; `python -m app.eval --no-judge` (fake) 16 cases with per-skill `analytical/year-9-10` combo rows. Unlocks ISS-003.

## ISS-003 - Seed and evaluate Year 9-10 analytical loop
- Status: `DONE`
- Priority: `P0`
- Type: `feature`
- Depends on: `ISS-002`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 9.2; PRD: §5 North Star metric; ERD: curriculum_outcome/rubric_score`
- Effort: `S`
- Attempt: `1`
- Started: `2026-08-19T20:46:51+10:00`
- Completed: `2026-08-19T20:59:00+10:00`
- Commit: `25aee22`

### Outcome and scope
Seed Year 9-10 QCAA analytical outcomes and prove a year_level=9 session can run the loop with Year 9 descriptors cited in feedback.

### Acceptance criteria
- [x] Year 9-10 QCAA analytical outcomes are seeded idempotently.
- [x] A year_level=9 analytical session runs end-to-end with FakeProvider in tests.
- [x] Rubric scores persist for a graded Year 9 attempt.

### Implementation notes
- Likely files or components: backend/app/seed.py, backend/seed.py, backend/tests/test_seed.py, backend/tests/test_session_orchestrator.py, backend/tests/test_api_daily_loop.py.
- Constraints: keep seed idempotent; do not broaden to persuasive/imaginative yet.

### Verification
- [x] `cd backend && uv run pytest tests/test_seed.py tests/test_session_orchestrator.py tests/test_api_daily_loop.py` — 19 passed.
- [x] `cd backend && uv run pytest` — 153 passed, 4 skipped (was 150/4; +3 new tests).

### Completion evidence
- `app/seed.py` generalised to seed three outcome sets idempotently: `YEAR_8_OUTCOMES` (unchanged), `YEAR_9_OUTCOMES` (QCAA-Y9-ANL-01..04, traced to reaserch.md Year 9 marking criteria + the ISS-002 year-9-10 packs: discriminating thesis, representations/reader-positioning, formal register/metalanguage, 600–800 word sustained response), `YEAR_10_OUTCOMES` (QCAA-Y10-ANL-01..04, derived one band up per Q-001 provenance note). `backend/seed.py` print updated; analytical only, persuasive/imaginative untouched.
- Tests: `test_seed.py` rewritten (+2 tests: year-9-10 creation incl. band-shift descriptor assertion, idempotency extended to all 12 outcomes); `test_session_orchestrator.py::test_run_daily_loop_year_9_cites_year_9_descriptors` — full year_level=9 loop with FakeProvider, asserts every pack-bearing prompt (criteria/independent/diagnosis/coach/feedback) cites the year-9-10 packs ("Year 9", give-feedback carries "discriminating thesis"), no degradation note on any tutor turn, 5 rubric scores persisted; `test_api_daily_loop.py::test_year_9_session_runs_loop_and_persists_scores` — HTTP-level loop for a year-9 student profile, scores persisted and surfaced in the feedback body.
- Full suite 153 passed/4 skipped; ruff check clean; mypy 29 errors in 4 unrelated test files — identical to the ISS-002 baseline, changed files clean. One new mypy error in test_seed.py (Sequence `+`) found and fixed during the run.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 9.2; PRD: §5 North Star metric; ERD: curriculum_outcome/rubric_score` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-19T20:46:51+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-19T20:59:00+10:00 - DONE. Year 9-10 QCAA analytical outcomes seeded idempotently (12 outcomes across Year 8/9/10); year_level=9 loop proven end-to-end with FakeProvider at orchestrator and HTTP level, with year-9-10 packs cited in prompts and 5 rubric scores persisted. Verification: targeted 19 passed; full suite 153 passed/4 skipped; ruff clean; mypy unchanged vs baseline. Unlocks ISS-004.

## ISS-004 - Persuasive reference packs for Year 8-10
- Status: `DONE`
- Priority: `P1`
- Type: `research`
- Depends on: `ISS-003`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 7.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-19T22:59:00+10:00`
- Completed: `2026-08-19T23:20:00+10:00`
- Commit: `3695649`

### Outcome and scope
Create persuasive reference packs covering argument structure, rhetorical devices by band, QCAA persuasive A-E descriptors, and task specs.

### Acceptance criteria
- [x] Persuasive packs exist for the relevant skills and year bands.
- [x] Every pedagogical claim traces to a research source file.
- [x] Pack selection falls back safely when an exact combo is missing.

### Implementation notes
- Likely files or components: skills/*/references/persuasive/, reaserch.md, Queensland English Tutoring Blueprint.md, backend/app/skills/executor.py.
- Constraints: no copyrighted set texts; use public-domain or generated stimulus only.

### Verification
- [x] `cd backend && uv run pytest tests/test_skill_loader.py tests/test_skill_executor.py` — 32 passed, 1 skipped.
- [x] `cd backend && LLM_PROVIDER=fake uv run python -m app.eval --no-judge` — 16 cases, 12 passed / 4 failed (canned-fake rule failures on give-feedback + diagnose-errors, the expected no-judge baseline, unchanged); exit 1 as expected.
- [x] `cd backend && uv run pytest` — 157 passed, 4 skipped (was 153/4; +4 new tests).
- [x] `cd backend && uv run ruff check .` — clean; `uv run mypy app tests` — 29 errors in 4 unrelated test files, identical to the ISS-003 baseline; changed files clean.

### Completion evidence
- Twelve persuasive packs authored (six pack-bearing skills × `year-8` + `year-9-10`), filenames mirroring the analytical packs: `check-structure/rubric.md` (argument-structure rubric: contention, reason/elaboration/evidence/link, response architecture, rebuttal at 9-10), `diagnose-errors/taxonomy.md` (six leverage-ordered categories routing to existing skills; strengthen-argument noted as planned ISS-005), `elevate-vocabulary/tiers.md` (modality ladder, audience register, Tier 3 rhetorical metalanguage incl. ethos/pathos/logos at 9-10), `give-feedback/rubric.md` (A–E persuasive descriptors mapped to QCAA criteria + NAPLAN persuasive criteria), `independent-task/task-specs.md` (QCAA conditions, approved persuasive formats per band, copyright-safe stimulus rules), `set-success-criteria/criteria-bank.md` ("I can…" banks + learning-intention stems).
- Traceability: every pack cites `reaserch.md` sections (persuasive domain "arguments, rhetoric, and evidence to sway an audience"; Year 8 formats — speeches/vlogs adapting voice to formal/informal audiences; Year 9 formats — feature articles, letters to the editor, campaign pitches, formal reviews with rhetorical strategies and evidence; assessment conditions; marking criteria; NAPLAN persuasive criteria) plus `teacher-skills.md` (AERO Writing Instruction Model) and `Queensland English Tutoring Blueprint.md` (PEEL). Year 10 descriptors carry Q-001 derived-not-verbatim provenance notes.
- Fallback proven by tests: `persuasive/year-8` and `persuasive/year-9-10` resolve exactly (no degradation note); `persuasive/year-11-12` falls back to `persuasive/year-8` with the nearest-band note; `imaginative/year-8` still falls back to skill instructions only. Tests: `test_reference_files_load_into_persuasive_year_8_pack`, `test_reference_files_load_into_persuasive_year_9_10_pack`, updated `test_select_packs_prefers_exact_then_nearest_band`, new `test_execute_persuasive_year_9_uses_exact_pack_without_degradation_note`, new `test_execute_appends_degradation_note_on_persuasive_band_fallback`, `test_execute_without_matching_pack_returns_response_with_note` retargeted to imaginative. No backend source changed; analytical packs untouched, so analytical behaviour is byte-identical.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 7.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-19T22:59:00+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-19T23:20:00+10:00 - DONE. Persuasive reference packs shipped for all six pack-bearing skills across year-8 and year-9-10 (12 packs), traced to reaserch.md/teacher-skills.md/Blueprint with Q-001 provenance notes; safe fallback proven (exact for 8-10, nearest-band note for 11-12, instructions-only for imaginative). Verification: targeted 32 passed/1 skipped; full suite 157 passed/4 skipped; ruff clean; mypy unchanged vs baseline; `python -m app.eval --no-judge` (fake) 16 cases, 12 passed/4 failed — unchanged baseline. Unlocks ISS-005.

## ISS-005 - New skill strengthen-argument
- Status: `DONE`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-004`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 7.2; PRD: §3 bounded feedback; ERD: skill registry`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-20T00:10:00+10:00`
- Completed: `2026-08-20T00:40:00+10:00`
- Commit: `2bb9791`

### Outcome and scope
Add the ninth agent skill strengthen-argument to diagnose weak argument chains and coach the fix within the global guardrails.

### Acceptance criteria
- [x] skills/strengthen-argument/ follows skills/README.md convention.
- [x] Golden examples exist and are discovered by the eval harness.
- [x] diagnose-errors can route persuasive submissions to strengthen-argument.

### Implementation notes
- Likely files or components: skills/strengthen-argument/, backend/app/skills/router.py, backend/tests/test_diagnosis_router.py, backend/tests/test_skill_sync.py.
- Constraints: coach do not ghostwrite; bounded feedback max 1-2 next steps; model-agnostic skill package.

### Verification
- [x] `cd backend && uv run pytest tests/test_diagnosis_router.py tests/test_skill_loader.py tests/test_skill_sync.py` — 18 passed.
- [x] `cd backend && uv run python -m app.eval --skill strengthen-argument --no-judge` — 2 cases, 2 passed (persuasive/year-8 + persuasive/year-9-10 combo rows).
- [x] `cd backend && uv run pytest` — 159 passed, 4 skipped (was 157/4; +2 new tests).
- [x] `cd backend && uv run ruff check .` — clean; `uv run mypy app tests` — 29 errors in the same 4 unrelated test files as the ISS-004 baseline (test_config, test_delete_student, test_interaction_log, test_session_time); changed files clean.
- [x] `cd backend && LLM_PROVIDER=fake uv run python -m app.eval --no-judge` — 18 cases, 14 passed / 4 failed (the same canned-fake give-feedback + diagnose-errors baseline as ISS-004); strengthen-argument 2/2 PASS.

### Completion evidence
- `skills/strengthen-argument/` authored per the convention: SKILL.md with all 8 required sections (chain-trace method: contention → reason → elaboration → evidence → link, one broken link per turn, model on a different topic, hand back with an "I can…" criterion); two reference packs (`references/persuasive/year-8/argument-chains.md`, `references/persuasive/year-9-10/argument-chains.md`) encoding the four break types (contention w/o reasons, reason w/o elaboration, decorative evidence, missing/token rebuttal) with priority rules and band calibration, traced to reaserch.md (persuasive domain, Year 8/9 formats, marking criteria, A–E elaborations), Blueprint (PEEL), teacher-skills.md (AERO); Year 10 carries the Q-001 derived-not-verbatim note.
- Two golden fixtures: sample-01 (Year 8 speech — asserted reasons + "everyone knows" decorative evidence; no rebuttal demanded) and sample-02 (Year 9 letter to the editor — "research shows" not load-bearing + strawman dismissal where the task invites opposition), discovered as persuasive/year-8 and persuasive/year-9-10.
- Routing wired: diagnose-errors SKILL.md route list + both persuasive taxonomy packs now route category 2 (argument/evidence, argument/substantiation) to `strengthen-argument` (contention/architecture stay with check-structure; "planned ISS-005" notes removed). `LOOP_STAGES` gains `strengthen-argument: coach`; skills/README.md index updated (nine skills).
- Tests: new `test_strengthen_argument_loads_persuasive_packs_and_examples`, new `test_diagnosis_router_routes_persuasive_to_strengthen_argument` (dispatch + persuasive year-8 pack in the coaching prompt); count updates (8→9 skills, 16→18 cases) in loader/sync/eval tests; two fixture tests pinned to the 8 original core skills (specialist skills intentionally ship no analytical fixtures).
- Live LLM judge eval was not run (no API credential in this environment); the historical "live eval PASS" line in IMPLEMENTATION-PLAN-2 7.2 remains a pre-beta follow-up, while this ticket's declared verification is the no-judge harness above.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 7.2; PRD: §3 bounded feedback; ERD: skill registry` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-20T00:10:00+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-20T00:40:00+10:00 - DONE. Ninth skill strengthen-argument shipped: SKILL.md + two persuasive argument-chain packs (year-8, year-9-10) + two golden fixtures; diagnose-errors persuasive taxonomies route argument/substantiation to it. Verification: targeted 18 passed; full suite 159 passed/4 skipped; ruff clean; mypy unchanged vs baseline; skill eval 2/2 PASS; full no-judge eval 18 cases, 14 passed/4 failed — unchanged canned-fake baseline. Unlocks ISS-006.

## ISS-006 - Seed and wire persuasive daily loop
- Status: `DONE`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-005`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 7.3; PRD: §4 daily-loop UX; ERD: session/attempt/rubric_score`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-20T03:33:08+10:00`
- Completed: `2026-08-20T03:39:21+10:00`
- Commit: `90cb2e7`

### Outcome and scope
Seed persuasive outcomes and run the full daily loop with text_type=persuasive, persisting rubric scores.

### Acceptance criteria
- [x] Persuasive curriculum outcomes are seeded idempotently.
- [x] A persuasive session can start, advance, submit, and receive feedback over HTTP.
- [x] Rubric scores persist for a persuasive graded attempt.

### Implementation notes
- Likely files or components: backend/app/seed.py, backend/app/sessions/interactive.py, backend/app/api/routes.py, backend/tests/test_api_daily_loop.py.
- Constraints: keep analytical Year 8 loop unchanged; unsupported combos fail clearly.

### Verification
- [x] `cd backend && uv run pytest tests/test_seed.py tests/test_api_daily_loop.py` — 18 passed.
- [x] `cd backend && uv run pytest` — 161 passed, 4 skipped (was 159/4; +2 new tests).
- [x] `cd backend && uv run ruff check .` — clean; `uv run mypy app tests` — 29 errors in the same 4 unrelated test files as the ISS-005 baseline (test_config, test_delete_student, test_interaction_log, test_session_time); changed files clean.

### Completion evidence
- `app/seed.py` generalised from analytical-only to `(year_level, text_type, outcomes)` triples: the three analytical sets are unchanged (codes/descriptors byte-identical), and three persuasive sets are seeded idempotently — `YEAR_8_PERSUASIVE_OUTCOMES` (QCAA-Y8-PER-01..04: hook/contention/one-reason-per-paragraph/call-to-action, develop-one-reason with support, audience-adapted voice, sustained position — traced to reaserch.md Year 8 marking criteria + NAPLAN persuasive criteria + the ISS-004 year-8 criteria bank), `YEAR_9_PERSUASIVE_OUTCOMES` (QCAA-Y9-PER-01..04: escalating viewpoint, substantiating evidence, deliberate rhetoric/format-fit voice, counterargument + rebuttal — traced to reaserch.md Year 9 marking criteria + the year-9-10 criteria bank), `YEAR_10_PERSUASIVE_OUTCOMES` (QCAA-Y10-PER-01..04, derived one band up per Q-001). `backend/seed.py` print updated.
- No loop code changed: `InteractiveLoop._resolve_text_type` already resolves `focus_text_types[0]` on every stage (P6.2), so a student with `focus_text_types=["persuasive"]` runs the persuasive loop end-to-end today — proven by the new HTTP test.
- Tests: new `test_seed_creates_persuasive_outcomes` (12 persuasive rows across Year 8-10, codes/curriculum, Year 8-9 band-shift descriptors, analytical sets untouched); two pre-existing seed tests now filter by `text_type="analytical"` (year-only filtering matched the new persuasive rows); new `test_persuasive_session_runs_loop_and_persists_scores` — full loop over HTTP with FakeProvider: diagnosis routes to `strengthen-argument`, 5 rubric scores persist with persuasive criterion names (Position & ideas C, Argument & evidence D), every pack-bearing prompt (criteria/independent/diagnosis/coach/feedback) cites the persuasive/year-8 packs, feedback prompt carries "Position & ideas", no degradation note on any tutor turn.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 7.3; PRD: §4 daily-loop UX; ERD: session/attempt/rubric_score` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-20T03:33:08+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-20T03:39:21+10:00 - DONE. Persuasive outcomes seeded idempotently (12 outcomes across Year 8/9/10, QCAA-Y*-PER-* codes, traced to reaserch.md + ISS-004 packs, Q-001 derived note for Year 10); persuasive daily loop proven over HTTP with FakeProvider — strengthen-argument routing, persuasive pack citations on all pack-bearing prompts, 5 rubric scores persisted. Verification: targeted 18 passed; full suite 161 passed/4 skipped; ruff clean; mypy unchanged vs baseline. Unlocks ISS-007.

## ISS-007 - Imaginative reference packs for Year 8-10
- Status: `DONE`
- Priority: `P1`
- Type: `research`
- Depends on: `ISS-006`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 8.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-20T05:50:00+10:00`
- Completed: `2026-08-20T06:10:00+10:00`
- Commit: `0ff1be9`

### Outcome and scope
Create imaginative reference packs for narrative structure, character/setting/POV, show-don't-tell, sensory imagery, and QCAA imaginative descriptors.

### Acceptance criteria
- [x] Imaginative packs exist for the relevant skills and year bands.
- [x] Every pedagogical claim traces to a research source file.
- [x] Pack selection falls back safely when an exact combo is missing.

### Implementation notes
- Likely files or components: skills/*/references/imaginative/, reaserch.md, Queensland English Tutoring Blueprint.md, backend/app/skills/executor.py.
- Constraints: age-appropriate and curriculum-anchored; no ghostwritten story output as the teaching result.

### Verification
- [x] `cd backend && uv run pytest tests/test_skill_loader.py tests/test_skill_executor.py` — 37 passed, 1 skipped.
- [x] `cd backend && LLM_PROVIDER=fake uv run python -m app.eval --no-judge` — 18 cases, 14 passed / 4 failed (the same canned-fake give-feedback + diagnose-errors baseline as ISS-004/005, unchanged); exit 1 as expected.
- [x] `cd backend && uv run pytest` — 165 passed, 4 skipped (was 161/4; +4 new tests).
- [x] `cd backend && uv run ruff check .` — clean; `uv run mypy app tests` — 29 errors in the same 4 unrelated test files as the ISS-006 baseline (test_config, test_delete_student, test_interaction_log, test_session_time); changed files clean.

### Completion evidence
- Twelve imaginative packs authored (six pack-bearing skills × `year-8` + `year-9-10`), filenames mirroring the analytical/persuasive packs: `check-structure/rubric.md` (narrative-arc rubric: orientation, complication, rising tension, climax, resolution; 9-10 adds structural control + tone), `diagnose-errors/taxonomy.md` (six leverage-ordered categories routing plot/structure to check-structure, showing/POV to craft-voice (planned ISS-008), vocabulary to elevate-vocabulary), `elevate-vocabulary/tiers.md` (show-don't-tell upgrade table, Tier 3 narrative metalanguage; 9-10 shifts to tonal control + motif/symbolism/foreshadowing), `give-feedback/rubric.md` (A–E imaginative descriptors mapped to QCAA criteria + NAPLAN narrative criteria — Audience, Text Structure, Ideas, Character & Setting, Vocabulary, Cohesion), `independent-task/task-specs.md` (QCAA conditions, approved imaginative formats per band, copyright-safe stimulus rules — public-domain sources only for interventions/transformations), `set-success-criteria/criteria-bank.md` ("I can…" banks + learning-intention stems).
- Traceability: every pack cites `reaserch.md` sections (imaginative domain "conveys meaning and perspectives through narrative structure"; Year 8 formats — short stories, narrative interventions, text transformations, memoirs, diaries; Year 9 formats — multi-text narratives, serialized vlogs, script transformations, monologues, digital stories with structural experimentation/voice/POV/tone play; assessment conditions; marking criteria; NAPLAN narrative criteria) plus `teacher-skills.md` (AERO Writing Instruction Model). Year 10 descriptors carry Q-001 derived-not-verbatim provenance notes.
- Fallback proven by tests: `imaginative/year-8` and `imaginative/year-9-10` resolve exactly (no degradation note); `imaginative/year-11-12` falls back to `imaginative/year-8` with the nearest-band note; an unknown text type (`poetry`) still degrades to skill instructions only. Tests: new `test_reference_files_load_into_imaginative_year_8_pack`, `test_reference_files_load_into_imaginative_year_9_10_pack`, new `test_execute_imaginative_year_9_uses_exact_pack_without_degradation_note`, new `test_execute_appends_degradation_note_on_imaginative_band_fallback`; updated `test_select_packs_prefers_exact_then_nearest_band` (imaginative exact + fallback, no-pack case retargeted to `poetry`); `test_execute_without_matching_pack_returns_response_with_note` retargeted to `poetry`. No backend source changed; analytical/persuasive packs untouched, so existing loop behaviour is byte-identical (year-8 analytical byte-identical regression test passes).
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 8.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-20T05:50:00+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-20T06:10:00+10:00 - DONE. Imaginative reference packs shipped for all six pack-bearing skills across year-8 and year-9-10 (12 packs), traced to reaserch.md/teacher-skills.md with Q-001 provenance notes; safe fallback proven (exact for 8-10, nearest-band note for 11-12, instructions-only for unknown text types). Verification: targeted 37 passed/1 skipped; full suite 165 passed/4 skipped; ruff clean; mypy unchanged vs baseline; `python -m app.eval --no-judge` (fake) 18 cases, 14 passed/4 failed — unchanged baseline. Unlocks ISS-008.

## ISS-008 - New skill craft-voice
- Status: `DONE`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-007`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 8.2; PRD: §3 bounded feedback; ERD: skill registry`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-20T08:00:00+10:00`
- Completed: `2026-08-20T08:15:00+10:00`
- Commit: `530b4fa`

### Outcome and scope
Add the tenth agent skill craft-voice to diagnose telling-vs-showing, thin imagery, and POV drift, then coach the fix.

### Acceptance criteria
- [x] skills/craft-voice/ follows skills/README.md convention.
- [x] Golden examples exist and are discovered by the eval harness.
- [x] diagnose-errors can route imaginative submissions to craft-voice.

### Implementation notes
- Likely files or components: skills/craft-voice/, backend/app/skills/router.py, backend/tests/test_diagnosis_router.py, backend/tests/test_skill_sync.py.
- Constraints: coach do not ghostwrite; bounded feedback max 1-2 next steps; model-agnostic skill package.

### Verification
- [x] `cd backend && uv run pytest tests/test_diagnosis_router.py tests/test_skill_loader.py tests/test_skill_sync.py` — 22 passed.
- [x] `cd backend && LLM_PROVIDER=fake uv run python -m app.eval --skill craft-voice --no-judge` — 2 cases, 2 passed (imaginative/year-8 + imaginative/year-9-10 combo rows).

### Completion evidence
- `skills/craft-voice/` authored per the convention: SKILL.md with all 8 required sections (three craft dials — key moment shown/told, emotion shown/named, narrator steady/drifting; ONE craft move per turn; model on a different scene; hand back with an "I can…" criterion); two reference packs (`references/imaginative/year-8/voice-craft.md`, `references/imaginative/year-9-10/voice-craft.md`) encoding the priority-ordered issue types (Year 8: summarised key moment / named emotions / POV drift; Year 9–10 adds thin-or-clichéd imagery at the key beat, design-vs-drift POV rule, and tone whiplash) with band calibration, traced to reaserch.md (imaginative domain, Year 8/9 formats, marking criteria, A–E elaborations, NAPLAN narrative criteria), teacher-skills.md (AERO); Year 10 carries the Q-001 derived-not-verbatim note.
- Two golden fixtures: sample-01 (Year 8 bush story — noise-in-the-dark key moment told in one sentence + named emotions; type 1 is the priority pick) and sample-02 (Year 9 moving-away opening — genuine shown beats inside the lens, but unsignalled drift into Mum's head and third-person "Marcus"; type 3 is the priority pick), discovered as imaginative/year-8 and imaginative/year-9-10.
- Routing wired: diagnose-errors SKILL.md route list + both imaginative taxonomy packs now route showing/immediacy and voice/POV/tone to `craft-voice` (plot/arc/structural control stay with check-structure; "planned ISS-008" notes removed from the taxonomies and both give-feedback imaginative rubrics). `LOOP_STAGES` gains the skill as `coach`; skills/README.md index updated (ten skills).
- Lane discipline: check-structure keeps plot arc, complication, scene order, and structural control; craft-voice owns showing strategy, key-moment craft, narrator/POV/tone; elevate-vocabulary keeps individual word choice.
- Tests: new `test_craft_voice_loads_imaginative_packs_and_examples`, new `test_diagnosis_router_routes_imaginative_to_craft_voice` (dispatch + imaginative year-8 voice-craft pack in the coaching prompt); count updates (9→10 skills, 18→20 cases) in loader/sync/eval tests; fixture-test comments extended to both specialist skills.
- Live LLM judge eval was not run (no valid API credential in this environment — the `.env` Kimi key returns 401); the historical "live eval PASS" line in IMPLEMENTATION-PLAN-2 8.2 remains a pre-beta follow-up, while this ticket's declared verification is the no-judge harness above.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 8.2; PRD: §3 bounded feedback; ERD: skill registry` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-20T08:00:00+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-20T08:15:00+10:00 - DONE. Tenth skill craft-voice shipped: SKILL.md + two imaginative voice-craft packs (year-8, year-9-10) + two golden fixtures; diagnose-errors imaginative taxonomies route showing/immediacy and voice/POV/tone to it. Verification: targeted 22 passed; full suite 167 passed/4 skipped; ruff clean; mypy unchanged vs baseline (29 errors in the same 4 unrelated test files); skill eval 2/2 PASS (imaginative/year-8 + year-9-10 combos); full no-judge eval 20 cases, 16 passed/4 failed — unchanged canned-fake baseline. Unlocks ISS-009.

## ISS-009 - Seed and wire imaginative daily loop
- Status: `DONE`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-008`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 8.3; PRD: §4 daily-loop UX; ERD: session/attempt/rubric_score`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-20T10:12:46+10:00`
- Completed: `2026-08-20T10:30:00+10:00`
- Commit: `None`

### Outcome and scope
Seed imaginative outcomes and run the full daily loop with text_type=imaginative, persisting rubric scores.

### Acceptance criteria
- [x] Imaginative curriculum outcomes are seeded idempotently.
- [x] An imaginative session can start, advance, submit, and receive feedback over HTTP.
- [x] Rubric scores persist for an imaginative graded attempt.

### Implementation notes
- Likely files or components: backend/app/seed.py, backend/app/sessions/interactive.py, backend/app/api/routes.py, backend/tests/test_api_daily_loop.py.
- Constraints: keep analytical and persuasive loops unchanged; unsupported combos fail clearly.

### Verification
- [x] `cd backend && uv run pytest tests/test_seed.py tests/test_api_daily_loop.py` — 20 passed.
- [x] `cd backend && uv run pytest` — 169 passed, 4 skipped (was 167/4; +2 new tests).
- [x] `cd backend && uv run ruff check .` — clean; `uv run mypy app tests` — 29 errors in the same 4 unrelated test files as the ISS-008 baseline (test_config, test_delete_student, test_interaction_log, test_session_time); changed files clean.

### Completion evidence
- `app/seed.py` gains three imaginative outcome sets seeded idempotently via the existing `(year_level, text_type, outcomes)` triples — the six analytical/persuasive sets are unchanged (codes/descriptors byte-identical). `YEAR_8_IMAGINATIVE_OUTCOMES` (QCAA-Y8-IMA-01..04: one clear complication with rising tension, show-don't-tell with sensory detail, consistent POV/character, hook + format-fit sustained narrative — traced to reaserch.md Year 8 marking criteria + NAPLAN narrative criteria + the ISS-007 year-8 criteria bank), `YEAR_9_IMAGINATIVE_OUTCOMES` (QCAA-Y9-IMA-01..04: purposeful structural experimentation with reader orientation, distinct narrator voice with signalled tone/POV shifts, motif-level imagery, 600–800 word sustained complication — traced to reaserch.md Year 9 marking criteria + the year-9-10 criteria bank), `YEAR_10_IMAGINATIVE_OUTCOMES` (QCAA-Y10-IMA-01..04, derived one band up per Q-001). `backend/seed.py` print updated; module docstring records the imaginative provenance.
- No loop code changed: `InteractiveLoop._resolve_text_type` already resolves `focus_text_types[0]` on every stage (P6.2), so a student with `focus_text_types=["imaginative"]` runs the imaginative loop end-to-end today — proven by the new HTTP test.
- Tests: new `test_seed_creates_imaginative_outcomes` (12 imaginative rows across Year 8-10, codes/curriculum, Year 8-9 band-shift descriptors — experiment/motif at Year 9 vs complication at Year 8 — analytical + persuasive sets untouched); new `test_imaginative_session_runs_loop_and_persists_scores` — full loop over HTTP with FakeProvider: diagnosis routes to `craft-voice`, 5 rubric scores persist with imaginative criterion names (Story & tension C, Showing & voice D), every pack-bearing prompt (criteria/independent/diagnosis/coach/feedback) cites the imaginative/year-8 packs, feedback prompt carries "Story & tension", no degradation note on any tutor turn.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 8.3; PRD: §4 daily-loop UX; ERD: session/attempt/rubric_score` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-20T10:12:46+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-20T10:30:00+10:00 - DONE. Imaginative outcomes seeded idempotently (12 outcomes across Year 8/9/10, QCAA-Y*-IMA-* codes, traced to reaserch.md + ISS-007 packs, Q-001 derived note for Year 10); imaginative daily loop proven over HTTP with FakeProvider — craft-voice routing, imaginative pack citations on all pack-bearing prompts, 5 rubric scores persisted. Verification: targeted 20 passed; full suite 169 passed/4 skipped; ruff clean; mypy unchanged vs baseline. Unlocks ISS-010.

## ISS-010 - Beta first-run wizard and profile UX
- Status: `READY`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-009`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B1.1; PRD: §9 FR-GA-002; ERD: student`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Polish clean-machine docker compose startup into a guided first run that creates a student profile, picks year level, and starts a first session quickly.

### Acceptance criteria
- [ ] A clean machine can reach a first session in under 15 minutes following README/DEPLOYMENT guidance.
- [ ] First-run flow creates or selects a student profile.
- [ ] Profile edit remains available after first run.

### Implementation notes
- Likely files or components: frontend/src/components/ProfileView.tsx, frontend/src/App.tsx, README.md, DEPLOYMENT.md, docker-compose.yml.
- Constraints: V1/Beta remains per-family local install; no public auth or billing in this ticket.

### Verification
- [ ] `cd frontend && npm run build`
- [ ] `cd backend && uv run pytest tests/test_student_profile.py`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B1.1; PRD: §9 FR-GA-002; ERD: student` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-011 - Student data export and restore
- Status: `READY`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-010`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B1.2; PRD: §6 privacy; ERD: Privacy & retention`
- Effort: `S`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Add one-click local JSON export of a student's full data and an import path that restores progress.

### Acceptance criteria
- [ ] Export includes profile, sessions, attempts, feedback, rubric scores, and relevant logs.
- [ ] Export → delete → import round-trip preserves progress.
- [ ] Tests cover the round-trip.

### Implementation notes
- Likely files or components: backend/app/api/routes.py, backend/app/models.py, backend/app/database.py, frontend/src/components/ProfileView.tsx.
- Constraints: export stays local; do not add cloud sync; treat exported content as sensitive minor data.

### Verification
- [ ] `cd backend && uv run pytest tests/test_delete_student.py tests/test_student_profile.py`
- [ ] `cd backend && uv run pytest`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B1.2; PRD: §6 privacy; ERD: Privacy & retention` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-012 - New skill baseline-assessment
- Status: `READY`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-011`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B2.1; PRD: §5 North Star metric; ERD: student/rubric_score`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Add the eleventh agent skill baseline-assessment: one timed write produces a rubric baseline and a recommended student focus profile.

### Acceptance criteria
- [ ] skills/baseline-assessment/ follows skills/README.md convention.
- [ ] A new student's first use can complete a baseline and write day-0 rubric_score rows.
- [ ] The baseline recommends ranked weaknesses and a starting focus loop.

### Implementation notes
- Likely files or components: skills/baseline-assessment/, backend/app/skills/router.py, backend/app/sessions/interactive.py, backend/tests/test_student_profile.py.
- Constraints: baseline is coaching-oriented, not a high-stakes exam; avoid overwhelming the student with feedback.

### Verification
- [ ] `cd backend && uv run pytest tests/test_skill_loader.py tests/test_student_profile.py`
- [ ] `cd backend && uv run python -m app.eval --skill baseline-assessment --no-judge`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B2.1; PRD: §5 North Star metric; ERD: student/rubric_score` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-013 - New skill fix-mechanics
- Status: `READY`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-012`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B3.1; PRD: §3 bounded feedback; ERD: skill registry`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Add the twelfth agent skill fix-mechanics for grammar, spelling, and punctuation coaching as a third diagnose-errors route.

### Acceptance criteria
- [ ] skills/fix-mechanics/ follows skills/README.md convention.
- [ ] Golden examples exist and are discovered by the eval harness.
- [ ] diagnose-errors can route mechanics-dominant submissions to fix-mechanics while staying bounded.

### Implementation notes
- Likely files or components: skills/fix-mechanics/, backend/app/skills/router.py, backend/tests/test_diagnosis_router.py.
- Constraints: mechanics feedback must not flatten the feedback into a laundry list; max 1-2 next steps.

### Verification
- [ ] `cd backend && uv run pytest tests/test_diagnosis_router.py tests/test_skill_loader.py`
- [ ] `cd backend && uv run python -m app.eval --skill fix-mechanics --no-judge`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B3.1; PRD: §3 bounded feedback; ERD: skill registry` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-014 - New skill spaced-review and retrieval stage
- Status: `READY`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-013`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B3.2; MVP-Plan: §2 core loop; ERD: interaction_log/rubric_score`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Add the thirteenth agent skill spaced-review and make retrieval the first stage of the daily loop using interaction_log and rubric_score history.

### Acceptance criteria
- [ ] skills/spaced-review/ follows skills/README.md convention.
- [ ] Daily loop order becomes retrieval → criteria → I do → we do → you do → feedback.
- [ ] Tests cover the new stage order and retrieval item generation inputs.

### Implementation notes
- Likely files or components: skills/spaced-review/, backend/app/sessions/interactive.py, backend/app/sessions/orchestrator.py, backend/tests/test_session_time.py, backend/tests/test_api_daily_loop.py.
- Constraints: retrieval items are short warm-ups; do not turn them into a second full lesson.

### Verification
- [ ] `cd backend && uv run pytest tests/test_session_orchestrator.py tests/test_api_daily_loop.py`
- [ ] `cd backend && uv run pytest`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B3.2; MVP-Plan: §2 core loop; ERD: interaction_log/rubric_score` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-015 - Weekly timed mock mode
- Status: `READY`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-014`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B3.3; PRD: §3 weekly timed practice; ERD: attempt.mode/rubric_score`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Add a weekly-mock mode with QCAA-like conditions and summative A-E feedback, visually distinct in the progress trend.

### Acceptance criteria
- [ ] A mock session completes end-to-end and stores attempt.mode='assessment'.
- [ ] Progress view distinguishes daily practice points from weekly mock points.
- [ ] Summative feedback remains bounded and references rubric criteria.

### Implementation notes
- Likely files or components: backend/app/sessions/interactive.py, backend/app/api/schemas.py, frontend/src/components/ProgressView.tsx, backend/tests/test_api_daily_loop.py.
- Constraints: mock mode is periodic; do not disrupt the daily 15-20 minute loop.

### Verification
- [ ] `cd backend && uv run pytest tests/test_api_daily_loop.py tests/test_session_time.py`
- [ ] `cd frontend && npm run build`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B3.3; PRD: §3 weekly timed practice; ERD: attempt.mode/rubric_score` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-016 - Streaks and weekly goal
- Status: `READY`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-015`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B4.1; PRD: §7 deferred motivation layer; ERD: student/session`
- Effort: `S`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Add a gentle streak counter and default weekly goal of four sessions, with recovery rather than punishment after a break.

### Acceptance criteria
- [ ] Streak and weekly goal persist per student.
- [ ] UI renders current streak and weekly progress.
- [ ] A break produces a recovery prompt, not a penalty.

### Implementation notes
- Likely files or components: backend/app/models.py, backend/app/api/routes.py, frontend/src/components/ProgressView.tsx or App.tsx.
- Constraints: motivation serves practice; no points shop, leaderboard, or punitive mechanics.

### Verification
- [ ] `cd backend && uv run pytest`
- [ ] `cd frontend && npm run build`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B4.1; PRD: §7 deferred motivation layer; ERD: student/session` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-017 - Criterion level-up celebration
- Status: `READY`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-016`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B4.2; PRD: §5 North Star metric; ERD: rubric_score`
- Effort: `S`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Detect when a rubric criterion crosses a band and trigger specific praise naming the real improvement.

### Acceptance criteria
- [ ] A criterion band crossing is persisted as an event or derived reliably from rubric_score history.
- [ ] UI shows a level-up moment tied to the actual criterion change.
- [ ] Message references the improvement mechanism, not generic praise only.

### Implementation notes
- Likely files or components: backend/app/api/routes.py, backend/app/models.py, frontend/src/components/ProgressView.tsx.
- Constraints: do not invent progress; only celebrate observed rubric_score changes.

### Verification
- [ ] `cd backend && uv run pytest`
- [ ] `cd frontend && npm run build`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B4.2; PRD: §5 North Star metric; ERD: rubric_score` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-018 - Coach persona tone setting
- Status: `READY`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-017`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B4.3; PRD: §9 GA profile direction; ERD: student`
- Effort: `S`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Add a per-profile coach tone setting that changes system-prompt tone without changing teaching output contracts.

### Acceptance criteria
- [ ] Profile supports a tone setting such as warm, strict, or humorous.
- [ ] Same input yields perceptibly different tone while preserving skill output contract.
- [ ] Tests assert contract fields remain present.

### Implementation notes
- Likely files or components: backend/app/models.py, backend/app/skills/executor.py, frontend/src/components/ProfileView.tsx.
- Constraints: tone is prompt-level only; never changes rubric levels, next-step bounds, or guardrails.

### Verification
- [ ] `cd backend && uv run pytest tests/test_student_profile.py tests/test_skill_executor.py`
- [ ] `cd frontend && npm run build`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B4.3; PRD: §9 GA profile direction; ERD: student` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-019 - Weekly parent report with privacy boundary
- Status: `READY`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-018`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B5.1; PRD: §7 deferred parent layer; ERD: Privacy & retention`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Add an in-app weekly parent report and printable PDF showing sessions, time, criterion trends, highlight, and next-week suggestion without exposing full essay text by default.

### Acceptance criteria
- [ ] Parent endpoints return trends/levels/time/goals but no attempt full text.
- [ ] Printable report generates from the same data.
- [ ] Tests assert the privacy boundary.

### Implementation notes
- Likely files or components: backend/app/api/routes.py, backend/app/api/schemas.py, frontend/src/components/ProgressView.tsx or new ParentView.
- Constraints: D3 remains in force: parents see trends, not full essays, unless the student explicitly shares.

### Verification
- [ ] `cd backend && uv run pytest`
- [ ] `cd frontend && npm run build`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B5.1; PRD: §7 deferred parent layer; ERD: Privacy & retention` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-020 - Shared parent-student goal setting
- Status: `READY`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-019`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B5.2; PRD: §7 deferred parent layer; ERD: student/session`
- Effort: `S`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Let parent and student set a weekly goal together and surface it at the start of the session loop.

### Acceptance criteria
- [ ] Weekly goal is stored on the student profile or related goal record.
- [ ] Session opening references the shared goal.
- [ ] Goal edits are visible in the parent/student views according to the privacy boundary.

### Implementation notes
- Likely files or components: backend/app/models.py, backend/app/api/routes.py, backend/app/sessions/interactive.py, frontend/src/components/ProfileView.tsx.
- Constraints: keep goal supportive and lightweight; do not add surveillance-style controls.

### Verification
- [ ] `cd backend && uv run pytest`
- [ ] `cd frontend && npm run build`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B5.2; PRD: §7 deferred parent layer; ERD: student/session` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-021 - Per-stage model routing
- Status: `READY`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-020`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B6.1; PRD: §6 model-swappable; ERD: interaction_log`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Add config-driven per-stage model routing so heavy judgement stages can use stronger models and light stages can use cheaper tiers.

### Acceptance criteria
- [ ] Routing table is configurable by loop_stage.
- [ ] Tests assert the factory/executor picks the expected provider per stage.
- [ ] Interaction logs record the actual model used.

### Implementation notes
- Likely files or components: backend/app/config.py, backend/app/llm/factory.py, backend/app/skills/executor.py, backend/app/sessions/interactive.py.
- Constraints: business logic remains provider-agnostic; routing must not change skill contracts.

### Verification
- [ ] `cd backend && uv run pytest tests/test_llm.py tests/test_config.py tests/test_skill_executor.py`
- [ ] `cd backend && uv run pytest`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B6.1; PRD: §6 model-swappable; ERD: interaction_log` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-022 - Privacy-safe telemetry and feedback package
- Status: `READY`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-021`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B6.2; PRD: §6 privacy; ERD: Privacy & retention`
- Effort: `S`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Add local aggregated usage metrics with no student content and a one-click feedback package export for beta families.

### Acceptance criteria
- [ ] Telemetry excludes student writing and LLM content.
- [ ] Feedback package bundles logs/config/metadata needed to diagnose a beta issue.
- [ ] A beta issue can be diagnosed from the package in under 10 minutes.

### Implementation notes
- Likely files or components: backend/app/api/routes.py, backend/app/eval or backend/app/ops, frontend/src/components/ProfileView.tsx.
- Constraints: privacy-safe by default; no third-party analytics on student content.

### Verification
- [ ] `cd backend && uv run pytest`
- [ ] `cd frontend && npm run build`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B6.2; PRD: §6 privacy; ERD: Privacy & retention` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-023 - Beta handbook
- Status: `READY`
- Priority: `P2`
- Type: `chore`
- Depends on: `ISS-022`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B6.3; PRD: §9 GA direction; ERD: Deployment/migration`
- Effort: `S`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Write the beta handbook: install guide, parent one-pager, feedback channel, and weekly check-in template.

### Acceptance criteria
- [ ] A non-technical parent can install from the guide alone.
- [ ] Handbook includes privacy expectations and feedback channel.
- [ ] Weekly check-in template exists for beta families.

### Implementation notes
- Likely files or components: docs or root markdown files, README.md, DEPLOYMENT.md.
- Constraints: keep Beta per-family local install; do not describe unsupported hosted GA features as available.

### Verification
- [ ] Manual check: follow the guide on a clean machine profile or review against DEPLOYMENT.md
- [ ] `cd backend && uv run pytest`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B6.3; PRD: §9 GA direction; ERD: Deployment/migration` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-024 - QCE senior instrument modelling
- Status: `READY`
- Priority: `P2`
- Type: `research`
- Depends on: `ISS-023`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 10.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Model QCE Units 1-4, IA1, IA2, IA3, and EA into curriculum_outcome and write the ISMG to A-E mapping research note.

### Acceptance criteria
- [ ] Senior assessment instruments are represented in the curriculum model.
- [ ] ISMG to A-E mapping strategy is documented with sources.
- [ ] No senior content depth is claimed beyond the modelled framework.

### Implementation notes
- Likely files or components: backend/app/seed.py, curriculum research notes, reaserch.md, test-context.md.
- Constraints: senior depth waits for a real senior user except IA1 framework; avoid speculative full senior content.

### Verification
- [ ] `cd backend && uv run pytest tests/test_seed.py`
- [ ] Manual check: mapping note cites sources and matches curriculum_outcome seed shape

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 10.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-025 - Senior IA1 analytical pack
- Status: `READY`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-024`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 10.2; PRD: §9 FR-GA-003; ERD: curriculum_outcome/skill`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Fill analytical/year-11-12 reference depth for IA1 only and prove an IA1 task receives senior-standard feedback end-to-end.

### Acceptance criteria
- [ ] references/analytical/year-11-12/ contains IA1-specific pack content.
- [ ] An IA1 analytical task can run through the loop and produce senior-standard feedback.
- [ ] Eval coverage includes the senior IA1 combo.

### Implementation notes
- Likely files or components: skills/*/references/analytical/year-11-12/, skills/*/examples/, backend/app/eval.
- Constraints: do not broaden to IA2/IA3/EA content depth in this ticket.

### Verification
- [ ] `cd backend && uv run pytest tests/test_skill_loader.py tests/test_skill_executor.py`
- [ ] `cd backend && uv run python -m app.eval --no-judge`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 10.2; PRD: §9 FR-GA-003; ERD: curriculum_outcome/skill` during `/plan`; completed milestones were kept as context, not tickets.

## Change Log
- `2026-08-19T13:44:45+10:00` - Initialized by `/plan` from `PRD.md`, `ERD.md`, and `IMPLEMENTATION-PLAN-2.md`; completed P0-P5/P6.1/P6.2 work recorded as context only.
