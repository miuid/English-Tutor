# independent-task

## Purpose

Set a clear, curriculum-aligned writing task the student does on their own (the "you do" of gradual release), with the scaffolds removed, so they build automaticity and demonstrate the skill unaided.

## When to use

- After `guided-practice`, when the student can do the move with minimal help.
- For the weekly timed practice / mock assessment.
- When the student is ready to prove a success criterion independently.

## Inputs

- `skill_focus` / `outcome` — what the task must elicit.
- `year_level` — 8–12 (MVP default 8).
- `text_type` — imaginative / analytical (MVP) / persuasive.
- `mode` — practice (untimed) or assessment (timed, QCAA conditions).
- `stimulus` — optional text/topic; if absent, generate a copyright-safe one.

## Pedagogical basis

- **GRR "you do"**: independent practice with scaffolds removed; teacher monitors and feeds back. (Blueprint; reaserch.md)
- **AERO SWIF Stage 4**: dedicated time for extended independent writing, building automaticity via spaced practice.
- **QCAA assessment conditions** (Year 8): short response 50–200 words/item; extended analytical response 400–600 words; exam up to 70 min + 10 min planning. (reaserch.md — see `task-specs.md`)

## Method

1. Pick the task type from `task-specs.md` matching `text_type` + `mode`.
2. Write a clear task prompt tied to the `outcome`/`skill_focus`, with a copyright-safe stimulus if none given (public-domain or generated text — never reproduce copyrighted set texts).
3. State the conditions plainly: length, time (if assessment), and what will be assessed (restate the success criteria).
4. Remove scaffolds: no stems, no word banks — this is the independent attempt. A brief planning reminder is allowed, not a template.
5. Tell the student what happens next: submit → `give-feedback` (and/or self-check against criteria).

## Output contract

```
Your task: <prompt tied to outcome, with stimulus if needed>
Conditions: <length> · <time, if assessment> · <text type>
You'll be assessed on: <the success criteria, restated>
Plan first (2 min), then write. Submit when done and I'll give you feedback.
```

## Success criteria (drives eval)

- Task elicits the target `skill_focus`/`outcome`.
- Conditions match `task-specs.md` for the year level + mode.
- No scaffolds (stems/word banks) included — genuinely independent.
- Stimulus is copyright-safe.
- Success criteria are restated so the student knows the target.

## Guardrails

- Never reproduce copyrighted set texts as stimulus — generate or use public-domain material.
- Don't provide sentence stems or templates here (that's `guided-practice`).
- Don't set a task above the year-level conditions without flagging it as a stretch.
