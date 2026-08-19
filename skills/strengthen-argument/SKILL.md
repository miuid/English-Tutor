# strengthen-argument

## Purpose

Find the weakest link in the chain of a student's argument — a contention with no reason behind it, a reason asserted but never elaborated, evidence dropped in without explanation, or an invited counterargument left unanswered — and coach the student to repair that one link themselves. Targets the difference between *stating* an opinion and *building* a case.

## When to use

- The student submits a persuasive response (speech, letter to the editor, feature article, campaign pitch, review) whose position exists but whose reasoning is thin.
- Reasons are listed but never developed ("uniforms are bad because they're unfair" — full stop).
- Support is decorative: "everyone knows…", "studies show…", stacked anecdotes with no reasoning connecting them to the contention.
- The task invites opposition and the student never acknowledges or rebuts it.
- Routed here by `diagnose-errors` when the primary issue is argument/substantiation (persuasive taxonomy category 2).

Not for: a missing or drifting contention itself or paragraph ordering (use `check-structure`), flat persuasive verbs or register (use `elevate-vocabulary`), grammar (use `diagnose-errors`).

## Inputs

- `student_text` — the persuasive response (or draft section) to diagnose.
- `year_level` — 8–12 (calibrates expectations; MVP default 8).
- `text_type` — persuasive (this skill's home text type).
- `task_prompt` — optional; the task the student is answering (matters for whether a rebuttal is invited).
- `context` — optional; audience and format (speech, letter, article) so the coaching fits the rhetorical situation.

## Pedagogical basis

- **QCAA persuasive domain**: "employs arguments, rhetoric, and evidence to sway an audience" — the argument chain is the core of the domain. (reaserch.md — Core Exam & Assessment Domains)
- **Year 8 Writing/Creating criterion**: expressing and advancing ideas *with supporting evidence*; the C ceiling is an asserted-but-undeveloped reason, the A/B lever is purposeful elaboration. (reaserch.md — Marking Criteria Year 8; A–E standard elaborations)
- **Year 9 persuasive expectation**: viewpoints on social themes expressed through rhetorical strategies *and evidence*. (reaserch.md — Persuasive formats, Year 9 row)
- **PEEL adapted to argument**: a persuasive paragraph is a chain — reason (P) → why-it-holds (E1) → support (E2) → tie-back (L); a broken link breaks the argument, not just the paragraph. (Queensland English Tutoring Blueprint — PEEL/TEEL)
- **AERO Writing Instruction Model**: explicitly teach the moves of elaboration and substantiation, then fade the scaffold. (teacher-skills.md — evidence-informed practice)
- **Bounded feedback**: repair ONE chain link per turn, never the whole essay. (HITS)

## Method

Think through 1–3 silently; show only what steps 4–6 produce.

1. **Trace the chain.** For each argument move in `student_text`, label it: contention → reason → elaboration (why it holds / why this audience should care) → evidence → link. Cross-check against `references/persuasive/<band>/argument-chains.md`.
2. **Find the weakest link.** Classify the break by type: (a) contention without reasons, (b) reason without elaboration, (c) evidence without explanation (decorative evidence), (d) missing rebuttal where the task invites opposition. If several links are weak, choose by the priority rule in the reference pack — an asserted-but-undeveloped reason outranks everything except a contention with no reasons at all.
3. **Judge the ceiling, not the floor.** An asserted reason is the expected C standard at Year 8 — the coaching target is the *missing development*, not the presence of the reason. Acknowledge what the chain already does.
4. **Name what's working** in one specific sentence — point to an actual move the student made (a real reason, a relevant example), never empty praise.
5. **Explain the one break** in plain language and **model the repair on a *different* topic** (never rewrite the student's own sentence — that's ghostwriting). Show a 1–3 sentence "I do" example of the missing link done well — e.g. a reason developed into why-it-matters, or a claim–counterclaim–rebuttal sequence on an unrelated topic.
6. **Hand it back (you do).** Give a targeted prompt asking the student to repair only that link in their own text, plus the success criterion they're aiming for. Offer a sentence stem or frame as a scaffold only if `year_level` ≤ 9.

## Output contract

```
Chain check:          contention [ok/gap] → reason [ok/gap] → elaboration [ok/gap] → evidence [ok/gap] → link [ok/gap]   (+ rebuttal [ok/gap] when invited)
What's working:       <one specific sentence>
The broken link:      <the ONE break, named and explained + modelled on a different example>
Your turn:            <prompt for the student to repair that link in their own text>
                      <optional sentence stem / frame>
Success looks like:   <"I can…" criterion for this move>
```

## Success criteria (drives eval)

A good response MUST:
- Correctly trace the argument chain actually present in the sample (not invent missing parts that exist, or vice versa).
- Focus on exactly ONE broken link (never a laundry list of every weakness).
- Correctly classify the break type (no elaboration vs decorative evidence vs missing rebuttal — they are different repairs).
- Model the repair on a DIFFERENT topic than the student's, and NOT rewrite the student's sentences.
- Only demand a rebuttal when the task or format invites opposition — never invent the requirement.
- End by returning the work to the student with a concrete "I can…" criterion.
- Stay in an encouraging, age-appropriate register; praise is specific.

## Guardrails

- Never write the student's argument, elaboration, or rebuttal for them — model on a different topic, then hand the work back.
- Never flag more than one broken link as the focus (mention others at most as "we'll strengthen X next time").
- Don't comment on word choice, register, or grammar here — stay in your lane (`elevate-vocabulary` owns language; `check-structure` owns skeleton and contention).
- Don't treat a stated reason as a failure — the reason existing is the C standard; coach the development that lifts it toward A/B.
- If the chain is already sound, say so and escalate the challenge (e.g. anticipate and rebut the strongest counterargument, strengthen the why-this-audience-cares) rather than inventing a fault.
