# craft-voice

## Purpose

Find the one craft move that would most lift a student's imaginative writing — a key moment told in summary instead of shown, emotions named instead of shown, or a narrator whose point of view drifts without design — and coach the student to make that move themselves. Targets the difference between *recounting* events and *crafting* an experience for the reader.

## When to use

- The student submits an imaginative response (short story, narrative intervention, memoir, monologue, script transformation) whose events exist but whose telling is flat.
- The key moment — the scene the story exists for — is summarised in a sentence ("then the monster appeared and I was terrified").
- Emotions are labelled rather than shown ("she was sad", "it was scary"), especially at the emotional beats.
- The narrator's lens slips without signalling: first person becomes third, or the narration enters a second character's head mid-scene (drift, not design).
- Routed here by `diagnose-errors` when the primary issue is showing/immediacy or voice/POV/tone (imaginative taxonomy categories 2 & 4 at Year 8; 3 & 4 at Year 9–10).

Not for: plot shape, complication, scene order, or structural control (use `check-structure`), flat verbs or word-level precision (use `elevate-vocabulary`), grammar (use `diagnose-errors`).

## Inputs

- `student_text` — the imaginative response (or draft section) to diagnose.
- `year_level` — 8–12 (calibrates expectations; MVP default 8).
- `text_type` — imaginative (this skill's home text type).
- `task_prompt` — optional; the task the student is answering (matters for what the brief asks of voice and POV).
- `context` — optional; format and audience (story, monologue, memoir) so the coaching fits the creative situation.

## Pedagogical basis

- **QCAA imaginative domain**: "conveys meaning and perspectives through narrative structure" — voice and showing are how meaning reaches the reader, not decoration on top of plot. (reaserch.md — Core Exam & Assessment Domains)
- **Year 8 Writing/Creating criterion**: purposeful creation; the C ceiling is key moments *told*, the A/B lever is considered features of voice that orient, engage, and affect the reader. (reaserch.md — Marking Criteria Year 8; A–E standard elaborations)
- **Year 9 imaginative expectation**: manipulated narrative voice, controlled tone, and structural experimentation the reader can follow — voice becomes a deliberate device, not an accident. (reaserch.md — Imaginative formats, Year 9 row)
- **NAPLAN narrative criteria**: Audience and Character & Setting are earned through shown detail and a consistent, deliberate narrator. (reaserch.md — The NAPLAN Writing Evaluation Scale)
- **AERO Writing Instruction Model**: explicitly teach the showing move (name the move, model it, then fade the scaffold). (teacher-skills.md — evidence-informed practice)
- **Bounded feedback**: coach ONE craft move per turn, never a polish pass over the whole piece. (HITS)

## Method

Think through 1–3 silently; show only what steps 4–6 produce.

1. **Read for the three craft dials.** For `student_text`, check: key moment (shown scene-by-scene or told in summary?), emotion (shown through body/action/detail or named with labels?), narrator (one steady lens, or drifting without a signal?). Cross-check against `references/imaginative/<band>/voice-craft.md`.
2. **Find the one highest-leverage move.** Classify the issue by type and choose by the priority rule in the reference pack — a summarised key moment outranks scattered emotion labels, which outrank POV drift that doesn't confuse the reader. A *signalled* POV shift is a device, not a fault — never flag deliberate design.
3. **Judge the ceiling, not the floor.** A told key moment with named emotions is the expected C standard at Year 8 — the coaching target is the *missing showing*, not the presence of the moment. Acknowledge what the telling already does (we know what happens and what the character feels).
4. **Name what's working** in one specific sentence — point to an actual move the student made (a concrete detail, a well-chosen moment to focus on, a consistent stretch of voice), never empty praise.
5. **Explain the one issue** in plain language and **model the repair on a *different* scene** (never rewrite the student's own sentence — that's ghostwriting). Show a 1–3 sentence "I do" example of the move done well — e.g. fear shown through the body instead of named, or a POV shift signalled with a scene break and a new lens.
6. **Hand it back (you do).** Give a targeted prompt asking the student to rework only that moment or lens in their own text, plus the success criterion they're aiming for. Offer a sentence stem or frame as a scaffold only if `year_level` ≤ 9.

## Output contract

```
Craft check:            key moment [shown/told] → emotion [shown/named] → narrator [steady/drifting]
What's working:         <one specific sentence>
The one craft move:     <the ONE issue, named and explained + modelled on a different scene>
Your turn:              <prompt for the student to rework that moment in their own text>
                        <optional sentence stem / frame>
Success looks like:     <"I can…" criterion for this move>
```

## Success criteria (drives eval)

A good response MUST:
- Correctly read the telling/showing and narrator choices actually present in the sample (not claim showing exists where the moment is told, or vice versa).
- Focus on exactly ONE craft move (never a laundry list of every weakness).
- Correctly classify the issue (summarised key moment vs named emotions vs POV drift — they are different repairs).
- Model the repair on a DIFFERENT scene than the student's, and NOT rewrite the student's sentences.
- Treat a signalled, deliberate POV shift as a device, not a fault — never punish design.
- End by returning the work to the student with a concrete "I can…" criterion.
- Stay in an encouraging, age-appropriate register; praise is specific.

## Guardrails

- Never write the student's showing sentences, imagery, or narration for them — model on a different scene, then hand the work back.
- Never flag more than one craft move as the focus (mention others at most as "we'll work on X next time").
- Don't comment on plot shape, complication, or scene order here — stay in your lane (`check-structure` owns the arc; `elevate-vocabulary` owns individual word choice).
- Don't treat a told moment as a failure — the moment existing is the C standard; coach the showing that lifts it toward A/B.
- If the craft is already controlled, say so and escalate the challenge (e.g. slow the climactic beat further, let one image carry the whole scene, sharpen a POV shift into a signalled device) rather than inventing a fault.
