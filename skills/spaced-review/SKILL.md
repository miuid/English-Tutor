# spaced-review

## Purpose

Open every daily loop with 2–3 short retrieval warm-up items drawn from the student's own learning history — the rubric criteria they scored lowest on and the patterns they were coached on most recently — so prior learning is reactivated before new work begins. This is a warm-up, not a lesson: three minutes, then hand over to today's goal.

## When to use

- First stage of every daily loop, before `set-success-criteria`.
- Always runs, including the student's very first session: when `review_history` reports no prior sessions, generate a generic warm-up from the task and year-level fundamentals instead (cold start).

Not for: teaching new content (that's `model-response` / `guided-practice`), diagnosing a fresh submission (`diagnose-errors`), or scoring work (`give-feedback`). Retrieval reactivates; it never introduces.

## Inputs

- `year_level` — 8–12 (sets item difficulty and metalanguage ceiling; MVP default 8).
- `text_type` — analytical / persuasive / imaginative (retrieval practice is text-type-agnostic; it only changes which fundamentals a cold-start warm-up targets).
- `task_prompt` — today's task, so items can lean toward what the student is about to need.
- `context` — optional; extra task context.
- `review_history` — a compact digest built from the student's `interaction_log` and `rubric_score` history: days since the last session, the latest level per rubric criterion (weakest first), and the most recently coached skills. Reads `No prior sessions` on first use.

## Pedagogical basis

- **Retrieval practice / lesson opening (HITS, VTLM)**: effective lessons open with quick retrieval that activates prior knowledge before new content — the structured sequence "quick retrieval / explicit explanation / guided practice / independent practice / brief review". This skill is the first step of that sequence. (teacher-skills.md — Lesson planning & structuring)
- **Spaced practice (AERO SWIF)**: revisiting learned skills across sessions builds automaticity; the warm-up deliberately reaches back to *earlier* sessions' coached patterns rather than re-drilling yesterday only. (teacher-skills.md — AERO Writing Instruction Model)
- **Cognitive load / bounded feedback**: 2–3 items, ~3 minutes. A warm-up that teaches new content or runs long steals working memory from the actual lesson. (Queensland English Tutoring Blueprint — cognitive science / GRR)
- **Curriculum-anchored**: item targets come from the student's QCAA rubric criterion history, not vibes — the weakest criterion and the most recently coached pattern are what get reactivated. (reaserch.md — A–E standards; ERD — rubric_score / interaction_log)
- **MVP-Plan §2 core loop**: the daily loop's promised first step — 热身 retrieval, a quick review of last session's techniques and vocabulary.

## Method

Think through 1–2 silently; show what steps 3–6 produce.

1. **Read `review_history`.** If it says there are no prior sessions, skip to step 4 (cold start). Otherwise note: how many days since the last session, the weakest 1–2 criteria (lowest latest levels), and the most recently coached skill(s).
2. **Pick 2–3 targets**, in this priority order: (a) the weakest criterion's underlying skill; (b) the most recently coached pattern — especially if several days have passed (spacing is the point); (c) a fundamental today's `task_prompt` is about to demand. Never more than 3.
3. **Write one short item per target.** Use the item types in `references/shared/retrieval-guide.md`: recall (name/define/list), spot (find the thing in a tiny invented snippet), or apply-in-one-line (one sentence using the skill). Mix recall with application where you can. Items must be answerable in a sentence or two — no paragraphs, no new teaching, no hints that give the answer away.
4. **Cold start (no history):** write 2 generic items from the year-level fundamentals for this `text_type` (see the guide's cold-start menu), leaning toward what `task_prompt` needs. Say plainly that this is their first session, so you're starting with the building blocks.
5. **Add the self-check answers** — one line per item, so the student marks themselves. Never make the student wait for you to confirm.
6. **Close with one onward line** that hands over to today's goal — warm, specific, never a recap of their grades.

## Output contract

```
## Warm-up
<one line: why these items today — e.g. "Two quick ones from last time before we start" — never a grade recap>

1. <item one — a question or tiny task>
2. <item two>
3. <item three — optional; omit when two is enough>

## Check yourself
1. <answer, one line>
2. <answer, one line>
3. <answer, one line — only if item 3 exists>

## Onward
<one line handing over to today's goal>
```

## Success criteria (drives eval)

A good response MUST:
- Contain 2–3 warm-up items and no more — never a second lesson, never a numbered list beyond the items and their answers.
- Make every item traceable: to the weakest criterion or recently coached pattern in `review_history`, or — on cold start — to the text-type fundamentals in the guide. Never invent history the digest does not contain.
- Keep every item answerable in a sentence or two (recall / spot / apply-in-one-line), completable in ~3 minutes total.
- Ask for recall or application, never re-teach: no explanations, rules, or worked examples inside the items.
- Include a one-line self-check answer per item.
- Match the year-level metalanguage ceiling in the guide.
- Stay warm and specific; never quote grades or levels back at the student as a scorecard.

## Guardrails

- Never exceed 3 items, and never turn the warm-up into teaching — no new content, no corrections, no mini-lessons.
- Never invent history: if `review_history` does not mention a criterion, pattern, or session, do not reference it. Cold start means cold start.
- Never shame or grade-recap ("last time you got a D") — the digest steers *what* you ask, never *how you make them feel*.
- Never answer the items inside the `## Warm-up` section — answers live only under `## Check yourself`.
- No provider-specific syntax; plain instructions any capable LLM can follow.
