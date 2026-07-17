# give-feedback

## Purpose

Give criterion-referenced feedback on a completed response: a QCAA-style A–E judgement per criterion, one genuine strength, and the 1–2 highest-leverage next steps — framed so the student improves, not just receives a grade.

## When to use

- After the student submits an independent/assessment response.
- At the end of a session, or for the weekly mock.
- After `diagnose-errors` when the response is broadly sound and needs a graded judgement + stretch.

## Inputs

- `student_text` — the completed response.
- `year_level` — 8–12 (MVP default 8).
- `text_type` — analytical (MVP).
- `task_prompt` / `success_criteria` — what it was meant to achieve.
- `mode` — formative (default) or summative (attach the A–E level explicitly).

## Pedagogical basis

- **APST Std 5**: assess, provide feedback, report. (teacher-skills.md)
- **HITS feedback**: specific, timely, linked to success criteria; advances learning *and* verifies teaching.
- **QCAA A–E standard elaborations**: A/B = purposeful, sophisticated, cohesive; C = sound; D/E = partial/fragmented. (reaserch.md — Evaluative Standards; see `rubric.md`)
- **AERO SWIF Stage 5**: honest, constructive feedback against transparent rubrics at the centre of the model.
- **Metacognition**: ask the student to self-rate against criteria before/with the feedback. (NSW metacognition report)

## Method

1. Score `student_text` against each criterion in `rubric.md` and assign an A–E per criterion, naming each criterion exactly as in `rubric.md` (and an overall level in `summative` mode).
2. Name **one specific strength** — a real move the student made, not empty praise.
3. Identify the **1–2 highest-leverage next steps** (never a long list). Prefer the step that would move the most criteria up a level.
4. For each next step, say *what* to do and *why it lifts the grade* — tie to the standard descriptor ("to reach a B here, explain the effect, don't just quote").
5. Offer a metacognitive prompt: ask the student to self-rate against the criteria and compare.
6. If a next step needs coaching, hand off (e.g. to `check-structure` / `elevate-vocabulary`).

## Output contract

```
## Per-criterion levels
- <criterion name from rubric.md, exactly>: **<A–E level>** — <short note>
- … (one line per rubric criterion; level is a single letter A–E, optionally + or -)
(Overall: **<A–E>**)        ← summative mode only
Strength: <one specific thing you did well>
Your 1–2 next steps to level up:
  1. <what> — <why it raises the grade, tied to the standard>
  2. <what> — <why>   (optional)
Self-check: how would you rate yourself against these criteria? Let's compare.
```

The `## Per-criterion levels` heading and the `- <name>: **<level>** — <note>` line shape are required exactly as shown — the backend parses them to record per-criterion progress over time.

## Success criteria (drives eval)

- Each criterion gets an A–E judgement tied to `rubric.md` descriptors.
- Exactly ONE strength, specific and real.
- No more than 2 next steps, each with a *why* linked to the standard.
- Includes a metacognitive self-rating prompt.
- Encouraging, Year 8 register; honest without being harsh.

## Guardrails

- Never give a bare number/grade with no path to improve.
- Never exceed 2 next steps (bounded feedback).
- Don't rewrite the student's work — describe the move, hand coaching to the specialist skill.
- Praise must be specific; no "great job!".
- In formative mode, lead with growth, not the letter grade.
