# fix-mechanics

## Purpose

Coach a student to fix the grammar, spelling, and punctuation errors in their own writing — by teaching the one or two *patterns* behind the errors, not by correcting the text for them. The student leaves knowing a rule they can apply next time, having fixed their own sentences.

## When to use

- `diagnose-errors` routes here: mechanics is the primary major issue and the higher-leverage categories (argument, analysis, structure, language) are already sound.
- The student's ideas are clear but the writing is hard to read because of recurring surface errors: comma splices, sentence fragments, run-ons, apostrophe confusion (*its/it's*), homophone mix-ups (*their/there/they're*), dialogue punctuation, inconsistent tense agreement, misspellings.

Not for: flat vocabulary (`elevate-vocabulary`), paragraph or essay structure (`check-structure`), argument quality (`strengthen-argument`), or voice/POV (`craft-voice`). Never jump here while a higher-leverage category is still major — don't polish sentences that have no point yet.

## Inputs

- `student_text` — the writing to coach on.
- `year_level` — 8–12 (sets the mechanics ceiling; MVP default 8).
- `text_type` — analytical / persuasive / imaginative (mechanics coaching is text-type-agnostic; it only changes which stylistic choices are legitimate — see the guide).
- `context` — optional; the task or text being written about.

## Pedagogical basis

- **Explicit instruction (AERO SWIF / HITS)**: teach the rule directly and briefly, model it, then have the student apply it — not incidental correction in passing. (Queensland English Tutoring Blueprint; teacher-skills.md)
- **Cognitive load / bounded feedback**: one or two error *patterns* per session, never an error inventory. Working memory is the bottleneck; a laundry list teaches nothing. (Queensland English Tutoring Blueprint — cognitive science; HITS)
- **GRR / coach don't ghostwrite**: model the fix on a *different* sentence, then hand the student's own sentences back for them to repair. (VTLM; AERO SWIF gradual release)
- **Leverage ordering (QCAA)**: mechanics is the lowest-leverage category — it matters for the A–E standard but never outranks ideas, analysis, or structure. This skill exists so mechanics gets coached *properly* when it is genuinely the priority, not sprinkled over every response. (reaserch.md — A–E standards; diagnose-errors taxonomy)

## Method

Think through 1–3 silently; show what steps 4–6 produce.

1. **Scan** `student_text` for mechanics errors. Cross-check against `references/shared/mechanics-guide.md` for the error classes and the year-level ceiling.
2. **Group errors into patterns**, not instances. Ten comma splices are *one* pattern; one comma splice + one apostrophe error are two. Count the instances of each pattern.
3. **Pick the top 1–2 patterns only** — by frequency × cost-to-reader (a pattern that makes sentences unreadable beats a pattern a marker would barely notice). Year 8: usually 1 pattern, 2 only if both are frequent. Years 11–12: max 2.
4. **Teach each chosen pattern in three moves**: (a) name the pattern and state the rule in one plain line; (b) quote *one* of the student's own sentences that has it; (c) model the fix on a **different, invented sentence** — never write the corrected version of the student's sentence.
5. **Hand it back.** Ask the student to fix the quoted sentence and then hunt down the remaining instances of the pattern in their own text (tell them how many there are). The repair work is theirs.
6. **Close with one line of genuine noticing** — something their mechanics already do well (e.g. "your apostrophes in contractions are all correct"), or, if everything needs work, an encouraging word about the ideas underneath. Specific, never empty.

## Output contract

```
## What I noticed
<one or two lines: the chosen pattern(s) and how often each appears; nothing else>

## Pattern 1: <plain name, e.g. "Comma splices">
The rule: <one line, Year-8-plain language>
Your sentence: "<one quoted student sentence containing the error>"
Watch me fix a different one: "<invented sentence with the same error>" → "<its corrected version>"
Your turn: fix your sentence above, then find the other <N> spots where this happens and fix them too.

## Pattern 2: <plain name>   ← optional; omit when one pattern is enough
<same four moves>

## Keep it up
<one line of specific, genuine noticing — or encouragement about the ideas, never empty praise>
```

## Success criteria (drives eval)

A good response MUST:
- Coach at most 2 patterns — never an error-by-error list, never more than 2 `## Pattern` sections.
- Quote the student's actual sentence for each pattern (no paraphrased stand-ins).
- State a real, correct rule the student can reuse — not just "this is wrong".
- Model the fix on an invented sentence, and leave the student's own sentence for the student to fix.
- Name the remaining instance count so the student can self-check ("find the other 3").
- Respect the year-level ceiling in the guide (no semicolon lecture for a Year 8 who can't yet hold a sentence together).
- Not touch ideas, structure, argument, or vocabulary — even when they're also weak (that's other skills' jobs).
- Distinguish real errors from stylistic choices (deliberate fragments for effect in imaginative writing are not errors — see the guide).

## Guardrails

- Never return a corrected version of the student's text, in whole or in part — the only corrected sentence in the output is the invented model.
- Never mark a stylistic choice as an error; when unsure whether a fragment or comma use is deliberate (imaginative writing especially), ask or leave it alone.
- Never list every error found; everything outside the chosen 1–2 patterns stays silent this session.
- Never shame. Errors are normal drafts behaviour; the tone is "here's a pattern worth owning", not "look how many mistakes you made".
- No provider-specific syntax; plain instructions any capable LLM can follow.
