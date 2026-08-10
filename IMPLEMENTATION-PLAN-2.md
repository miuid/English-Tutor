# English Tutor — Phase 2 Implementation Plan (Skills Depth + Beta)

> Resumable build checklist for Phase 2. Same resume protocol as `IMPLEMENTATION-PLAN.md`: read `MEMORY.md` → this file → do the first unchecked step → verify → tick → log to MEMORY §11. Planning rationale and decision points live in `PHASE-2-PLAN.md` (D1–D4 confirmed by owner 2026-07-31).

Last updated: 2026-07-31

## Locked decisions (from PHASE-2-PLAN.md §1, owner-confirmed)

- **D1** Beta distribution = per-family local install (docker compose); hosted multi-tenant stays GA.
- **D2** Year 11–12 = framework + IA1 analytical depth only; rest waits for a real senior user.
- **D3** Parent sees trends/levels/time/goals by default, NOT full essays; student can share individual pieces.
- **D4** Order: P6 → P9 → P7 → P8 → B1–B6; P10 timed by beta family mix.

## Architecture being introduced: reference packs

Skills stay generic; content depth lives in `skills/<skill>/references/<text_type>/<year_band>/` (bands: `year-8`, `year-9-10`, `year-11-12`; plus `references/shared/`). The executor injects only the pack matching the session's `(text_type, year_band)`; no match → fall back to `shared/` + nearest band with a degradation note, never an error. Existing Year 8 analytical content migrates to `references/analytical/year-8/` with zero behaviour change.

---

## Milestone 6 — Skill framework generalisation (P6)

- [x] **6.1 Reference-pack convention + loader/executor changes** (L)
  - Goal: loader recursively collects `references/`; executor selects the pack by `(text_type, year_band)`; fallback to `shared/` + nearest band with a degradation note in output; existing Year 8 content migrated, behaviour unchanged.
  - Touches: `skills/*/…` (move reference files), `backend/app/skills/loader.py`, `backend/app/skills/executor.py` (or equivalent), tests.
  - Done when: pytest all green; live eval 8/8 still PASS; a request with a non-existent combo returns a degradation-noted response, not an error.
  - Depends on: —
  - **Done 2026-07-31:** `Skill.packs` (key `"shared"` / `"<text_type>/<band>"`) replaces flat references; all 6 existing reference files migrated to `references/analytical/year-8/`; `year_band_for()` + `select_packs()` with nearest-band fallback + code-appended degradation note; byte-exact prompt regression test proves Year-8 analytical prompts unchanged. pytest 115 passed + 4 skipped (+20 new); ruff/mypy clean (3 ruff errors elsewhere pre-exist at HEAD); live eval 8/8 PASS after tuning give-feedback expected-01 (Understanding C→C/D, explicit C/D acceptance notes — model drift, not regression; E-grading stays a FAIL). Packless skills (guided-practice, model-response) get no degradation note by design.

- [ ] **6.2 Student profile + session context** (M)
  - Goal: `student` gains `year_level` + `focus_text_types`; `POST /api/sessions` injects them into skill inputs (overridable); frontend profile create/edit.
  - Done when: two students with different profiles start sessions whose prompts carry different `year_level`; tests cover it.
  - Depends on: 6.1

- [ ] **6.3 Eval fixture matrix** (M)
  - Goal: a skill can ship multiple fixtures (frontmatter tags band/text_type); scorecard groups by combo.
  - Done when: one skill runs 2 fixtures of different bands and the scorecard groups results.
  - Depends on: 6.1

## Milestone 9 — Year 9–10 analytical depth (P9) ⏰ hard deadline: Feb 2027

- [ ] **9.1 Year 9–10 analytical packs** (M)
  - Goal: `references/analytical/year-9-10/` for all 8 skills: band-adjusted rubric descriptors (A/B = discerning/purposeful…), raised vocab ceilings, longer task specs, register transition from Year 8 voice.
  - Done when: packs trace to `reaserch.md`; each core skill gains a year-9-10 golden fixture.
  - Depends on: 6.1

- [ ] **9.2 Seed + eval** (S)
  - Goal: Year 9–10 QCAA analytical outcomes seeded; live eval green across the matrix.
  - Done when: a `year_level=9` session runs the full loop and A–E judgements cite Year 9 descriptors.
  - Depends on: 9.1, 6.2, 6.3

## Milestone 7 — Persuasive depth, Year 8–10 (P7)

- [ ] **7.1 Persuasive reference packs** (M)
  - Goal: argument structure (thesis → argument blocks → rebuttal → conclusion), band-layered rhetorical device library, QCAA persuasive A–E descriptors, task specs. Traceable to research files.
  - Done when: packs exist for the relevant skills; every claim cites a research source.
  - Depends on: 6.1

- [ ] **7.2 New skill `strengthen-argument`** (M)
  - Goal: 9th skill — diagnoses weak argument chains (claim w/o reason, reason w/o evidence, missing rebuttal), coaches the fix; full `skills/README.md` convention + golden examples; `diagnose-errors` routing table extended.
  - Done when: live eval PASS for the new skill; routing test covers persuasive submissions.
  - Depends on: 7.1

- [ ] **7.3 Seed + loop wiring (persuasive)** (M)
  - Goal: persuasive outcomes seeded; full daily loop runs with `text_type=persuasive`; rubric_score persists.
  - Done when: end-to-end persuasive session + green eval.
  - Depends on: 7.2

## Milestone 8 — Imaginative depth, Year 8–10 (P8)

- [ ] **8.1 Imaginative reference packs** (M)
  - Goal: narrative structure (orientation → complication → climax → resolution), character/setting/POV, show-don't-tell & sensory imagery, QCAA imaginative descriptors.
  - Depends on: 6.1

- [ ] **8.2 New skill `craft-voice`** (M)
  - Goal: 10th skill — diagnoses telling-vs-showing, thin imagery, POV drift; coaches the fix; convention + golden examples; routing table extended.
  - Done when: live eval PASS; routing test covers imaginative submissions.
  - Depends on: 8.1

- [ ] **8.3 Seed + loop wiring (imaginative)** (M)
  - Done when: end-to-end imaginative session + green eval.
  - Depends on: 8.2

## Milestone B1 — Beta distribution & student profiles (M)

- [ ] **B1.1 First-run wizard + profile UX** (M)
  - Goal: clean-machine `docker compose up` → guided first-run (create student profile, pick year, paste school task); profile edit UI (from 6.2 backend).
  - Done when: a clean machine reaches a first session in <15 min following the README.
  - Depends on: 6.2

- [ ] **B1.2 Data export / backup** (S)
  - Goal: one-click local JSON export of a student's full data; import restores progress.
  - Done when: export → delete → import round-trip preserves progress; test covers it.
  - Depends on: 6.2

## Milestone B2 — Baseline assessment (M)

- [ ] **B2.1 New skill `baseline-assessment`** (M)
  - Goal: 11th skill — one 15-min timed write → rubric baseline → generates the student profile (ranked weaknesses, starting A–E, recommended focus loop).
  - Done when: a new student's first use completes a baseline; day-0 rubric_score rows appear in the progress view.
  - Depends on: 6.2

## Milestone B3 — Complete the teaching loop (L)

- [ ] **B3.1 New skill `fix-mechanics`** (M)
  - Goal: 12th skill — grammar/spelling/punctuation coach; third `diagnose-errors` route; still bounded (≤2 next steps).
  - Done when: convention + golden examples; live eval PASS.
  - Depends on: 6.1

- [ ] **B3.2 New skill `spaced-review` + retrieval stage** (M)
  - Goal: 13th skill — generates 2–3 warm-up retrieval items from interaction_log + rubric_score; becomes loop step 1.
  - Done when: daily loop = retrieval → criteria → I/we/you do → feedback; test covers stage order.
  - Depends on: B3.1 not required; 6.1

- [ ] **B3.3 Weekly timed mock mode** (M)
  - Goal: orchestrator weekly-mock mode (full QCAA conditions, summative A–E feedback); progress view distinguishes daily vs mock data points.
  - Done when: a mock session completes end-to-end and is visually distinct in the trend.
  - Depends on: 6.2

## Milestone B4 — Motivation layer (M)

- [ ] **B4.1 Streaks + weekly goal** (S)
  - Goal: streak counter + default 4 sessions/week goal; gentle, no punishment on break.
  - Done when: persisted + rendered; break produces a recovery prompt, not a penalty.
  - Depends on: 6.2

- [ ] **B4.2 Level-up celebration** (S)
  - Goal: criterion crossing a band (e.g. C→B) triggers specific praise naming the actual improvement.
  - Done when: event persisted + UI moment; message references the real criterion change.
  - Depends on: 6.2

- [ ] **B4.3 Coach persona tone** (S)
  - Goal: per-profile tone setting (warm / strict / humorous) injected into system prompt, never changing teaching contracts.
  - Done when: same input yields perceptibly different tone, identical output contract.
  - Depends on: 6.2

## Milestone B5 — Parent layer (M)

- [ ] **B5.1 Weekly parent report** (M)
  - Goal: in-app parent view + printable PDF: sessions, time, criterion trends, weekly highlight, next-week suggestion; NO full essay text (D3) — enforced in the API.
  - Done when: parent endpoints return no attempt full text (test asserts); PDF generates.
  - Depends on: 6.2, B3.3

- [ ] **B5.2 Shared goal setting** (S)
  - Goal: parent + student set the weekly goal together; referenced at loop start.
  - Done when: goal stored on profile and surfaced in the session opening.
  - Depends on: B5.1

## Milestone B6 — Beta ops (M)

- [ ] **B6.1 Per-stage model routing** (M)
  - Goal: adapter picks model by loop_stage (heavy stages → strong model; light stages → cheap tier); config-driven.
  - Done when: routing table in config; test asserts per-stage provider selection.
  - Depends on: —

- [ ] **B6.2 Privacy-safe telemetry + feedback package** (S)
  - Goal: local aggregated usage metrics (no content); one-click "feedback package" export for beta families.
  - Done when: a beta issue can be diagnosed from the package in <10 min.
  - Depends on: B1.2

- [ ] **B6.3 Beta handbook** (S)
  - Goal: install guide, parent one-pager, feedback channel, weekly check-in template.
  - Done when: a non-technical parent can install from the guide alone.
  - Depends on: B1.1

## Milestone 10 — Senior framework (P10, timed by beta family mix)

- [ ] **10.1 QCE instrument modelling** (M)
  - Goal: Units 1–4 / IA1 / IA2 / IA3 / EA modelled into `curriculum_outcome`; ISMG↔A–E mapping written as a research note.
  - Depends on: 6.1

- [ ] **10.2 Senior IA1 analytical pack** (M)
  - Goal: `references/analytical/year-11-12/` filled for IA1 only.
  - Done when: an IA1 task gets senior-standard feedback end-to-end.
  - Depends on: 10.1

---

## Progress

Phase 2 milestones done: **6.1** (reference packs). Next: 6.2 student profile + session context.
