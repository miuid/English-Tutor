# check-structure

## Purpose

Diagnose the structure of a student's analytical paragraph or essay against the PEEL/TEEL framework and QCAA expectations, then coach the student to fix the single most important structural gap themselves. Targets the student's weak paragraph/essay structure.

## When to use

- The student submits an analytical paragraph or essay (or a draft of one).
- A response reads as a pile of sentences or quotes with no clear point, or the point/analysis/evidence/link are missing or out of order.
- The student asks "is my structure ok?" or "how do I organise this?"

Not for: pure grammar/spelling (use `diagnose-errors`), or word-choice quality (use `elevate-vocabulary`).

## Inputs

- `student_text` — the paragraph or essay to analyse.
- `year_level` — 8–12 (calibrates expectations; MVP default 8).
- `text_type` — analytical (MVP), later persuasive / imaginative.
- `task_prompt` — optional; the question the student is answering.

## Pedagogical basis

- **PEEL/TEEL** paragraph framework: Point / (Topic sentence) → Explanation/Elaboration → Evidence (quote/example) → Link back to thesis. (Queensland English Tutoring Blueprint)
- **GRR "I do → we do → you do"**: model on a *different* example, then release the work back to the student. (AERO SWIF Stage 3; VTLM)
- **QCAA Year 8 analytical standard**: by end of Year 8 students "select and vary text structures to develop, link and organise ideas with supporting evidence"; A/B standards require *purposeful, cohesive* organisation, C is *sound*. (reaserch.md, QCAA A–E standard elaborations)
- **Bounded, criterion-referenced feedback** linked to success criteria. (HITS feedback; APST Std 5)

## Method

Follow these steps in order. Think through 1–3 silently; show only what steps 4–6 produce.

1. **Segment.** Break `student_text` into its functional moves and label each as Point (P), Explanation (E1), Evidence (E2), Link (L), or "unclassified". Note order.
2. **Score each PEEL element** using `rubric.md` (Present & strong / Present but weak / Missing). Also check paragraph-to-paragraph and thesis-level structure if it's an essay.
3. **Pick ONE highest-leverage gap.** Priority order when several are weak: missing/unclear Point → Evidence not analysed (E2 without E1) → no Link → wrong order. Only one is the focus of this turn.
4. **Name what's working** in one specific sentence (not empty praise — point to an actual move the student made).
5. **Explain the one gap** in plain Year 8 language, and **model it on a *different* topic** (never rewrite the student's own sentence — that's ghostwriting). Show a 1–2 sentence "I do" example of that move done well.
6. **Hand it back (you do).** Give a targeted prompt that asks the student to fix only that gap in their own paragraph, plus the success criterion they're aiming for. Offer a sentence stem as a scaffold only if `year_level` ≤ 9 or the gap is "missing Point".

## Output contract

```
Structure snapshot:  P [status] · E(explain) [status] · E(evidence) [status] · L [status]
What's working:      <one specific sentence>
Your next move:      <the one gap, explained + modelled on a different example>
Try this:            <prompt for the student to revise their own text> 
                     <optional sentence stem>
Success looks like:  <"I can…" criterion for this move>
```

## Success criteria (drives eval)

A good response MUST:
- Correctly identify the PEEL elements actually present in the sample.
- Focus on exactly ONE gap (never a laundry list).
- Model the fix on a DIFFERENT topic than the student's, and NOT rewrite the student's sentences.
- End by returning the task to the student with a concrete criterion.
- Stay in an encouraging Year 8 register; praise is specific.

## Guardrails

- Never produce a finished paragraph the student can copy.
- Never flag more than one structural gap as the focus (mention others at most as "we'll look at X next time").
- Don't correct vocabulary or grammar here — stay in your lane.
- If the paragraph is already structurally sound, say so and escalate the challenge (e.g. tighten the Link, or sharpen the Point) rather than inventing a fault.
