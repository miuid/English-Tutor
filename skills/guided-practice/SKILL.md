# guided-practice

## Purpose

Work *with* the student (the "we do" of gradual release) on their own task, one step at a time, using prompts, questions and sentence stems — and withdraw the scaffolding as they succeed, so responsibility shifts to them.

## When to use

- After `model-response`, before `independent-task`.
- When a student can recognise a good move but can't yet do it unaided.
- When a student is stuck mid-task and needs a nudge, not the answer.

## Inputs

- `skill_focus` — the move being practised.
- `student_text` / `student_task` — the student's own work in progress.
- `year_level` — 8–12 (MVP default 8).
- `scaffold_level` — full / partial / minimal (starts where `model-response` left off; steps down as the student succeeds).

## Pedagogical basis

- **GRR "we do"**: joint construction with an *extended handover* — scaffolds reduced based on readiness. (Blueprint; reaserch.md)
- **AERO SWIF Stage 3**: co-construct using syntax prompts and sentence stems, then withdraw.
- **Scaffolding + fading**: sentence stems, graphic organisers, guiding questions removed as proficiency grows. (teacher-skills.md — explicit teaching & modelling)

## Method

1. Break `skill_focus` into the smallest next step for THIS student's task.
2. Prompt, don't tell: ask a guiding question first ("what technique is in that line? what does comparing X to Y suggest?"). Give the student a turn to answer.
3. Offer a scaffold sized to `scaffold_level`:
   - **full**: sentence stem + example word choices.
   - **partial**: sentence stem only, or a guiding question.
   - **minimal**: just a nudge ("you've got the quote — now the effect").
4. React to the student's attempt: affirm what worked, re-prompt only the part that didn't.
5. **Fade**: if the step succeeded, explicitly reduce the scaffold for the next step and say so ("you did that one with a stem — try the next without it").
6. Stop when the student can do the move; hand to `independent-task`.

## Output contract

Conversational, one step at a time:
```
Guiding question: <question about their text>
Scaffold (level: <full|partial|minimal>): <stem / hint, sized to level>
Your turn: <what to write/answer now>
```
After the student responds, next turn affirms + fades or re-prompts.

## Success criteria (drives eval)

- Works on the student's OWN text, one step at a time.
- Leads with a question/prompt before offering any scaffold.
- Scaffold matches `scaffold_level`.
- Explicitly fades support when the student succeeds.
- Never completes the step for the student.

## Guardrails

- Never write the student's sentence for them — the scaffold is a stem/hint, they fill it.
- Don't advance to the next step until the current one lands (or offer more scaffold, not the answer).
- One step per turn — don't dump the whole procedure.
- Don't stay on `full` scaffold once the student shows they don't need it.
