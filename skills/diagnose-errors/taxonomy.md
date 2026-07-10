# Error taxonomy + routing (Year 8 analytical)

Used by `diagnose-errors`. Categories are ordered by leverage — fix higher categories first.

| # | Category | What it looks like | Routes to |
|---|---|---|---|
| 1 | **Argument / point** | No clear claim; describes/retells instead of arguing; doesn't answer the question. | `check-structure` (Point) |
| 2 | **Analysis / evidence** | Quote-dumping; evidence not explained; asserts without proof; "shows" with no *how*. | `check-structure` (E1/E2) |
| 3 | **Structure / cohesion** | Elements out of order; no link; paragraphs without unity; no logical flow. | `check-structure` (L / essay-level) |
| 4 | **Language / vocabulary** | Flat/vague/repeated words; missing analytical metalanguage; wrong register. | `elevate-vocabulary` |
| 5 | **Mechanics** | Grammar, punctuation, spelling errors (only once higher levels are sound). | (future) `fix-mechanics` |

## Priority rule
Choose the primary issue as the **lowest-numbered category rated "major"**. Rationale: a strong vocabulary can't rescue a response with no argument, so fix the argument first. Mechanics is last — don't polish sentences that have no point.

## Strong-response case
If nothing is "major" and at most one thing is "minor", route to `give-feedback` with a *stretch* target (e.g. sharpen the thesis, deepen one analysis) rather than inventing a fault.
