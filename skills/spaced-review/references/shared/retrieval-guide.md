# Retrieval warm-up guide (shared)

Shared reference for `spaced-review`. Retrieval practice is text-type-agnostic, so this guide is shared across all `(text_type, year_band)` combos — the inputs (`text_type`, `year_level`, `review_history`) carry the combo-specific information.

## Why retrieval first

- HITS / VTLM lesson structure opens with **quick retrieval** to activate prior knowledge before new content: "quick retrieval / explicit explanation / guided practice / independent practice / brief review". (teacher-skills.md — Lesson planning & structuring)
- AERO's Writing Instruction Model builds automaticity through **spaced repetition** — skills are revisited across sessions, not massed into one. (teacher-skills.md — AERO SWIF)
- Cognitive load: working memory is the bottleneck. A warm-up longer than ~3 minutes or one that teaches new content steals capacity from the lesson that follows. (Queensland English Tutoring Blueprint — cognitive science)
- The daily loop promised in MVP-Plan §2 opens with 热身 retrieval — a quick review of last session's techniques and vocabulary.

## Reading the `review_history` digest

The digest is built from the student's `rubric_score` and `interaction_log` history:

```
Days since last session: <N | "first session">
Latest criterion levels (weakest first):
- <criterion name>: <A–E level>
- ...
Recently coached: <skill name> (<date>), <skill name> (<date>)
```

- **First session** — the digest reads `No prior sessions — this is the student's first daily loop.` Go to the cold-start menu below; do not reference any history.
- **Weakest-first criterion list** — the top 1–2 entries are your primary targets. A criterion sitting at D across recent sessions is a better warm-up target than one already at B.
- **Recently coached** — the skill(s) the student was coached on most recently (e.g. `check-structure`, `elevate-vocabulary`, `fix-mechanics`). If several days have passed since that coaching, retrieve it now — spacing is the mechanism.
- **Days since last session** — the bigger the gap, the more valuable the retrieval; keep the tone matter-of-fact either way.

## Item types

Use one item per target. Vary the type across the warm-up where possible.

1. **Recall** — name/define/list from memory.
   - "In one sentence: what does the 'E' (evidence) in a PEEL paragraph ask you to do?"
   - "Name two modal words that make a claim sound stronger."
2. **Spot** — find the target in a tiny *invented* snippet (never the student's own past text — you don't have it, and quoting grades back is shaming).
   - "Here is a flat sentence: 'The character was very scared.' What craft move would turn the telling into showing?"
   - "Which of these two sentences has a comma splice? A) … B) …"
3. **Apply-in-one-line** — use the skill once, in a single sentence.
   - "Write one sentence about any topic that shows an emotion without naming it."
   - "Turn this asserted reason into an elaborated one: 'Uniforms are unfair.'"

Items must be answerable in a sentence or two. No multi-sentence writing tasks — that is the independent task's job.

## Cold-start menu (no prior sessions)

Pick 2 items from the fundamentals for the session's `text_type`, leaning toward what `task_prompt` demands:

- **Analytical** — what a thesis statement does; naming a language technique (metaphor, simile, imagery) and its effect in one line; what "evidence" means in an analytical paragraph.
- **Persuasive** — the difference between a position and a reason; naming one rhetorical device (rhetorical question, rule of three, emotive language); what makes evidence *load-bearing* rather than decorative.
- **Imaginative** — the difference between showing and telling; what a complication does in a story; what "point of view" means.

Say plainly that it is their first session, so the warm-up starts with the building blocks — never pretend to remember history that does not exist.

## Band calibration

- **Year 8** — plain language, concrete metalanguage only (thesis, evidence, technique, showing/telling, contention). One-step items.
- **Year 9–10** — add the expected metalanguage (representation, reader positioning, modality, counterargument, motif, tonal control); items may combine recall + one-line application.
- **Year 11–12** — derived one band up (senior descriptors are derived, not verbatim — see Q-001): full critical metalanguage; apply-in-one-line items may ask for an evaluative judgement.

## Time and tone box

- 2–3 items, ~3 minutes total. This is a hard ceiling, not a target.
- Tone: warm, brisk, specific. Never recap grades ("last time you scored D") — the digest steers *what* you ask, never *how you make them feel*.
- Answers always included under `## Check yourself` so the student self-marks and moves straight on.
