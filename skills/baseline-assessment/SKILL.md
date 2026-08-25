# baseline-assessment

## Purpose

Turn a new student's first timed write into a calm, honest starting point: a criterion-referenced A–E baseline across the five feedback criteria for their text type, the 1–3 highest-leverage weaknesses ranked in the order we'll attack them, and a recommended starting focus loop — so day one already knows where it's going.

## When to use

- A brand-new student's first use, before any daily loop has run (the first-run "get your baseline" step).
- A returning student switches to a text type they have never been scored on, and we want a day-0 read for that type.
- A parent or student asks "where are we actually starting from?" and no rubric scores exist yet.

Not for: ongoing sessions (use the normal loop: `diagnose-errors` → specialist coach → `give-feedback`); re-assessment of a student with existing scores (the progress trend already answers this); grading a school assignment for marks (this is a coaching baseline, never a high-stakes exam).

## Inputs

- `student_text` — the timed write (roughly 15 minutes, one sitting, no help). Short and imperfect is fine — that's the point.
- `year_level` — 8–12 (calibrates the standard the baseline is read against).
- `text_type` — analytical | persuasive | imaginative (the type the student chose to be baselined on).
- `task_prompt` — optional; the baseline prompt given to the student.
- `context` — optional; anything the student/parent added (e.g. "hasn't written essays since primary school").

## Pedagogical basis

- **Criterion-referenced, never norm-referenced**: read the writing against the QCAA A–E standard descriptors, not against other students. (reaserch.md — Evaluative Standards & Marking Rubrics)
- **Diagnostic assessment before instruction**: a baseline exists to choose the starting point and the first lever, not to judge — the same evidence-first logic as the daily loop's `diagnose-errors` triage. (Queensland English Tutoring Blueprint — diagnostic-first competency mapping)
- **Gradual release**: the baseline sets where the "I do → we do → you do" loop starts and how much scaffold to offer first. (GRR; teacher-skills.md — VTLM/HITS)
- **Bounded feedback**: the student hears ONE strength and the top-ranked lever only; the full ranking is the plan, not a lecture. (HITS — feedback; PRD §3)
- **Low-stakes framing**: assessment for learning, not of learning — a timed first write read generously, at the ceiling of what it shows. (AERO SWIF, teacher-skills.md)

## Method

Think through 1–3 silently; show only what steps 4–7 produce.

1. **Confirm the read conditions.** Note `year_level` and `text_type`, and open `references/shared/baseline-guide.md`: use that text type's five criterion names **exactly as written there** (they match the loop's feedback rubric, so day-0 scores trend against later sessions) and its band calibration.
2. **Read generously at the ceiling.** For each of the five criteria, find the *highest* descriptor the writing genuinely evidences. A baseline taken from one short timed write is a floor estimate — when between two levels, pick the lower and say the evidence is thin, never inflate.
3. **Rank the levers.** Choose the 1–3 weaknesses with the highest leverage for this year level and text type, in attack order, using the guide's leverage ranking and skill map. Rank by what lifts the A–E standard fastest, not by what is easiest to notice.
4. **Report the baseline.** Produce the `## Per-criterion levels` section — exactly five bullet lines, one per criterion, in the contract format. These rows become the student's day-0 progress points.
5. **Name one specific strength.** Point to a real move in the writing (a genuine reason, a well-chosen quote, a moment of voice). Never empty praise, never more than one strength — the baseline is about direction.
6. **Recommend the focus loop.** State the ranked weaknesses (numbered, in attack order) and name the starting focus: the ONE specialist skill and text type the first daily loops should concentrate on, from the guide's map, plus a plain-language reason a Year 8 student or parent would understand.
7. **Close with the first step.** One encouraging sentence: what tomorrow's first session will do. No score talk with the student beyond "here's where we're starting" — the A–E letters are for the progress view, not a verdict.

## Output contract

```
  ## Per-criterion levels
  - <criterion name 1>: **<A–E level>** — <one short evidence note>
  - <criterion name 2>: **<A–E level>** — <one short evidence note>
  - <criterion name 3>: **<A–E level>** — <one short evidence note>
  - <criterion name 4>: **<A–E level>** — <one short evidence note>
  - <criterion name 5>: **<A–E level>** — <one short evidence note>

  Starting strength: <one specific sentence pointing at a real move>

  ## Ranked weaknesses
  1. <highest-leverage weakness — the lever we attack first>
  2. <second weakness>   (omit if only one matters)
  3. <third weakness>    (never more than three)

  ## Recommended focus loop
  Start with: <skill-name> on <text_type> writing — <one plain-language reason>
  First session: <one encouraging sentence about what happens next>
```

(The `## …` headings above are literal output headings the student-facing report must carry; the per-criterion lines are what becomes day-0 rubric scores.)

## Success criteria (drives eval)

A good response MUST:
- Emit exactly five per-criterion level lines using the text type's exact criterion names from the reference guide (analytical: Understanding of text / ideas · Analysis (how techniques create meaning) · Use of evidence · Structure & cohesion · Language & vocabulary), each with a valid A–E level and a short evidence note.
- Read generously but never inflate: levels match what the writing actually evidences; a thin, short baseline cannot score A/B without clear evidence.
- Rank 1–3 weaknesses in genuine leverage order (never a laundry list of everything wrong), consistent with the levels given.
- Recommend exactly ONE starting focus — a real specialist skill from the guide's map plus the text type — with a plain-language reason.
- Keep the student-facing tone warm and low-stakes: one specific strength, no mark talk, no comparing to other students.
- Stay model-agnostic and age-appropriate.

## Guardrails

- Never ghostwrite or "improve" any part of the student's text — the baseline only reads; coaching starts in the loop.
- Never present the baseline as a grade, prediction, or exam result — it is a starting point for teaching, explicitly revisable as real sessions accumulate.
- Never list more than 3 ranked weaknesses or more than 1 starting focus — bounded feedback applies here hardest, because this is the student's first impression.
- Never use criterion names other than the guide's five for the text type — day-0 rows must line up with the loop's rubric scores in the progress view.
- Never comment on handwriting, speed, spelling counts, or anything outside the five criteria; mechanics feed `diagnose-errors` in the loop, not the baseline verdict.
- If the submission is too short to evidence a criterion, score it E/D with "not enough evidence yet" as the note — do not refuse, and do not guess upward.
