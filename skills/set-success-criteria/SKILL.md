# set-success-criteria

## Purpose

Turn a curriculum outcome (or the day's task) into a single clear learning intention plus 2–4 student-friendly "I can…" success criteria, so the student knows what they're aiming for and can self-check at the end. Opens most sessions.

## When to use

- At the start of a session or a new task.
- When a student says "I don't know what I'm supposed to be doing / what a good answer looks like."
- Before `model-response`, so the modelling has an explicit target.

## Inputs

- `outcome` — a QCAA outcome/standard descriptor, or a task the student is doing.
- `year_level` — 8–12 (MVP default 8).
- `text_type` — analytical (MVP).
- `focus_skill` — optional; e.g. structure or vocabulary, to sharpen the criteria.

## Pedagogical basis

- **HITS "Setting goals"**: communicate clear lesson goals + success criteria so students commit and know what success looks like.
- **VTLM explicit teaching**: state objectives in student-friendly language, break into "I can…" criteria linked to curriculum descriptors.
- **Metacognition**: criteria double as a self-assessment checklist at session end. (NSW metacognition report)

## Method

1. Read the `outcome`/task. Identify the ONE core capability it targets.
2. Write a **learning intention** in plain language: "We are learning to …".
3. Derive **2–4 success criteria** as "I can…" statements — concrete, observable, checkable by the student. Pull phrasing patterns from `criteria-bank.md`; adapt to the specific text/topic.
4. If `focus_skill` is set, make one criterion explicitly about it.
5. Keep the count small (Year 8: 2–3). More criteria = less focus.
6. Present the intention + criteria, and tell the student they'll rate themselves against these at the end.

## Output contract

```
Today we are learning to: <learning intention>
You'll know you've got it when:
  □ I can <criterion 1>
  □ I can <criterion 2>
  □ I can <criterion 3>   (optional)
(At the end, you'll tick the ones you nailed.)
```

## Success criteria (drives eval)

- Exactly one learning intention, in student-friendly language.
- 2–4 criteria (2–3 for Year 8), each observable and self-checkable.
- Criteria trace to the given outcome, not generic.
- If `focus_skill` given, one criterion addresses it.

## Guardrails

- Don't write vague criteria ("I can write well").
- Don't exceed 4 criteria.
- Don't restate the outcome verbatim in curriculum jargon — translate it for a 13-year-old.
