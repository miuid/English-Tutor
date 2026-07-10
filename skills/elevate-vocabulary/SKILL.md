# elevate-vocabulary

## Purpose

Find flat, vague, or repetitive words in a student's writing and coach them to replace those words with more precise academic and analytical language — teaching the *why* (shade of meaning, register) so the upgrade sticks, not just handing over a thesaurus swap. Targets the student's flat vocabulary.

## When to use

- The student's writing leans on weak all-purpose words: *good, bad, said, shows, big, thing, a lot, very, interesting, nice*.
- The same word repeats across a paragraph.
- Analytical writing lacks the metalanguage to name techniques and effects (*connotes, juxtaposes, evokes, positions, emphasises*).
- The student asks "how do I make this sound smarter / more sophisticated?"

Not for: structure (use `check-structure`) or grammar (use `diagnose-errors`).

## Inputs

- `student_text` — the writing to scan.
- `year_level` — 8–12 (sets the vocabulary tier ceiling; MVP default 8).
- `text_type` — analytical (MVP) → prioritises analytical metalanguage.
- `context` — optional; the text/topic being written about (so suggestions fit meaning).

## Pedagogical basis

- **AERO explicit vocabulary instruction**: teach Tier 2 (academic, cross-subject) and Tier 3 (subject-specific) words directly, including *shade of meaning* and morphology — not naturalistic acquisition. (Queensland English Tutoring Blueprint; AERO SWIF Stage 1)
- **Analytical metalanguage**: QCAA analytical writing requires students to name how language features shape meaning (*imagery, connotation, tone, positioning*). (reaserch.md)
- **GRR / coach don't ghostwrite**: offer choices and reasoning, student picks and rewrites. (VTLM; AERO SWIF Stage 3)
- **Bounded feedback**: a few high-value upgrades, not every word. (HITS)

## Method

Think through 1–3 silently; show what steps 4–5 produce.

1. **Scan** `student_text` for flat/vague/repeated words and for missing analytical metalanguage. Cross-check against `tiers.md`.
2. **Rank** candidates by payoff: a vague word doing important analytical work (e.g. "shows") beats a minor adjective. Pick the **top 2–3 only** (Year 8), max 4 for Years 11–12.
3. **For each, generate 2–3 stronger options** that fit the sentence's *actual meaning and register* (not just "fancier"). Pull from the right tier in `tiers.md`. Never suggest a word whose connotation changes the student's intended meaning.
4. **Teach the shade of meaning.** For each upgrade, give a one-line reason: what nuance/precision it adds, or what technique it lets the student name. This is the part that builds durable vocabulary.
5. **Hand it back.** Present as choices, and ask the student to reread the sentence and pick the word that best fits *their* meaning, then rewrite the sentence themselves. Do not rewrite it for them.

## Output contract

```
Words worth upgrading (top 2–3):

1. "<flat word>"  →  <option A> / <option B> / <option C>
   why: <shade of meaning / precision / technique it names>
2. ...

Your turn: reread each sentence, choose the option that fits YOUR meaning, and rewrite the sentence.
One to notice: <optional single pattern, e.g. "you used 'shows' 4 times — vary how you name what the text does">
```

## Success criteria (drives eval)

A good response MUST:
- Surface only the 2–3 (max 4) highest-value words, not every weak word.
- Offer options that preserve the student's intended meaning (no meaning drift).
- Give a genuine *reason* (shade of meaning / precision / metalanguage) for each, not just a synonym list.
- Include analytical metalanguage upgrades when `text_type` is analytical and the student used bare verbs like "shows/says".
- Return the rewrite to the student; never rewrite their sentence for them.
- Stay within the tier ceiling for the year level (no Year 12 words dropped on a Year 8 without explanation).

## Guardrails

- Never rewrite the student's sentence or paragraph wholesale.
- Never suggest a word the student is unlikely to understand without also explaining it.
- Don't inflate register for its own sake — precision over ostentation; flag if the student's original word was actually the best choice.
- Don't touch structure or grammar here.
