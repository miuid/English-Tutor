# diagnose-errors

## Purpose

Read a student's response and classify what's holding it back by *error type* — not just mark it wrong — then route to the right specialist skill. This is the triage layer that decides which of the other skills should act.

## When to use

- On any submitted response, before deciding what feedback/coaching to give.
- When multiple things are weak and the tutor must choose where to start.
- As the router that dispatches to `check-structure`, `elevate-vocabulary`, or `give-feedback`.

## Inputs

- `student_text` — the response to diagnose.
- `year_level` — 8–12 (MVP default 8).
- `text_type` — analytical (MVP).
- `task_prompt` — optional.

## Pedagogical basis

- **APST Std 5 / diagnostic assessment**: identify what a student can do and what they need next, by category. (teacher-skills.md)
- **Responsive teaching (VTLM "monitor progress")**: use error patterns to select the next move. (teacher-skills.md — evidence-informed practice)
- **Bounded feedback / cognitive load**: name the categories, then act on the single highest-leverage one. (HITS)

## Method

1. Read `student_text` against the taxonomy in `taxonomy.md`.
2. Tag each category present as: not an issue / minor / major.
3. Choose the **primary** issue by leverage (see taxonomy priority): argument/point > analysis/evidence > structure/cohesion > language/vocabulary > mechanics.
4. Output the diagnosis + the recommended route (which skill should act next).
5. Do NOT coach or rewrite here — diagnosis only. Hand off.

## Output contract

```
Diagnosis:
  Argument/point:      <ok | minor | major>
  Analysis/evidence:   <ok | minor | major>
  Structure/cohesion:  <ok | minor | major>
  Language/vocabulary: <ok | minor | major>
  Mechanics:           <ok | minor | major>
Primary issue: <one category> — <one-line why>
Route to: <check-structure | elevate-vocabulary | give-feedback | guided-practice>
```

## Success criteria (drives eval)

- Every taxonomy category is rated.
- Exactly one primary issue chosen, by the leverage priority.
- A concrete route to the correct downstream skill.
- No coaching, rewriting, or scoring (that's other skills' jobs).

## Guardrails

- Diagnosis only — never fix, coach, or rewrite here.
- Pick ONE primary issue; don't route to five skills at once.
- If the response is strong across the board, say so and route to `give-feedback` for a stretch target.
