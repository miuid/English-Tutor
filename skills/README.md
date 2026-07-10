# Agent Skills — Authoring Convention

These are the teaching skills that make the tutor act like a top Year 8–12 English teacher. They are the product's core IP. Each skill is a **portable, model-agnostic Markdown package** — human-readable, version-controlled, and loaded by the backend at runtime. Teaching quality lives here, not in application code.

## Package layout

```
skills/
  <skill-name>/
    SKILL.md            # the skill itself (required)
    <reference>.md      # optional supporting reference (rubric, word tiers, etc.)
    examples/
      sample-NN.md      # a real-ish student input (eval fixture)
      expected-NN.md    # the behaviour a good response must exhibit
```

## SKILL.md required sections

| Section | Purpose |
|---|---|
| `# <skill-name>` | Kebab-case name matching the folder. |
| **Purpose** | One or two sentences: what this skill does for the student. |
| **When to use** | Trigger conditions the orchestrator/LLM keys on. |
| **Inputs** | What the skill expects (student text, year level, task type…). |
| **Pedagogical basis** | The evidence this is built on (APST / HITS / VTLM / GRR / AERO SWIF / QCAA). Keeps us honest and defensible. |
| **Method** | The actual instructions the LLM follows, step by step. This is the heart of the skill. |
| **Output contract** | The exact shape of what the skill returns. |
| **Success criteria** | Verifiable checks a good output must pass (drives eval fixtures). |
| **Guardrails** | What the skill must never do. |

## Non-negotiable guardrails (all skills)

1. **Coach, don't ghostwrite.** Never write the student's answer for them. Model on a *different* example, then hand the work back.
2. **Gradual release.** Respect "I do → we do → you do"; withdraw scaffolds as the student improves.
3. **Curriculum-anchored.** Every judgement traces to a QCAA outcome or standard descriptor, not vibes.
4. **Bounded feedback.** Never dump more than the student can act on — surface the 1–2 highest-leverage next steps.
5. **Age-appropriate + encouraging.** Year 8 voice; specific praise, never empty praise.
6. **Model-agnostic.** No provider-specific syntax. Plain instructions any capable LLM can follow.

## Design vs delivery scope

Skills are authored to generalise across Year 8–12 and all text types (imaginative / analytical / persuasive). The **MVP deliverable** fills in Year 8 · analytical/essay writing depth first.

## Skill index

All 8 v1 skills authored. Ordered by where they sit in a session loop.

| Skill | Status | Loop stage | Targets |
|---|---|---|---|
| `set-success-criteria` | v1 | start | Learning intention + "I can…" criteria |
| `model-response` | v1 | I do | Think-aloud worked example on a *different* text |
| `guided-practice` | v1 | we do | Scaffolded co-writing, fading support |
| `independent-task` | v1 | you do | Independent writing brief, QCAA conditions |
| `diagnose-errors` | v1 | triage | Classify error type + route to a specialist skill |
| `check-structure` | v1 | coach | Paragraph/essay structure (PEEL/TEEL) — weakness #2 |
| `elevate-vocabulary` | v1 | coach | Flat vocabulary → precise academic language — weakness #1 |
| `give-feedback` | v1 | end | QCAA A–E scoring + ≤2 next steps + self-check |

### How they compose (typical daily loop)

`set-success-criteria` → `model-response` (I do) → `guided-practice` (we do) → `independent-task` (you do) → student submits → `diagnose-errors` (triage) routes to `check-structure` / `elevate-vocabulary` for coaching → `give-feedback` closes with an A–E judgement + self-check.

`diagnose-errors` is the router: it never coaches itself, it decides which specialist skill acts.
