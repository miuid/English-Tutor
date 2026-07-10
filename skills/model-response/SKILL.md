# model-response

## Purpose

Demonstrate a skill (the "I do" of gradual release) by producing a short worked example **with a think-aloud** — showing not just a good answer but the expert thinking behind it — on a text *different* from the student's own task, so nothing is done for them.

## When to use

- After success criteria are set, before the student attempts the skill.
- When a student says "I don't know how to start / what this looks like."
- When `check-structure` or another skill identifies a move the student hasn't seen done well.

## Inputs

- `skill_focus` — the move to model (e.g. explaining a technique's effect, embedding a quote, writing a topic sentence).
- `year_level` — 8–12 (MVP default 8).
- `student_task` — the student's actual task, used ONLY to pick a parallel-but-different example.

## Pedagogical basis

- **GRR "I do"**: teacher demonstrates explicitly, using think-alouds to model cognitive behaviour. (Blueprint; reaserch.md)
- **AERO SWIF Stage 3**: live modelling paired with metathinking / worked examples to manage cognitive load.
- **Worked-example effect** (cognitive load theory): novices learn more from studying a worked example than from unguided attempts. (Blueprint — Willingham/Sherrington)

## Method

1. Choose a **parallel example on a different topic/text** than `student_task` (same skill, new content) — so the student can't copy it into their own answer.
2. State what you're about to demonstrate (tie to the success criterion).
3. Produce the short example, interleaved with **think-aloud** in a distinct voice: verbalise the choices — "I'll start with my point so the reader knows my argument… now I need to explain *how*, not just quote…".
4. Keep it short: one paragraph or one move, not a whole essay.
5. End by **naming the transferable steps** the student should now try on their own text (bridge to `guided-practice` / `independent-task`).

## Output contract

```
Watch how I <skill_focus>. I'll think out loud so you can see my choices.

<worked example on a DIFFERENT text, with think-aloud interleaved, e.g.:>
  [example sentence]
  (why: <the reasoning>)
  ...

The steps I used — try these on your text:
  1. <step>  2. <step>  3. <step>
```

## Success criteria (drives eval)

- The example is on a DIFFERENT text/topic than the student's own task.
- Think-aloud is present and reveals reasoning, not just the answer.
- Scope is one move / one paragraph, not an essay.
- Ends with transferable steps naming what the student should do next.
- Matches `year_level` register.

## Guardrails

- Never model on the student's own task/text (that's ghostwriting by proxy).
- Don't skip the think-aloud — a bare good answer isn't modelling.
- Don't overload: one skill per model.
