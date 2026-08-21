# Delivery Backlog

This document is the canonical delivery state for autonomous development. Detailed issue blocks are authoritative; the index is a convenience summary.

## Delivery Gate
- State: `OPEN`
- Blocking questions: `None`
- Reason: No `BLOCKING` questions are open; completed P0-P5/P6.1/P6.2 work is recorded as context only, not as tickets.
- Active issue: `None`
- Integration mode: `delivery-branch`
- Delivery branch: `feature/english-tutor-delivery`
- Last evaluated: `2026-08-21T21:08:48+10:00`

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
| ISS-010 | Beta first-run wizard and profile UX | `DONE` | `P1` | `ISS-009` | `None` |
| ISS-011 | Student data export and restore | `DONE` | `P1` | `ISS-010` | `None` |
| ISS-012 | New skill baseline-assessment | `DONE` | `P1` | `ISS-011` | `None` |
| ISS-013 | New skill fix-mechanics | `DONE` | `P1` | `ISS-012` | `None` |
| ISS-014 | New skill spaced-review and retrieval stage | `DONE` | `P1` | `ISS-013` | `None` |
| ISS-015 | Weekly timed mock mode | `DONE` | `P1` | `ISS-014` | `None` |
| ISS-016 | Streaks and weekly goal | `DONE` | `P2` | `ISS-015` | `None` |
| ISS-017 | Criterion level-up celebration | `DONE` | `P2` | `ISS-016` | `None` |
| ISS-018 | Coach persona tone setting | `DONE` | `P2` | `ISS-017` | `None` |
| ISS-019 | Weekly parent report with privacy boundary | `DONE` | `P2` | `ISS-018` | `None` |
| ISS-020 | Shared parent-student goal setting | `DONE` | `P2` | `ISS-019` | `None` |
| ISS-021 | Per-stage model routing | `DONE` | `P2` | `ISS-020` | `None` |
| ISS-022 | Privacy-safe telemetry and feedback package | `DONE` | `P2` | `ISS-021` | `None` |
| ISS-023 | Beta handbook | `DONE` | `P2` | `ISS-022` | `None` |
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
- Commit: `9cc354f`

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
- Status: `DONE`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-009`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B1.1; PRD: §9 FR-GA-002; ERD: student`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-20T12:23:00+10:00`
- Completed: `2026-08-20T12:35:00+10:00`
- Commit: `804d7f1`

### Outcome and scope
Polish clean-machine docker compose startup into a guided first run that creates a student profile, picks year level, and starts a first session quickly.

### Acceptance criteria
- [x] A clean machine can reach a first session in under 15 minutes following README/DEPLOYMENT guidance.
- [x] First-run flow creates or selects a student profile.
- [x] Profile edit remains available after first run.

### Implementation notes
- Likely files or components: frontend/src/components/ProfileView.tsx, frontend/src/App.tsx, README.md, DEPLOYMENT.md, docker-compose.yml.
- Constraints: V1/Beta remains per-family local install; no public auth or billing in this ticket.

### Verification
- [x] `cd frontend && npm run build` — tsc + vite build clean (370.97 kB bundle).
- [x] `cd backend && uv run pytest tests/test_student_profile.py` — 9 passed.
- [x] `cd frontend && npm run lint` (oxlint) — 0 warnings, 0 errors.
- [x] `cd backend && uv run pytest` — 169 passed, 4 skipped (unchanged from ISS-009 baseline; no backend source changed); `uv run ruff check .` clean.
- [x] HTTP smoke against a real backend (`LLM_PROVIDER=fake`, tmp SQLite): `GET /api/students` → `[]`, `POST /api/students` → 201 with `focus_text_types` persisted, `GET /api/students` → the created profile — the exact call chain the wizard makes.

### Completion evidence
- New `frontend/src/components/FirstRunWizard.tsx`: gated in `App.tsx` on `studentId === null`, so any browser without a linked profile lands on the wizard before the tabbed UI. The wizard lists existing server profiles via `listStudents()` (pick one — shared family server / new device) or creates a new profile (name, year level 8–12, curriculum QCAA/NESA, optional focus text types) via `createStudent()`; on success it persists id + profile to localStorage and hands the `StudentOut` to App, which lands on the Today tab start card.
- `App.tsx` hydrates `student` from the cached profile on load, so the session start card greets the student by name immediately (previously only after opening the Profile tab).
- `ProfileView.tsx` keeps create/edit unchanged (Profile tab = edit after first run); **Clear** now also clears the stored student id (`storage.ts` gains `clearStudentId()`) and calls a new optional `onClear` prop, returning the app to the wizard so another profile can be selected or created — previously Clear left a stale id linked.
- Styling reuses existing tokens (`profile-shell`/`profile-card`/`chip`/`btn`); only `.wizard-list`/`.wizard-student*` and `.btn.ghost.wide` added to `App.css`.
- Docs: README gains a "First run (guided)" section (pick-or-create profile → start first session; edit any time in Profile; <15 min clean-machine path, long pole = one-time image build) and the skills count is corrected 8 → 10. DEPLOYMENT.md gains a matching 首次使用（首跑向导）section.
- No backend code changed; no auth/billing introduced (per-family local install preserved). The <15-minute criterion is supported by the documented path plus build/API-smoke evidence — no physical clean-machine run was performed in this environment.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B1.1; PRD: §9 FR-GA-002; ERD: student` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-20T12:23:00+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-20T12:35:00+10:00 - DONE. First-run wizard shipped: `FirstRunWizard` (select existing profile via `listStudents` or create new) gated on `studentId === null` in App; profile edit unchanged in the Profile tab; Clear unlinks the browser and returns to the wizard; README + DEPLOYMENT first-run guidance added. Verification: frontend build + oxlint clean; backend student-profile tests 9 passed; full backend suite 169 passed/4 skipped with ruff clean (backend untouched); HTTP smoke of the wizard's exact API chain (list → create → list) green against a real backend with FakeProvider. Unlocks ISS-011.

## ISS-011 - Student data export and restore
- Status: `DONE`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-010`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B1.2; PRD: §6 privacy; ERD: Privacy & retention`
- Effort: `S`
- Attempt: `1`
- Started: `2026-08-20T14:37:00+10:00`
- Completed: `2026-08-20T15:05:00+10:00`
- Commit: `c27b1ba`

### Outcome and scope
Add one-click local JSON export of a student's full data and an import path that restores progress.

### Acceptance criteria
- [x] Export includes profile, sessions, attempts, feedback, rubric scores, and relevant logs.
- [x] Export → delete → import round-trip preserves progress.
- [x] Tests cover the round-trip.

### Implementation notes
- Likely files or components: backend/app/api/routes.py, backend/app/models.py, backend/app/database.py, frontend/src/components/ProfileView.tsx.
- Constraints: export stays local; do not add cloud sync; treat exported content as sensitive minor data.

### Verification
- [x] `cd backend && uv run pytest tests/test_student_transfer.py tests/test_delete_student.py tests/test_student_profile.py` — 17 passed.
- [x] `cd backend && uv run pytest` — 175 passed, 4 skipped (was 169/4; +6 new tests).
- [x] `cd backend && uv run ruff check .` — clean; `uv run mypy app tests` — 29 errors in the same 4 unrelated test files as the ISS-010 baseline (test_config, test_delete_student, test_interaction_log, test_session_time); changed files clean.
- [x] `cd frontend && npm run build` — tsc + vite build clean (372.02 kB bundle); `npm run lint` (oxlint) — 0 warnings, 0 errors.

### Completion evidence
- New `backend/app/student_transfer.py`: `export_student()` serialises the profile plus every session (success criteria, attempts with feedback + rubric scores, interaction logs) into one versioned JSON document (`format: english-tutor-student-export`, `version: 1`, ISO datetimes); `import_student()` validates the document (`ExportImportError` → HTTP 400 on wrong format/version/missing profile/invalid year level) and restores it as a NEW student — fresh UUIDs for every student-owned row, references remapped, timestamps preserved so A–E progress trends survive. Skill/curriculum-outcome FKs are global registry data: kept only when the target row exists locally, else NULL (matching ON DELETE SET NULL semantics).
- Routes: `GET /api/students/{id}/export` (JSONResponse with `Content-Disposition: attachment; filename="english-tutor-export-<name>.json"`, 404 on unknown student) and `POST /api/students/import` (201 → StudentOut; declared before `/students/{student_id}` so the literal path wins). Import never overwrites an existing profile — restoring a backup while the original still exists creates a second profile (covered by test).
- Frontend: ProfileView saved card gains **Export my data** (one-click download via the attachment endpoint) with a privacy hint; FirstRunWizard gains **Restore from a backup file** (file picker → `importStudent` → lands on the Today tab as the restored profile), so the export → delete → import round-trip is reachable in the real UX on a clean browser. No cloud sync; the file stays local (PRD §6).
- Tests (`backend/tests/test_student_transfer.py`, 6 new): export document shape (profile/sessions/attempts incl. student writing/feedback with 5 rubric scores/interaction logs, content-disposition filename), export 404, export→delete→import round-trip asserting the progress endpoint returns the identical `(criterion, level, scored_at)` sequence under the new id, restore-alongside-original without collision, malformed-payload 400s, minimal profile-only import.
- Discovery during the run: the interactive loop never persists `SuccessCriterion` rows, so exported `success_criteria` is legitimately empty for loop sessions; the field is still exported/imported for completeness.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B1.2; PRD: §6 privacy; ERD: Privacy & retention` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-20T14:37:00+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-20T15:05:00+10:00 - DONE. Student data export/restore shipped: versioned JSON export endpoint + import-as-new-profile restore (fresh UUIDs, timestamps preserved, registry FKs resolved-or-NULL), one-click export in ProfileView, restore-from-backup in the first-run wizard. Verification: targeted 17 passed; full suite 175 passed/4 skipped; ruff clean; mypy unchanged vs baseline; frontend build + oxlint clean. Round-trip test proves identical rubric progress after export → delete → import. Unlocks ISS-012.

## ISS-012 - New skill baseline-assessment
- Status: `DONE`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-011`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B2.1; PRD: §5 North Star metric; ERD: student/rubric_score`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-20T16:40:00+10:00`
- Completed: `2026-08-20T17:10:00+10:00`
- Commit: `7f46f92`

### Outcome and scope
Add the eleventh agent skill baseline-assessment: one timed write produces a rubric baseline and a recommended student focus profile.

### Acceptance criteria
- [x] skills/baseline-assessment/ follows skills/README.md convention.
- [x] A new student's first use can complete a baseline and write day-0 rubric_score rows.
- [x] The baseline recommends ranked weaknesses and a starting focus loop.

### Implementation notes
- Likely files or components: skills/baseline-assessment/, backend/app/skills/router.py, backend/app/sessions/interactive.py, backend/tests/test_student_profile.py.
- Constraints: baseline is coaching-oriented, not a high-stakes exam; avoid overwhelming the student with feedback.

### Verification
- [x] `cd backend && uv run pytest tests/test_skill_loader.py tests/test_student_profile.py` — 27 passed.
- [x] `cd backend && LLM_PROVIDER=fake uv run python -m app.eval --skill baseline-assessment --no-judge` — 2 cases, 2 passed (analytical/year-8 + imaginative/year-9-10 combo rows).
- [x] `cd backend && uv run pytest` — 180 passed, 4 skipped (was 175/4; +5 new tests).
- [x] `cd backend && uv run ruff check .` — clean; `uv run mypy app tests` — 29 errors in the same 4 unrelated test files as the ISS-011 baseline (test_config, test_delete_student, test_interaction_log, test_session_time); changed files clean.
- [x] `cd backend && LLM_PROVIDER=fake uv run python -m app.eval --no-judge` — 22 cases, 18 passed / 4 failed (the same canned-fake give-feedback + diagnose-errors baseline as ISS-004 through ISS-011, unchanged); baseline-assessment 2/2 PASS.

### Completion evidence
- `skills/baseline-assessment/` authored per the convention: SKILL.md with all 8 required sections (confirm read conditions → read generously at the ceiling → rank levers → report baseline → one specific strength → recommend ONE starting focus → close with the first step); output contract carries literal `## Per-criterion levels` (5 lines, exact criterion names per text type), `## Ranked weaknesses` (max 3), `## Recommended focus loop` (one skill + text type + plain reason). One shared reference pack (`references/shared/baseline-guide.md`): baseline conditions, the five exact criterion names per text type × band (matching the give-feedback rubrics so day-0 rows trend in the progress view), band calibration, leverage ranking, weakness→starting-focus map, tone rules — traced to reaserch.md (marking criteria, A–E elaborations, the Year 8 C→A lever, NAPLAN criteria), Blueprint (diagnostic-first), teacher-skills.md (AERO, HITS feedback), Q-001 derived note for seniors.
- Two golden fixtures: sample-01 (Year 8 analytical first write — assertion-not-analysis C/D read, top lever = thin analysis → `check-structure`) and sample-02 (Year 9 imaginative — genuinely strong opening read honestly at B-ceiling, no A-inflation, stretch levers only), discovered as analytical/year-8 and imaginative/year-9-10.
- Backend: `InteractiveLoop.run_baseline()` persists a short already-ended baseline session (submission attempt + baseline tutor turn + InteractionLog) and parses the report through `parse_rubric_levels` into day-0 RubricScore rows on a Feedback attached to the report turn — the existing progress endpoint surfaces them unchanged. New route `POST /api/students/{student_id}/baseline` (201 → BaselineOut with session id, feedback incl. rubric scores, and the full report; 404 on unknown student). The profile is never mutated by the recommendation.
- Executor: shared-only skills (packs == {"shared"}) are combo-agnostic by design and no longer get a degradation note — the note would have been appended to every student-facing baseline report despite the guide covering all combos. Pack-bearing skills' fallback behaviour is unchanged (all fallback tests still pass).
- Tests (5 new): `test_baseline_assessment_loads_shared_guide_and_examples` (loader: stage `baseline`, shared guide, criterion names, 2 fixtures); `test_execute_shared_only_skill_adds_no_degradation_note`; `test_baseline_writes_day0_rubric_scores` (HTTP: 201, 5 parsed scores, progress endpoint returns the identical rows); `test_baseline_uses_profile_and_shared_pack` (year 9 + persuasive focus inherited, baseline-guide.md cited in the system prompt, session ended with submission + baseline turns); `test_baseline_unknown_student_returns_404`. Count updates 10→11 skills / 20→22 cases in loader/sync/eval tests.
- Live LLM judge eval was not run (no valid API credential in this environment); consistent with ISS-005/ISS-008, the no-judge harness above is this ticket's declared verification.
- Intentional follow-up (not this ticket): wire the baseline into the first-run wizard UX (ISS-010 shipped the wizard; the baseline is currently API-only).
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B2.1; PRD: §5 North Star metric; ERD: student/rubric_score` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-20T16:40:00+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-20T17:10:00+10:00 - DONE. Eleventh skill baseline-assessment shipped: SKILL.md + shared baseline guide + two golden fixtures (analytical/year-8, imaginative/year-9-10); `POST /api/students/{id}/baseline` runs the skill over one timed write and persists day-0 rubric scores (verified identical via the progress endpoint); report recommends ranked weaknesses (max 3) + one starting focus loop. Executor no longer appends degradation notes for shared-only skills. Verification: targeted 27 passed; full suite 180 passed/4 skipped; ruff clean; mypy unchanged vs baseline; skill eval 2/2 PASS; full no-judge eval 22 cases, 18 passed/4 failed — unchanged canned-fake baseline. Unlocks ISS-013.

## ISS-013 - New skill fix-mechanics
- Status: `DONE`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-012`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B3.1; PRD: §3 bounded feedback; ERD: skill registry`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-20T19:15:00+10:00`
- Completed: `2026-08-20T19:30:00+10:00`
- Commit: `8794a46`

### Outcome and scope
Add the twelfth agent skill fix-mechanics for grammar, spelling, and punctuation coaching as a third diagnose-errors route.

### Acceptance criteria
- [x] skills/fix-mechanics/ follows skills/README.md convention.
- [x] Golden examples exist and are discovered by the eval harness.
- [x] diagnose-errors can route mechanics-dominant submissions to fix-mechanics while staying bounded.

### Implementation notes
- Likely files or components: skills/fix-mechanics/, backend/app/skills/router.py, backend/tests/test_diagnosis_router.py.
- Constraints: mechanics feedback must not flatten the feedback into a laundry list; max 1-2 next steps.

### Verification
- [x] `cd backend && uv run pytest tests/test_diagnosis_router.py tests/test_skill_loader.py` — 23 passed.
- [x] `cd backend && LLM_PROVIDER=fake uv run python -m app.eval --skill fix-mechanics --no-judge` — 2 cases, 2 passed (analytical/year-8 + imaginative/year-9-10 combo rows).
- [x] `cd backend && uv run pytest` — 182 passed, 4 skipped (was 180/4; +2 new tests).
- [x] `cd backend && uv run ruff check .` — clean; `uv run mypy app tests` — 29 errors in the same 4 unrelated test files as the ISS-011/ISS-012 baseline (test_config, test_delete_student, test_interaction_log, test_session_time); changed files clean.
- [x] `cd backend && LLM_PROVIDER=fake uv run python -m app.eval --no-judge` — 24 cases, 20 passed / 4 failed (the same canned-fake give-feedback + diagnose-errors baseline as ISS-004 through ISS-012, unchanged); fix-mechanics 2/2 PASS.

### Completion evidence
- `skills/fix-mechanics/` authored per the convention: SKILL.md with all 8 required sections (scan → group into patterns → pick top 1–2 by frequency × cost-to-reader → teach rule + quote student sentence + model fix on an *invented* sentence → hand back with instance counts → one line of genuine noticing); output contract carries literal `## What I noticed` / `## Pattern 1:` (max two pattern sections) / `## Keep it up`. One shared reference pack (`references/shared/mechanics-guide.md`): error classes, pattern selection rule, band calibration for year-8 / year-9-10 / year-11-12 (senior calibration marked derived per Q-001), errors-vs-stylistic-choices boundary (deliberate fragments are craft, not error), the four-step teaching move, tone rules — traced to Blueprint (AERO SWIF explicit instruction, cognitive load, GRR), teacher-skills.md (HITS feedback), reaserch.md (A–E standards, NAPLAN conventions). Shared-only by design: mechanics coaching is text-type-agnostic, so no banded packs and no degradation note.
- Two golden fixtures: sample-01 (Year 8 analytical — comma splices ×3 + its/it's, ideas/structure sound so mechanics is the rightful route) and sample-02 (Year 9 imaginative — dialogue punctuation + apostrophes; the deliberate fragment "Nothing." must NOT be flagged), discovered as analytical/year-8 and imaginative/year-9-10.
- diagnose-errors wiring: SKILL.md dispatch list and `Route to:` contract now include `fix-mechanics`, with the explicit rule that mechanics routes only when it is the primary major issue AND higher-leverage categories are sound; all six taxonomy packs updated from "(future) `fix-mechanics`" to `fix-mechanics`. `DiagnosisRouter` needed no code change — `parse_route` already validates against loaded skills.
- Backend: loader `LOOP_STAGES` gains `fix-mechanics: coach`.
- Tests (2 new): `test_fix_mechanics_loads_shared_guide_and_examples` (loader: coach stage, shared guide, error classes + senior ceiling present, 2 fixtures, bounded "at most 2 patterns" criterion); `test_diagnosis_router_routes_mechanics_to_fix_mechanics` (route lands, diagnosis prompt offers the route, coaching prompt carries mechanics-guide.md, no degradation note for the shared-only skill). Count updates 11→12 skills / 22→24 cases in loader/sync/fixtures/runner tests.
- Live LLM judge eval was not run (no valid API credential in this environment); consistent with ISS-005/ISS-008/ISS-012, the no-judge harness above is this ticket's declared verification.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B3.1; PRD: §3 bounded feedback; ERD: skill registry` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-20T19:15:00+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-20T19:30:00+10:00 - DONE. Twelfth skill fix-mechanics shipped: SKILL.md + shared mechanics guide + two golden fixtures (analytical/year-8, imaginative/year-9-10); diagnose-errors routes mechanics-dominant submissions to it across all six taxonomy packs with the leverage guard intact. Verification: targeted 23 passed; full suite 182 passed/4 skipped; ruff clean; mypy unchanged vs baseline; skill eval 2/2 PASS; full no-judge eval 24 cases, 20 passed/4 failed — unchanged canned-fake baseline. Unlocks ISS-014.

## ISS-014 - New skill spaced-review and retrieval stage
- Status: `DONE`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-013`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B3.2; MVP-Plan: §2 core loop; ERD: interaction_log/rubric_score`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-20T21:33:15+10:00`
- Completed: `2026-08-20T21:51:36+10:00`
- Commit: `8009267`

### Outcome and scope
Add the thirteenth agent skill spaced-review and make retrieval the first stage of the daily loop using interaction_log and rubric_score history.

### Acceptance criteria
- [x] skills/spaced-review/ follows skills/README.md convention.
- [x] Daily loop order becomes retrieval → criteria → I do → we do → you do → feedback.
- [x] Tests cover the new stage order and retrieval item generation inputs.

### Implementation notes
- Likely files or components: skills/spaced-review/, backend/app/sessions/interactive.py, backend/app/sessions/orchestrator.py, backend/tests/test_session_time.py, backend/tests/test_api_daily_loop.py.
- Constraints: retrieval items are short warm-ups; do not turn them into a second full lesson.

### Verification
- [x] `cd backend && uv run pytest tests/test_session_orchestrator.py tests/test_api_daily_loop.py` — 19 passed.
- [x] `cd backend && uv run pytest` — 185 passed, 4 skipped (was 182/4; +3 new tests).
- [x] `cd backend && uv run ruff check .` — clean; `uv run mypy app tests` — 29 errors in the same 4 unrelated test files as the ISS-013 baseline (test_config, test_delete_student, test_interaction_log, test_session_time — same error classes/count, verified line-by-line for the edited test_interaction_log.py); changed files clean.
- [x] `cd backend && LLM_PROVIDER=fake uv run python -m app.eval --skill spaced-review --no-judge` — 2 cases, 2 passed (analytical/year-8 + imaginative/year-9-10 combo rows).
- [x] `cd backend && LLM_PROVIDER=fake uv run python -m app.eval --no-judge` — 26 cases, 22 passed / 4 failed (the same canned-fake give-feedback + diagnose-errors baseline as ISS-004 through ISS-013, unchanged); spaced-review 2/2 PASS.
- [x] `cd frontend && npm run build` — tsc + vite build clean (372.04 kB bundle); `npm run lint` (oxlint) — 0 warnings, 0 errors.

### Completion evidence
- `skills/spaced-review/` authored per the convention: SKILL.md with all 8 required sections (read the digest → pick 2–3 targets: weakest criterion first, then the most recently coached pattern when days have passed → one short recall/spot/apply-in-one-line item per target → self-check answers → one onward line; cold start = 2 generic items from the text-type fundamentals, honestly declared). One shared reference pack (`references/shared/retrieval-guide.md`): why retrieval first, the `review_history` digest shape, the three item types, the cold-start menu per text type, band calibration (year-8 / year-9-10 / year-11-12 with the Q-001 derived note for seniors), and the 3-minute time/tone box — traced to teacher-skills.md (HITS/VTLM "quick retrieval" lesson opening; AERO SWIF spaced repetition), Blueprint (cognitive load/GRR), MVP-Plan §2 (热身 retrieval loop step 1). Shared-only by design: retrieval practice is text-type-agnostic, so no banded packs and no degradation note.
- Two golden fixtures: sample-01 (analytical/year-8 with a real digest — Analysis at D + elevate-vocabulary coached 3 days ago; items must trace to the digest, never invent history) and sample-02 (imaginative/year-9-10 cold start; must declare first session and use the fundamentals menu), discovered as analytical/year-8 and imaginative/year-9-10.
- Retrieval stage wired as loop step 1 in both drivers: `InteractiveLoop.start()` and `SessionOrchestrator.run_daily_loop()` now run spaced-review before set-success-criteria and persist a `task_type="retrieval"` tutor turn; the GRR stage machine (`start → I do → we do → you do → ended`) is unchanged. New `app/sessions/review.py::build_review_history(db, student_id)` builds the compact digest from `rubric_score` (latest level per criterion, weakest first) and coaching turns (interaction history; most recent coach skills with local dates) plus days since the last ended session; a student with no finished sessions gets the cold-start line only. `LOOP_STAGES` gains `spaced-review: retrieval`; frontend `STAGE_LABELS` gains `retrieval: 'Warm-up review'`.
- Tests: new `test_spaced_review_loads_shared_guide_and_examples` (loader: retrieval stage, shared guide, digest/cold-start/band content, 2 fixtures, bounded "2–3" criterion); new `test_retrieval_cold_start_when_no_history` and `test_retrieval_uses_rubric_and_coach_history` (HTTP: after a full loop the next session's spaced-review call carries `review_history: Days since last session: 0`, weakest-first criterion levels, and `Recently coached: check-structure`); stage order pinned as ordered task_type lists in the orchestrator test and `test_get_session_rebuilds_conversation` (retrieval → criteria → model → guided → … → feedback); `test_interaction_log` updated (start now logs both opening skills). Count updates 12→13 skills / 24→26 cases in loader/sync/fixtures/runner tests; all loop-driving canned response lists gained the retrieval response; pack-citation call indices shifted +1 (spaced-review is call 0, shared-only, no pack).
- Live LLM judge eval was not run (no valid API credential in this environment); consistent with ISS-005/ISS-008/ISS-012/ISS-013, the no-judge harness above is this ticket's declared verification.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B3.2; MVP-Plan: §2 core loop; ERD: interaction_log/rubric_score` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-20T21:33:15+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-20T21:51:36+10:00 - DONE. Thirteenth skill spaced-review shipped: SKILL.md + shared retrieval guide + two golden fixtures (analytical/year-8 with digest, imaginative/year-9-10 cold start); retrieval is now loop step 1 in both the interactive loop and the scripted orchestrator, fed by `build_review_history` (rubric_score weakest-first levels + recent coaching + days-since). Verification: targeted 19 passed; full suite 185 passed/4 skipped; ruff clean; mypy unchanged vs baseline; skill eval 2/2 PASS; full no-judge eval 26 cases, 22 passed/4 failed — unchanged canned-fake baseline; frontend build + lint clean. Unlocks ISS-015.

## ISS-015 - Weekly timed mock mode
- Status: `DONE`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-014`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B3.3; PRD: §3 weekly timed practice; ERD: attempt.mode/rubric_score`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-21T02:06:00+10:00`
- Completed: `2026-08-21T02:35:00+10:00`
- Commit: `43a8001`

### Outcome and scope
Add a weekly-mock mode with QCAA-like conditions and summative A-E feedback, visually distinct in the progress trend.

### Acceptance criteria
- [x] A mock session completes end-to-end and stores attempt.mode='assessment'.
- [x] Progress view distinguishes daily practice points from weekly mock points.
- [x] Summative feedback remains bounded and references rubric criteria.

### Implementation notes
- Likely files or components: backend/app/sessions/interactive.py, backend/app/api/schemas.py, frontend/src/components/ProgressView.tsx, backend/tests/test_api_daily_loop.py.
- Constraints: mock mode is periodic; do not disrupt the daily 15-20 minute loop.

### Verification
- [x] `cd backend && uv run pytest tests/test_api_daily_loop.py tests/test_session_time.py` — 33 passed (+3 new mock tests).
- [x] `cd frontend && npm run build` — tsc + vite build clean (375.36 kB bundle); `npm run lint` (oxlint) — 0 warnings, 0 errors.
- [x] `cd backend && uv run pytest` — 188 passed, 4 skipped (was 185/4; +3 new tests).
- [x] `cd backend && uv run ruff check .` — clean; `uv run mypy app tests` — 29 errors in the same 4 unrelated test files as the ISS-014 baseline (test_config, test_delete_student, test_interaction_log, test_session_time); changed files clean.
- [x] HTTP smoke against a real backend (`LLM_PROVIDER=fake`, tmp SQLite): create student → `POST /api/students/{id}/mock` → 201 (session ended, `time_spent_seconds: 0`, submission `mode: "assessment"`, give-feedback tutor turn) → progress endpoint green.

### Completion evidence
- `InteractiveLoop.run_mock()` (adopted from the interrupted prior attempt, then reviewed and tested): one exam-conditions write creates an already-ended mock session holding the submission (`Attempt.mode="assessment"`) and a summative give-feedback turn (`mode: summative` input, so the overall A–E is attached per the skill contract); per-criterion levels are parsed into RubricScore rows. No retrieval/modelling/coaching run — QCAA-like conditions mean no scaffolds — while the feedback stays bounded (one strength, 1–2 next steps) and cites the exact combo rubric pack.
- Route `POST /api/students/{student_id}/mock` (201 → `MockOut` with session id, feedback, and the full report text; 404 on unknown student via `SessionNotFoundError`). `MockOut.report` added this run so the summative report is renderable without a second fetch (mirrors `BaselineOut.report`). The progress endpoint now returns `mode` per score (`ProgressScoreOut.mode`).
- Frontend: ProgressView renders `mode === 'assessment'` points as ◆ diamonds (daily practice stays ● circles) with a "Weekly mock — …" tooltip and a conditional legend note (`◆ Weekly timed mock · ● Daily practice`). ChatView start card gains a "Sit this week's timed mock" entry (student-linked only) → new `MockView` component: exam-conditions explainer → paste the timed piece → level badges (reusing `level-badge` styles) + the Markdown report + back link. `runMock` API client and `MockOut` / `ProgressScoreOut.mode` types added.
- Tests (3 new in `test_api_daily_loop.py`): `test_mock_stores_assessment_mode_and_summative_scores` (201, 5 parsed scores, bounded report sections incl. `(Overall: **C+**)`, exactly one LLM call = give-feedback with `mode: summative` + year-8 rubric pack citation, session ended with zero practice time, submission + feedback turns carry `assessment` mode, progress rows all `assessment`); `test_mock_points_distinguished_from_daily_practice` (full daily loop then a mock → progress returns 5 `end` + 5 `assessment` rows); `test_mock_unknown_student_returns_404`.
- Live LLM judge eval was not run (no valid API credential in this environment); consistent with ISS-005 through ISS-014, this ticket's declared verification is the no-judge harness above.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B3.3; PRD: §3 weekly timed practice; ERD: attempt.mode/rubric_score` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-21T02:06:00+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions. On entry the tree held uncommitted edits (`interactive.py` `run_mock`, `/mock` route, `MockRequest`/`MockOut`, progress `mode`) matching this ticket's implementation notes, dated ~00:02+10 — consistent with a prior cron attempt interrupted before tests/tracker update (midnight local, exact ticket scope). Adopted rather than discarded after verifying the tree green (185 passed/4 skipped); no user work overwritten.
- 2026-08-21T02:35:00+10:00 - DONE. Weekly timed mock mode shipped: `run_mock` (ended mock session, submission `attempt.mode='assessment'`, summative give-feedback with overall A–E, bounded 1–2 next steps), `POST /api/students/{id}/mock` (MockOut + report), progress endpoint returns per-score `mode`; frontend ProgressView ◆ diamonds vs ● circles with legend note, ChatView "Sit this week's timed mock" entry → new MockView. Verification: declared `pytest tests/test_api_daily_loop.py tests/test_session_time.py` 33 passed; full suite 188 passed/4 skipped; ruff clean; mypy unchanged vs baseline; frontend build + oxlint clean; HTTP smoke green (mock 201, ended session, assessment mode, zero practice time). Unlocks ISS-016.

## ISS-016 - Streaks and weekly goal
- Status: `DONE`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-015`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B4.1; PRD: §7 deferred motivation layer; ERD: student/session`
- Effort: `S`
- Attempt: `1`
- Started: `2026-08-21T04:35:00+10:00`
- Completed: `2026-08-21T04:55:00+10:00`
- Commit: `2eac2f4`

### Outcome and scope
Add a gentle streak counter and default weekly goal of four sessions, with recovery rather than punishment after a break.

### Acceptance criteria
- [x] Streak and weekly goal persist per student.
- [x] UI renders current streak and weekly progress.
- [x] A break produces a recovery prompt, not a penalty.

### Implementation notes
- Likely files or components: backend/app/models.py, backend/app/api/routes.py, frontend/src/components/ProgressView.tsx or App.tsx.
- Constraints: motivation serves practice; no points shop, leaderboard, or punitive mechanics.

### Verification
- [x] `cd backend && uv run pytest` — 200 passed, 4 skipped (was 188/4; +12 new in tests/test_motivation.py).
- [x] `cd frontend && npm run build` — tsc + vite build clean (377.07 kB bundle); `npm run lint` (oxlint) 0 warnings, 0 errors.

### Completion evidence
- `Student.weekly_goal` persisted (default 4, validated 1–14 via `DEFAULT_WEEKLY_GOAL`/`MAX_WEEKLY_GOAL` in `app/models.py`); idempotent SQLite patcher `_ensure_student_weekly_goal_column` keeps existing dev/LAN DBs. Settable on create + PATCH; surfaced in `StudentOut`; export/import round-trips it (older exports default to 4).
- The streak is **derived** from persisted session history (`app/motivation.py::build_motivation`), never stored separately — a practice day is any local date with at least one session (daily loop, baseline, or weekly mock); the run stays alive through yesterday and counts back over consecutive local days. Week = Monday–today local; the goal counts sessions, not days.
- New `GET /api/students/{id}/motivation` → `MotivationOut` (`current_streak`, `streak_broken`, `weekly_goal`, `sessions_this_week`, `goal_met`, `last_activity_date`). A lapsed run reports `streak_broken=True` so the UI answers with recovery copy, never a penalty; no points/shop/leaderboard anywhere.
- Frontend: `MotivationStrip` in ProgressView (empty + populated states) — 🔥 streak chip, 🌱 recovery prompt ("Welcome back — no catching up needed. One session today starts a fresh streak."), weekly progress chip with ⭐ goal-reached state; ProfileView gains a Weekly goal row + edit select (2–7, 4 recommended) with a legacy-cache fallback (`?? 4`); `getMotivation` client + `MotivationOut` types; motivation fetch failures never block the chart.
- Tests: `tests/test_motivation.py` — 12 tests: cold start, 3-day streak, yesterday-grace, missed-day recovery flag, Monday-week session counting (sessions not days, last week excluded), goal_met at/above goal, export/import round-trip + legacy default, HTTP cold-start/404/422, live start-session moves streak+weekly count, PATCH persists and flips goal_met.
- Verification detail: full suite 200 passed/4 skipped; `ruff check .` clean; `mypy app tests` — 29 errors in the same 4 unrelated baseline test files (test_config, test_delete_student, test_interaction_log, test_session_time), changed files clean; frontend tsc+vite build clean, oxlint 0/0. HTTP smoke against a real backend (FakeProvider, tmp SQLite): create → cold start (0/4) → session start 201 → streak 1, 1/4 → PATCH goal=1 → goal_met true; 404 unknown student; 422 goal=0. `last_activity_date` correctly reported the Brisbane local date.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B4.1; PRD: §7 deferred motivation layer; ERD: student/session` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-21T04:35:00+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-21T04:55:00+10:00 - DONE. Streaks + weekly goal shipped: `weekly_goal` persisted on Student (default 4, 1–14, patchable, export/import round-trip), streak derived from session history (Mon–Sun week, sessions-not-days, yesterday grace), `GET /students/{id}/motivation`, MotivationStrip with recovery-not-penalty copy in ProgressView, goal editor in ProfileView. Verification: full suite 200 passed/4 skipped (+12 new); ruff clean; mypy unchanged vs baseline; frontend build + oxlint clean; HTTP smoke green (cold start → streak 1 → goal_met on patch; 404/422). Unlocks ISS-017.

## ISS-017 - Criterion level-up celebration
- Status: `DONE`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-016`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B4.2; PRD: §5 North Star metric; ERD: rubric_score`
- Effort: `S`
- Attempt: `1`
- Started: `2026-08-21T07:10:00+10:00`
- Completed: `2026-08-21T07:12:00+10:00`
- Commit: `1722881`

### Outcome and scope
Detect when a rubric criterion crosses a band and trigger specific praise naming the real improvement.

### Acceptance criteria
- [x] A criterion band crossing is persisted as an event or derived reliably from rubric_score history.
- [x] UI shows a level-up moment tied to the actual criterion change.
- [x] Message references the improvement mechanism, not generic praise only.

### Implementation notes
- Likely files or components: backend/app/api/routes.py, backend/app/models.py, frontend/src/components/ProgressView.tsx.
- Constraints: do not invent progress; only celebrate observed rubric_score changes.

### Verification
- [x] `cd backend && uv run pytest` — 212 passed, 4 skipped (was 200/4; +12 new in tests/test_level_ups.py).
- [x] `cd frontend && npm run build` — tsc + vite build clean (377.61 kB bundle); `npm run lint` (oxlint) 0 warnings, 0 errors.

### Completion evidence
- New `backend/app/level_ups.py`: `build_level_ups(db, student_id)` derives band crossings from persisted `RubricScore` history — **derived, not stored**, mirroring the ISS-016 streak decision (one source of truth: the celebration can never disagree with the A–E record). Rule: a level-up fires when a criterion reaches a **personal-best band** (A–E letter; `+`/`-` modifiers ignored via `band_of`), so within-band moves (C → C+) and re-crossings after a dip (C → B → C → B) never re-celebrate — only observed, first-arrival progress counts. Each event carries criterion, from/to level strings, the rubric **note recorded with the new score** (the improvement mechanism), scored_at, session_id, feedback_id; events returned oldest first. Unparseable levels are skipped.
- New route `GET /api/students/{id}/level-ups` → `LevelUpsOut` (404 on unknown student). No schema change, no migration.
- Frontend: `LevelUpCard` in ProgressView (populated state, above the criterion chips) renders the most recent crossing — `🎉 Level up — <criterion>: <from> → <to>` plus the rubric note line, so the message names the real change and its mechanism rather than generic praise. `getLevelUps` client + `LevelUpOut`/`LevelUpsOut` types; a level-ups fetch failure never blocks the chart (same gentle add-on pattern as motivation). `.levelup-card` styles reuse existing tokens.
- Tests (`backend/tests/test_level_ups.py`, 12 new): band normalisation incl. modifiers/unknown strings, cold start, single score is not a crossing, D→C event carries note + ids, C+→B– modifier crossing counts, C→C+ within-band does not, dip-and-recovery does not re-celebrate, unparseable levels skipped, per-criterion isolation with oldest-first order, HTTP cold-start shape, 404, and an endpoint test that writes a crossing to the app's own DB and asserts the served payload.
- Verification detail: full suite 212 passed/4 skipped; `ruff check .` clean (one W292 fixed by `--fix`, suite re-run green after); `mypy app tests` — 29 errors in the same 4 unrelated baseline test files (test_config, test_delete_student, test_interaction_log, test_session_time), changed files clean; frontend tsc+vite build clean, oxlint 0/0. HTTP smoke against a real backend (FakeProvider, tmp SQLite, throwaway script): cold start empty → 404 unknown student → D→C crossing inserted into the same DB served with from/to + mechanism note.
- Tracker hygiene this run: the Issue Index row for ISS-016 still said `READY` although its authoritative detail block (and MEMORY.md) recorded `DONE` at 2026-08-21T04:55; the index row was corrected to `DONE`.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B4.2; PRD: §5 North Star metric; ERD: rubric_score` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-21T07:10:00+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-21T07:12:00+10:00 - DONE. Criterion level-up celebration shipped: `app/level_ups.py` derives personal-best band crossings from rubric_score history (modifiers ignored, no re-celebration after dips), `GET /students/{id}/level-ups`, LevelUpCard in ProgressView naming the criterion, from → to, and the rubric note (improvement mechanism). Verification: full suite 212 passed/4 skipped (+12 new); ruff clean; mypy unchanged vs baseline; frontend build + oxlint clean; HTTP smoke green (cold start → 404 → crossing served with note). Unlocks ISS-018.

## ISS-018 - Coach persona tone setting
- Status: `DONE`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-017`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B4.3; PRD: §9 GA profile direction; ERD: student`
- Effort: `S`
- Attempt: `1`
- Started: `2026-08-21T09:22:39+10:00`
- Completed: `2026-08-21T09:45:49+10:00`
- Commit: `6da6dbd`

### Outcome and scope
Add a per-profile coach tone setting that changes system-prompt tone without changing teaching output contracts.

### Acceptance criteria
- [x] Profile supports a tone setting such as warm, strict, or humorous.
- [x] Same input yields perceptibly different tone while preserving skill output contract.
- [x] Tests assert contract fields remain present.

### Implementation notes
- Likely files or components: backend/app/models.py, backend/app/skills/executor.py, frontend/src/components/ProfileView.tsx.
- Constraints: tone is prompt-level only; never changes rubric levels, next-step bounds, or guardrails.

### Verification
- [x] `cd backend && uv run pytest tests/test_student_profile.py tests/test_skill_executor.py` — 46 passed, 1 skipped.
- [x] `cd frontend && npm run build` — tsc + vite build clean (378.56 kB bundle); `npm run lint` (oxlint) 0 warnings, 0 errors.
- [x] `cd backend && uv run pytest` — 225 passed, 4 skipped (was 212/4 at ISS-017; +13 new tests).
- [x] `cd backend && uv run ruff check .` — clean; `uv run mypy app tests` — 29 errors in the same 4 unrelated test files as the ISS-017 baseline (test_config, test_delete_student, test_interaction_log, test_session_time); changed files clean.
- [x] `cd backend && LLM_PROVIDER=fake uv run python -m app.eval --no-judge` — 26 cases, 22 passed / 4 failed (the same canned-fake diagnose-errors route-line ×2 + give-feedback metacognitive-prompt ×2 baseline; unchanged).

### Completion evidence
- `Student.coach_tone` column (`warm`/`strict`/`humorous`, default `warm`; `CoachTone` Literal in models.py is the single source of truth, imported by schemas) plus idempotent `_ensure_student_coach_tone_column` SQLite patch for existing DBs (same pattern as `weekly_goal`). `StudentCreate`/`StudentUpdate` validate the tone (422 on invalid); `StudentOut` exposes it.
- Executor: `COACH_TONE_DIRECTIVES` + a contract note ("never what you teach: rubric levels, the bounded next-step count, and every output-contract field… stay exactly as specified"). A `coach_tone` input appends a `--- Coach tone ---` section to the **system prompt** and is popped from the user message. Opt-in by design: no `coach_tone` input → no tone section, so eval fixtures and the year-8 analytical byte-identical regression guard stay byte-identical. Unknown tones fall back to warm.
- Loop wiring: `InteractiveLoop._base_inputs`/`start()`/`run_baseline`/`run_weekly_mock` and `SessionOrchestrator.run_daily_loop` (base + coach inputs) all pass the student's tone, so every tutor turn — retrieval, criteria, model, guided, independent, diagnosis, coach, feedback, baseline, mock — runs in the profile's tone.
- Export/import: export carries `coach_tone`; import validates it (400 on invalid) and defaults pre-ISS-018 exports to warm.
- Frontend: ProfileView gains a Coach tone chip group (Warm/Strict/Humorous with one-line hints) in create/edit and shows the tone in the saved view; types updated. FirstRunWizard intentionally unchanged — wizard-created profiles default to warm and can change tone any time in Profile.
- Tests (+13): executor — directive injection per tone, same-input/different-tone identical output contract, unknown→warm fallback, no-tone→no-tone-section; profile API — default warm, create+update round-trip, 422 on invalid; orchestrator — strict-tone loop: every turn's system prompt carries the strict directive + contract note, tone never leaks into the user message, and the same 5 rubric criterion names/levels persist as the default-tone loop (contract fields present); transfer — round-trip preserves tone, older export defaults warm, invalid rejected.
- Live LLM tone perception was not run (no API credential in this environment); "perceptibly different tone" is evidenced by per-tone distinct system prompts (test asserts 3 distinct prompts) and the unchanged contract at the loop level. A live tone check is a pre-beta follow-up alongside the existing live-eval follow-ups.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B4.3; PRD: §9 GA profile direction; ERD: student` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-21T09:22:39+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-21T09:45:49+10:00 - DONE. Coach persona tone shipped: per-profile warm/strict/humorous setting injected into the system prompt only (opt-in input → byte-identical legacy/eval prompts), wired through every tutor turn in both loops, validated end-to-end (422/400 on invalid), export/import round-trip safe, ProfileView tone picker. Verification: declared tests 46 passed/1 skipped; full suite 225 passed/4 skipped (+13); ruff clean; mypy unchanged vs baseline; frontend build + oxlint clean; no-judge eval 26 cases 22/4 — unchanged canned-fake baseline. Unlocks ISS-019.

## ISS-019 - Weekly parent report with privacy boundary
- Status: `DONE`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-018`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B5.1; PRD: §7 deferred parent layer; ERD: Privacy & retention`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-21T11:50:00+10:00`
- Completed: `2026-08-21T12:15:00+10:00`
- Commit: `ad34aef`

### Outcome and scope
Add an in-app weekly parent report and printable PDF showing sessions, time, criterion trends, highlight, and next-week suggestion without exposing full essay text by default.

### Acceptance criteria
- [x] Parent endpoints return trends/levels/time/goals but no attempt full text.
- [x] Printable report generates from the same data.
- [x] Tests assert the privacy boundary.

### Implementation notes
- Likely files or components: backend/app/api/routes.py, backend/app/api/schemas.py, frontend/src/components/ProgressView.tsx or new ParentView.
- Constraints: D3 remains in force: parents see trends, not full essays, unless the student explicitly shares.

### Verification
- [x] `cd backend && uv run pytest tests/test_parent_report.py` — 12 passed.
- [x] `cd backend && uv run pytest` — 237 passed, 4 skipped (was 225/4; +12 new tests).
- [x] `cd backend && uv run ruff check .` — clean; `uv run mypy app tests` — 29 errors in the same 4 unrelated test files as the ISS-018 baseline (test_config, test_delete_student, test_interaction_log, test_session_time); changed files clean.
- [x] `cd frontend && npm run build` — tsc + vite build clean (382.27 kB bundle); `npm run lint` (oxlint) — 0 warnings, 0 errors.
- [x] HTTP smoke against a real backend (`LLM_PROVIDER=fake`, tmp SQLite): create student → start session → `GET /parent-report` 200 with correct weekly counts and goal nudge; `GET /parent-report/print` 200 `text/html` with the same data and the print-to-PDF button.

### Completion evidence
- New `backend/app/parent_report.py`: `build_parent_report()` derives the report from persisted sessions + rubric scores (nothing extra stored, mirroring the derived-streak decision): Monday–today local week window (matching `build_motivation`), sessions/practice-time counts, weekly-goal state, per-criterion trends (latest/previous level, up/down/steady/new direction, dated points), one honest highlight (this week's level-up, else goal-met), one supportive next-week suggestion (goal nudge → dip revisit → weakest growth area → keep going). `render_parent_report_html()` renders the printable one-page report from the same `ParentReport` value with every interpolation HTML-escaped and a print-to-PDF button (`@media print` hides it).
- D3 privacy boundary enforced in exactly one place: the builder reads `Attempt`/`Feedback` only to reach rubric scores — no `student_text`, `task_prompt`, feedback prose, or rubric notes ever leave the module; the print page states the boundary to parents.
- Routes: `GET /api/students/{id}/parent-report` (JSON `ParentReportOut`) and `GET /api/students/{id}/parent-report/print` (HTMLResponse), both 404 on unknown student; no new persistence.
- Frontend: new `ParentView.tsx` on a new **Parent** tab (week strip, highlight card, criterion-trend table, next-week suggestion, privacy note, Print/PDF button opening the server-rendered print page); `types.ts` + `api.ts` (`getParentReport`, `parentReportPrintUrl`) + `.parent-*` CSS tokens.
- Tests (`backend/tests/test_parent_report.py`, 12 new): cold start, week-window session/time counts (last week excluded), trend latest/previous/direction, highlight prefers this-week level-up over goal-met fallback and ignores last-week crossings, suggestion ordering (dip after goal met, weakest criterion when no dip), builder-level no-secret-text assertion, HTTP shape, 404s, **JSON and print privacy-boundary tests asserting marker essay/feedback/note/prompt strings never appear**, print page carries the same data + print button.
- PDF decision: no new dependency — the server-rendered printable HTML is the single source; the browser prints/saves to PDF. Report is derived, so PDFs never disagree with the app.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B5.1; PRD: §7 deferred parent layer; ERD: Privacy & retention` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-21T11:50:00+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-21T12:15:00+10:00 - DONE. Weekly parent report shipped: `build_parent_report` (derived weekly window, sessions/time, criterion trends, highlight, next-week suggestion) + JSON and printable-HTML endpoints with the D3 privacy boundary enforced in one module + Parent tab UI with print-to-PDF. Verification: targeted 12 passed; full suite 237 passed/4 skipped; ruff clean; mypy unchanged vs baseline; frontend build + oxlint clean; HTTP smoke of both endpoints green. Unlocks ISS-020.

## ISS-020 - Shared parent-student goal setting
- Status: `DONE`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-019`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B5.2; PRD: §7 deferred parent layer; ERD: student/session`
- Effort: `S`
- Attempt: `1`
- Started: `2026-08-21T14:14:19+10:00`
- Completed: `2026-08-21T14:30:00+10:00`
- Commit: `2ea3f64`

### Outcome and scope
Let parent and student set a weekly goal together and surface it at the start of the session loop.

### Acceptance criteria
- [x] Weekly goal is stored on the student profile or related goal record.
- [x] Session opening references the shared goal.
- [x] Goal edits are visible in the parent/student views according to the privacy boundary.

### Implementation notes
- Likely files or components: backend/app/models.py, backend/app/api/routes.py, backend/app/sessions/interactive.py, frontend/src/components/ProfileView.tsx.
- Constraints: keep goal supportive and lightweight; do not add surveillance-style controls.

### Verification
- [x] `cd backend && uv run pytest` — 242 passed, 4 skipped (was 237/4; +5 new tests); `uv run ruff check .` clean; `uv run mypy app tests` 29 errors in the same 4 unrelated test files as the ISS-019 baseline (test_config, test_delete_student, test_interaction_log, test_session_time); changed files clean.
- [x] `cd frontend && npm run build` — tsc + vite build clean (383.31 kB bundle); `npm run lint` (oxlint) — 0 warnings, 0 errors.

### Completion evidence
- `student.shared_goal` (nullable VARCHAR(280)) stores the family's shared weekly goal; idempotent SQLite column patch `_ensure_student_shared_goal_column` keeps existing dev/LAN databases. API: `shared_goal` on StudentCreate/StudentUpdate/StudentOut — create strips blank to None; PATCH `""` clears, an omitted field leaves the goal unchanged.
- Session opening: `InteractiveLoop.start()` injects `shared_goal` into both opening skill inputs (spaced-review + set-success-criteria) only when set, so goal-less openings stay byte-identical; the ChatView start card also shows "This week's shared goal" before the session begins.
- Privacy boundary: the goal is visible in the parent report (JSON `shared_goal` field, printable chip, Parent tab UI chip) because it is a goal, not student content — the D3 marker tests are unchanged and green. Student view: Profile tab saved row + edit field.
- Export/restore: `shared_goal` round-trips through student export/import; older exports without the key import as None (format version unchanged).
- Tests: new `test_shared_goal_defaults_to_none_and_round_trips`, `test_session_opening_references_shared_goal` (both opening prompts carry the goal; goal-less prompts omit the key), `test_parent_report_carries_shared_goal` (JSON + print + no-goal cases), `test_export_import_round_trip_preserves_shared_goal`, `test_import_older_export_without_shared_goal_defaults_none`.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B5.2; PRD: §7 deferred parent layer; ERD: student/session` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-21T14:14:19+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-21T14:30:00+10:00 - DONE. Shared parent-student weekly goal shipped: `student.shared_goal` + profile API (set/edit/clear), session-opening prompts reference it (spaced-review + set-success-criteria inputs, byte-identical when unset), ChatView start card shows it, parent report (JSON/print/UI) carries it inside the D3 boundary, and it survives export/import. Verification: full suite 242 passed/4 skipped (+5 new tests); ruff clean; mypy unchanged vs baseline; frontend build + oxlint clean. Unlocks ISS-021.

## ISS-021 - Per-stage model routing
- Status: `DONE`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-020`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B6.1; PRD: §6 model-swappable; ERD: interaction_log`
- Effort: `M`
- Attempt: `1`
- Started: `2026-08-21T16:31:48+10:00`
- Completed: `2026-08-21T16:44:07+10:00`
- Commit: `2d8892c`

### Outcome and scope
Add config-driven per-stage model routing so heavy judgement stages can use stronger models and light stages can use cheaper tiers.

### Acceptance criteria
- [x] Routing table is configurable by loop_stage.
- [x] Tests assert the factory/executor picks the expected provider per stage.
- [x] Interaction logs record the actual model used.

### Implementation notes
- Likely files or components: backend/app/config.py, backend/app/llm/factory.py, backend/app/skills/executor.py, backend/app/sessions/interactive.py.
- Constraints: business logic remains provider-agnostic; routing must not change skill contracts.

### Verification
- [x] `cd backend && uv run pytest tests/test_llm.py tests/test_config.py tests/test_skill_executor.py` — 59 passed, 3 skipped (62 passed/3 skipped including tests/test_interaction_log.py).
- [x] `cd backend && uv run pytest` — 253 passed, 4 skipped (was 242/4; +11 new tests).

### Completion evidence
- `Settings.llm_stage_models: dict[str, str]` (env `LLM_STAGE_MODELS` as a JSON object) is the routing table: loop_stage -> model name override, default empty; documented in `backend/.env.example`.
- New `app/llm/routing.py::StageProviderRouter` resolves and caches a `(provider, model_name)` pair per loop stage through the existing `create_llm_provider` factory (`settings.model_copy(update={"llm_model": ...})`); unmapped stages fall back to the default model. Routing stays within the configured provider family (one API key) — only the model tier changes per stage.
- `SkillExecutionService` gains optional `stage_router`: `execute()` picks the stage provider via `_provider_for(skill)`; `model_used_for(skill)` reports the actual model for logging. No router -> legacy single-provider behaviour, byte-identical prompts; skill contracts untouched.
- `app/api/deps.py::get_executor` attaches a router only when the routing table is non-empty (opt-in), so tests overriding `get_provider` and the eval harness (`app/eval/__main__.py`, router-free) behave exactly as before.
- `InteractiveLoop._log_interaction` now records `executor.model_used_for(skill)` — the per-stage model actually used.
- Tests (+11): config default-empty + env-JSON parsing (2); router default/override/caching/real-provider model override (4); `get_executor` opt-in behaviour (2); executor routes to the stage provider and reports the stage model (2); InteractionLog rows record per-stage models (`fake-light` retrieval override vs `fake-base` default) (1). One mid-run defect found and fixed: unconditional router wiring bypassed provider dependency overrides (22 API-test failures) — routing made opt-in, suite back to green.
- Full suite 253 passed/4 skipped; ruff clean; mypy `app` clean; mypy on the four touched test files = 12 errors, byte-identical to the pre-change baseline (stash-verified). Frontend untouched (no build needed).
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B6.1; PRD: §6 model-swappable; ERD: interaction_log` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-21T16:31:48+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-21T16:44:07+10:00 - DONE. Per-stage model routing shipped: `LLM_STAGE_MODELS` routing table + `StageProviderRouter` + opt-in executor wiring + per-stage model recorded in interaction_log. Verification: targeted 59 passed/3 skipped (62/3 with interaction-log tests); full suite 253 passed/4 skipped; ruff clean; mypy unchanged vs baseline. Unlocks ISS-022.

## ISS-022 - Privacy-safe telemetry and feedback package
- Status: `DONE`
- Priority: `P2`
- Type: `feature`
- Depends on: `ISS-021`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B6.2; PRD: §6 privacy; ERD: Privacy & retention`
- Effort: `S`
- Attempt: `1`
- Started: `2026-08-21T18:51:32+10:00`
- Completed: `2026-08-21T19:05:00+10:00`
- Commit: `10c5f2e`

### Outcome and scope
Add local aggregated usage metrics with no student content and a one-click feedback package export for beta families.

### Acceptance criteria
- [x] Telemetry excludes student writing and LLM content.
- [x] Feedback package bundles logs/config/metadata needed to diagnose a beta issue.
- [x] A beta issue can be diagnosed from the package in under 10 minutes.

### Implementation notes
- Likely files or components: backend/app/api/routes.py, backend/app/eval or backend/app/ops, frontend/src/components/ProfileView.tsx.
- Constraints: privacy-safe by default; no third-party analytics on student content.

### Verification
- [x] `cd backend && uv run pytest` — 262 passed, 4 skipped (was 253/4 at ISS-021; +9 new tests in tests/test_telemetry.py).
- [x] `cd frontend && npm run build` — tsc + vite build clean (383.85 kB bundle); `npm run lint` (oxlint) — 0 warnings, 0 errors.
- [x] `cd backend && uv run ruff check .` — clean; `uv run mypy app tests` — 29 errors in the same 4 unrelated test files as the ISS-021 baseline (test_config, test_delete_student, test_interaction_log, test_session_time); changed files clean (one new no-any-return found and fixed during the run).

### Completion evidence
- New `backend/app/telemetry.py`: `build_telemetry(db, student)` aggregates counts/totals/timestamps only — sessions/attempts/feedback/rubric-score totals, attempts by mode and by skill name, practice seconds, LLM calls by model and by skill, `llm_empty_output_calls` (the classic "feedback never arrived" symptom), first/last activity. `build_feedback_package(db, student, settings)` bundles the telemetry plus `environment` (app/python/fastapi/sqlalchemy versions, platform, loaded skill names), redacted non-secret `config` (provider, model, stage models, time budget, DB **dialect only** — `llm_api_key` never touched), `student_context` (year level/curriculum/focus types/tone/goal — **deliberately no name** so the package is safe to email), `recent_sessions` (last 10: stage/timing/paused, learning intention excluded) and `recent_interactions` (last 20: model/skill/timestamps + input/output **character lengths**, never text).
- Routes: `GET /api/students/{id}/telemetry` and `GET /api/students/{id}/feedback-package` (downloadable JSON attachment, 404 on unknown student), following the ISS-011 export pattern.
- Frontend: ProfileView gains a **Report a problem** button (same anchor-download pattern as Export) with an explainer that the package carries counts/settings/device info only — never writing, tutor responses, or even the student's name.
- Privacy boundary enforced by tests: `test_feedback_package_never_contains_student_content` plants distinctive markers in every content-bearing field (name, essay, task prompt, feedback prose, rubric note, log input/output, learning intention) and asserts none survive `json.dumps(package)`; `test_feedback_package_has_no_student_name_in_telemetry_endpoint_shape` does the same for telemetry alone; HTTP test asserts a created student's name never appears in the endpoint response body.
- The <10-minute diagnosis criterion is operationalised by a new README "Reporting a beta issue" section: what's inside, and a 5-step reading order (config drift → empty-output count → stalled session stage → interaction lengths → environment versions).
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B6.2; PRD: §6 privacy; ERD: Privacy & retention` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-21T18:51:32+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-21T19:05:00+10:00 - DONE. Privacy-safe telemetry + feedback package shipped: `app/telemetry.py` aggregation module, `/telemetry` + `/feedback-package` endpoints, ProfileView "Report a problem" download, README 10-minute diagnosis checklist. Privacy boundary (no writing, no LLM content, no name, no credentials) enforced by marker-string regression tests. Verification: full suite 262 passed/4 skipped; ruff clean; mypy unchanged vs baseline; frontend build + oxlint clean. Unlocks ISS-023.

## ISS-023 - Beta handbook
- Status: `DONE`
- Priority: `P2`
- Type: `chore`
- Depends on: `ISS-022`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: B6.3; PRD: §9 GA direction; ERD: Deployment/migration`
- Effort: `S`
- Attempt: `1`
- Started: `2026-08-21T21:04:51+10:00`
- Completed: `2026-08-21T21:08:48+10:00`
- Commit: `c868be9`

### Outcome and scope
Write the beta handbook: install guide, parent one-pager, feedback channel, and weekly check-in template.

### Acceptance criteria
- [x] A non-technical parent can install from the guide alone.
- [x] Handbook includes privacy expectations and feedback channel.
- [x] Weekly check-in template exists for beta families.

### Implementation notes
- Likely files or components: docs or root markdown files, README.md, DEPLOYMENT.md.
- Constraints: keep Beta per-family local install; do not describe unsupported hosted GA features as available.
- Decision (Q-002, answered 2026-08-21): beta recruitment channel is friend families first; tone the handbook for known families with fast feedback; school parent group expansion waits until B1-B3 are stable.

### Verification
- [x] Manual check: follow the guide on a clean machine profile or review against DEPLOYMENT.md — every command/path reviewed against `DEPLOYMENT.md` + `README.md`: `cp backend/.env.example backend/.env`, `docker compose up -d --build`, 3–8 min first build, `<15 min` to first session, `WEB_PORT=8080` fallback, `http://localhost/health`, `docker compose down -v` data wipe, no-auth LAN boundary. All match.
- [x] `cd backend && uv run pytest` — 262 passed, 4 skipped (docs-only change; matches the ISS-022 baseline exactly).

### Completion evidence
- New root doc `BETA-HANDBOOK.md` (English, friend-family tone per Q-002): §1 parent one-pager (what the tutor does, the 15-minute daily loop, what it never does — no ghostwriting, beta honesty, Year 8–10 QCAA coverage in this beta); §2 install guide written for a non-technical parent (Docker Desktop install, unzip project, copy/rename `backend/.env`, paste `LLM_API_KEY`, one `docker compose up -d --build`, browser + first-run wizard) with an everyday-use table, a troubleshooting table mirroring DEPLOYMENT.md symptoms, and full uninstall steps; §3 privacy expectations (all data stays on the family machine, the only outbound traffic is student writing to the LLM API per PRD §6, no login = family device only, delete any time, feedback package contains no writing — boundary enforced by tests); §4 feedback channel (Profile → Report a problem → email the JSON to Cheng, plus direct messages for small stuff, and what feedback is most valuable); §5 weekly check-in template (7 short questions, copy-paste block); closing scope note that hosted accounts/billing are future plans, not this build.
- `README.md` gains a pointer to the handbook for beta families.
- No code changed. No physical clean-machine run was performed in this environment; the install-alone criterion is supported by the command-by-command review against DEPLOYMENT.md/README plus the ISS-010 wizard smoke evidence.
- Commit: recorded in this issue's `Commit` field.

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: B6.3; PRD: §9 GA direction; ERD: Deployment/migration` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-21T14:55:02+10:00 - Q-002 answered by Cheng: friend families first; handbook tone constraint recorded.
- 2026-08-21T21:04:51+10:00 - `develop` attempt 1 started on `feature/english-tutor-delivery`; gate `OPEN`, no blocking questions.
- 2026-08-21T21:08:48+10:00 - DONE. `BETA-HANDBOOK.md` shipped: parent one-pager, non-technical install guide, privacy expectations, feedback channel, weekly check-in template; README links to it. Verification: manual command-by-command review against DEPLOYMENT.md/README (all match); full backend suite 262 passed/4 skipped — docs-only change, baseline unchanged. Unlocks ISS-024.

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
- Decision (Q-001, answered 2026-08-21): official QCAA syllabus/source PDFs must be imported and cited directly before this issue (and ISS-025) can be marked complete; derived descriptors from existing research files are not sufficient for senior depth claims.

### Verification
- [ ] `cd backend && uv run pytest tests/test_seed.py`
- [ ] Manual check: mapping note cites sources and matches curriculum_outcome seed shape

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 10.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome` during `/plan`; completed milestones were kept as context, not tickets.
- 2026-08-21T14:55:02+10:00 - Q-001 answered by Cheng: import official QCAA syllabus PDFs first; sourcing constraint recorded.

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
