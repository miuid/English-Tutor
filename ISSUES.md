# Delivery Backlog

This document is the canonical delivery state for autonomous development. Detailed issue blocks are authoritative; the index is a convenience summary.

## Delivery Gate
- State: `OPEN`
- Blocking questions: `None`
- Reason: No `BLOCKING` questions are open; completed P0-P5/P6.1/P6.2 work is recorded as context only, not as tickets.
- Active issue: `None`
- Integration mode: `delivery-branch`
- Delivery branch: `feature/english-tutor-delivery`
- Last evaluated: `2026-08-19T13:44:45+10:00`

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
| ISS-001 | Eval fixture matrix by year band and text type | `READY` | `P0` | `None` | `None` |
| ISS-002 | Year 9-10 analytical reference packs | `READY` | `P0` | `ISS-001` | `None` |
| ISS-003 | Seed and evaluate Year 9-10 analytical loop | `READY` | `P0` | `ISS-002` | `None` |
| ISS-004 | Persuasive reference packs for Year 8-10 | `READY` | `P1` | `ISS-003` | `None` |
| ISS-005 | New skill strengthen-argument | `READY` | `P1` | `ISS-004` | `None` |
| ISS-006 | Seed and wire persuasive daily loop | `READY` | `P1` | `ISS-005` | `None` |
| ISS-007 | Imaginative reference packs for Year 8-10 | `READY` | `P1` | `ISS-006` | `None` |
| ISS-008 | New skill craft-voice | `READY` | `P1` | `ISS-007` | `None` |
| ISS-009 | Seed and wire imaginative daily loop | `READY` | `P1` | `ISS-008` | `None` |
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
- Status: `READY`
- Priority: `P0`
- Type: `chore`
- Depends on: `None`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 6.3; PRD: §5 North Star metric; ERD: Key queries/Replay-eval`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Extend the eval harness so one skill can ship multiple golden fixtures tagged by year band and text type, and the scorecard groups results by combo.

### Acceptance criteria
- [ ] A skill can provide multiple fixtures with band/text_type frontmatter.
- [ ] Scorecard output groups pass/fail results by skill and by band/text_type combo.
- [ ] Existing Year 8 analytical fixtures still run unchanged.

### Implementation notes
- Likely files or components: backend/app/eval/fixtures.py, backend/app/eval/runner.py, backend/app/eval/scorecard.py, skills/*/examples/.
- Constraints: preserve current fixture discovery behaviour for untagged Year 8 analytical examples; no live LLM required for plumbing tests.

### Verification
- [ ] `cd backend && uv run pytest tests/test_eval_fixtures.py tests/test_eval_runner.py tests/test_eval_rules.py`
- [ ] `cd backend && uv run python -m app.eval --no-judge`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 6.3; PRD: §5 North Star metric; ERD: Key queries/Replay-eval` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-002 - Year 9-10 analytical reference packs
- Status: `READY`
- Priority: `P0`
- Type: `research`
- Depends on: `ISS-001`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 9.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Add analytical reference packs for year-9-10 across the existing skills, with band-adjusted rubric descriptors, vocabulary ceilings, task specs, and register transition.

### Acceptance criteria
- [ ] references/analytical/year-9-10/ exists for the relevant skills.
- [ ] Pack content traces to research files rather than intuition.
- [ ] Each core skill gains at least one year-9-10 golden fixture.

### Implementation notes
- Likely files or components: skills/*/references/analytical/year-9-10/, skills/*/examples/, reaserch.md, Queensland English Tutoring Blueprint.md.
- Constraints: keep skills generic; content depth lives in reference packs; do not change Year 8 analytical behaviour.

### Verification
- [ ] `cd backend && uv run pytest tests/test_skill_loader.py tests/test_skill_executor.py`
- [ ] `cd backend && uv run python -m app.eval --no-judge`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 9.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-003 - Seed and evaluate Year 9-10 analytical loop
- Status: `READY`
- Priority: `P0`
- Type: `feature`
- Depends on: `ISS-002`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 9.2; PRD: §5 North Star metric; ERD: curriculum_outcome/rubric_score`
- Effort: `S`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Seed Year 9-10 QCAA analytical outcomes and prove a year_level=9 session can run the loop with Year 9 descriptors cited in feedback.

### Acceptance criteria
- [ ] Year 9-10 QCAA analytical outcomes are seeded idempotently.
- [ ] A year_level=9 analytical session runs end-to-end with FakeProvider in tests.
- [ ] Rubric scores persist for a graded Year 9 attempt.

### Implementation notes
- Likely files or components: backend/app/seed.py, backend/seed.py, backend/tests/test_seed.py, backend/tests/test_session_orchestrator.py, backend/tests/test_api_daily_loop.py.
- Constraints: keep seed idempotent; do not broaden to persuasive/imaginative yet.

### Verification
- [ ] `cd backend && uv run pytest tests/test_seed.py tests/test_session_orchestrator.py tests/test_api_daily_loop.py`
- [ ] `cd backend && uv run pytest`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 9.2; PRD: §5 North Star metric; ERD: curriculum_outcome/rubric_score` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-004 - Persuasive reference packs for Year 8-10
- Status: `READY`
- Priority: `P1`
- Type: `research`
- Depends on: `ISS-003`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 7.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Create persuasive reference packs covering argument structure, rhetorical devices by band, QCAA persuasive A-E descriptors, and task specs.

### Acceptance criteria
- [ ] Persuasive packs exist for the relevant skills and year bands.
- [ ] Every pedagogical claim traces to a research source file.
- [ ] Pack selection falls back safely when an exact combo is missing.

### Implementation notes
- Likely files or components: skills/*/references/persuasive/, reaserch.md, Queensland English Tutoring Blueprint.md, backend/app/skills/executor.py.
- Constraints: no copyrighted set texts; use public-domain or generated stimulus only.

### Verification
- [ ] `cd backend && uv run pytest tests/test_skill_loader.py tests/test_skill_executor.py`
- [ ] `cd backend && uv run python -m app.eval --no-judge`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 7.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-005 - New skill strengthen-argument
- Status: `READY`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-004`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 7.2; PRD: §3 bounded feedback; ERD: skill registry`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Add the ninth agent skill strengthen-argument to diagnose weak argument chains and coach the fix within the global guardrails.

### Acceptance criteria
- [ ] skills/strengthen-argument/ follows skills/README.md convention.
- [ ] Golden examples exist and are discovered by the eval harness.
- [ ] diagnose-errors can route persuasive submissions to strengthen-argument.

### Implementation notes
- Likely files or components: skills/strengthen-argument/, backend/app/skills/router.py, backend/tests/test_diagnosis_router.py, backend/tests/test_skill_sync.py.
- Constraints: coach do not ghostwrite; bounded feedback max 1-2 next steps; model-agnostic skill package.

### Verification
- [ ] `cd backend && uv run pytest tests/test_diagnosis_router.py tests/test_skill_loader.py tests/test_skill_sync.py`
- [ ] `cd backend && uv run python -m app.eval --skill strengthen-argument --no-judge`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 7.2; PRD: §3 bounded feedback; ERD: skill registry` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-006 - Seed and wire persuasive daily loop
- Status: `READY`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-005`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 7.3; PRD: §4 daily-loop UX; ERD: session/attempt/rubric_score`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Seed persuasive outcomes and run the full daily loop with text_type=persuasive, persisting rubric scores.

### Acceptance criteria
- [ ] Persuasive curriculum outcomes are seeded idempotently.
- [ ] A persuasive session can start, advance, submit, and receive feedback over HTTP.
- [ ] Rubric scores persist for a persuasive graded attempt.

### Implementation notes
- Likely files or components: backend/app/seed.py, backend/app/sessions/interactive.py, backend/app/api/routes.py, backend/tests/test_api_daily_loop.py.
- Constraints: keep analytical Year 8 loop unchanged; unsupported combos fail clearly.

### Verification
- [ ] `cd backend && uv run pytest tests/test_seed.py tests/test_api_daily_loop.py`
- [ ] `cd backend && uv run pytest`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 7.3; PRD: §4 daily-loop UX; ERD: session/attempt/rubric_score` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-007 - Imaginative reference packs for Year 8-10
- Status: `READY`
- Priority: `P1`
- Type: `research`
- Depends on: `ISS-006`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 8.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Create imaginative reference packs for narrative structure, character/setting/POV, show-don't-tell, sensory imagery, and QCAA imaginative descriptors.

### Acceptance criteria
- [ ] Imaginative packs exist for the relevant skills and year bands.
- [ ] Every pedagogical claim traces to a research source file.
- [ ] Pack selection falls back safely when an exact combo is missing.

### Implementation notes
- Likely files or components: skills/*/references/imaginative/, reaserch.md, Queensland English Tutoring Blueprint.md, backend/app/skills/executor.py.
- Constraints: age-appropriate and curriculum-anchored; no ghostwritten story output as the teaching result.

### Verification
- [ ] `cd backend && uv run pytest tests/test_skill_loader.py tests/test_skill_executor.py`
- [ ] `cd backend && uv run python -m app.eval --no-judge`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 8.1; PRD: §9 FR-GA-003; ERD: curriculum_outcome` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-008 - New skill craft-voice
- Status: `READY`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-007`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 8.2; PRD: §3 bounded feedback; ERD: skill registry`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Add the tenth agent skill craft-voice to diagnose telling-vs-showing, thin imagery, and POV drift, then coach the fix.

### Acceptance criteria
- [ ] skills/craft-voice/ follows skills/README.md convention.
- [ ] Golden examples exist and are discovered by the eval harness.
- [ ] diagnose-errors can route imaginative submissions to craft-voice.

### Implementation notes
- Likely files or components: skills/craft-voice/, backend/app/skills/router.py, backend/tests/test_diagnosis_router.py, backend/tests/test_skill_sync.py.
- Constraints: coach do not ghostwrite; bounded feedback max 1-2 next steps; model-agnostic skill package.

### Verification
- [ ] `cd backend && uv run pytest tests/test_diagnosis_router.py tests/test_skill_loader.py tests/test_skill_sync.py`
- [ ] `cd backend && uv run python -m app.eval --skill craft-voice --no-judge`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 8.2; PRD: §3 bounded feedback; ERD: skill registry` during `/plan`; completed milestones were kept as context, not tickets.

## ISS-009 - Seed and wire imaginative daily loop
- Status: `READY`
- Priority: `P1`
- Type: `feature`
- Depends on: `ISS-008`
- Blocks: `None`
- Blocked by: `None`
- Branch: `<inherit delivery branch>`
- Sources: `IMPLEMENTATION-PLAN-2: 8.3; PRD: §4 daily-loop UX; ERD: session/attempt/rubric_score`
- Effort: `M`
- Attempt: `0`
- Started: `None`
- Completed: `None`
- Commit: `None`

### Outcome and scope
Seed imaginative outcomes and run the full daily loop with text_type=imaginative, persisting rubric scores.

### Acceptance criteria
- [ ] Imaginative curriculum outcomes are seeded idempotently.
- [ ] An imaginative session can start, advance, submit, and receive feedback over HTTP.
- [ ] Rubric scores persist for an imaginative graded attempt.

### Implementation notes
- Likely files or components: backend/app/seed.py, backend/app/sessions/interactive.py, backend/app/api/routes.py, backend/tests/test_api_daily_loop.py.
- Constraints: keep analytical and persuasive loops unchanged; unsupported combos fail clearly.

### Verification
- [ ] `cd backend && uv run pytest tests/test_seed.py tests/test_api_daily_loop.py`
- [ ] `cd backend && uv run pytest`

### Completion evidence
- Pending

### Work log
- 2026-08-19T13:44:45+10:00 - Planned from `IMPLEMENTATION-PLAN-2: 8.3; PRD: §4 daily-loop UX; ERD: session/attempt/rubric_score` during `/plan`; completed milestones were kept as context, not tickets.

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
