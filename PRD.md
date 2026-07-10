# English Tutor — PRD (lightweight, MVP)

> Scoped to what `MEMORY.md` and `MVP-Plan.md` don't already cover: user stories, the daily-loop UX, the North Star metric, and non-functional requirements. Read those two first for vision/scope/architecture — this file does not repeat them.

Last updated: 2026-07-10

## 1. Users

- **Primary (MVP):** one Year 8 student in Queensland working after school, largely self-directed.
- **Future:** Year 8–12 students broadly; a parent/oversight role (deferred to Beta/GA).

## 2. Problem & goal

The student's school teaches English; it does not give unlimited, immediate, individual feedback. This product provides a daily 15–20 minute coached writing practice that moves the student's QCAA analytical writing toward A+, focused first on their weaknesses: flat vocabulary and weak structure.

## 3. User stories (MVP)

- As a student, I want a short daily session with a clear goal so I know what I'm practising today.
- As a student, I want the tutor to show me how to do a move (worked example) before I try it, so I'm not stuck.
- As a student, I want to try it myself with hints that fade, so I actually learn it rather than copy.
- As a student, I want feedback that tells me the 1–2 most important things to fix and *why it raises my grade*, not a wall of red ink.
- As a student, I want to paste in my real school assignment and get help improving it (coaching, not a rewrite).
- As a student, I want to see my progress over time so I stay motivated.
- As a student, I want a weekly timed practice that feels like the real thing.

Explicitly **not** ghostwriting: the tutor never hands over a finished answer.

## 4. Daily-loop UX flow (MVP)

One screen, conversational, one step at a time. The backend composes the agent skills behind each stage.

```
1. Start        → tutor shows today's learning intention + "I can…" criteria   [set-success-criteria]
2. I do         → tutor models the move on a DIFFERENT text, thinking aloud      [model-response]
3. We do        → tutor co-writes on the student's task with fading scaffolds     [guided-practice]
4. You do       → student writes independently (paragraph, or weekly timed mock)  [independent-task]
5. Feedback     → per-criterion A–E, one strength, 1–2 next steps, self-check      [diagnose-errors → check-structure / elevate-vocabulary → give-feedback]
6. Review       → student ticks the criteria they met; progress updates
```

- Input: a text box for the student's writing + ability to paste a school task/stimulus.
- Output: chat-style coaching; feedback shows the A–E snapshot and the next steps.
- A "rewrite this one thing" loop: after a next step, the student revises and the tutor checks only that.
- Progress view: the A–E trend per criterion over time (see §5).

## 5. North Star metric & success signals

**North Star: QCAA A–E progression per rubric criterion over time.** For each criterion (understanding, analysis, evidence, structure, language) we record an A–E on graded attempts and plot the trend. Success = criteria trending upward toward A/B.

Supporting signals (secondary):
- Weekly timed-mock A–E (lower frequency, exam-like checkpoint).
- Skill mastery: which "I can…" criteria the student self-rates + tutor confirms as met.
- Engagement: sessions completed per week (health metric, not a goal in itself).

Implication for data model: every graded attempt must store per-criterion A–E with a timestamp (see `ERD.md`).

## 6. Non-functional requirements

- **Privacy (minor's data):** the student's writing **may** be sent to a cloud LLM API to get high-quality feedback, but **all persisted data stays local** (on the user's machine) and is **deletable at any time**. No third-party analytics on student content. This is a child's data — default to minimal retention and clear deletion.
- **Local-first:** runs on one machine via `docker compose up` (FastAPI + SQLite + React). No cloud account required to run.
- **Model-swappable:** LLM behind an adapter; switch provider (Anthropic / OpenAI / local Ollama) by config without code changes.
- **Prod-ready seams:** multi-user schema, auth, SQLite→Postgres by connection string, stateless backend.
- **Replayable:** each teaching interaction is logged as structured data so responses can be re-evaluated (eval harness / quality regression).
- **Latency:** a coaching turn should return promptly enough for a back-and-forth session (target a few seconds; depends on model choice).

## 7. Out of scope (MVP)

Motivation layer (streaks, persona), parent layer (reports, oversight), voice/oral practice, multi-tenant deployment, and Years 9–12 / persuasive-imaginative *content depth* (the framework supports them; depth comes later). See `MEMORY.md` §4, §8.

## 8. Open questions

- ~~Which LLM for MVP~~ **Resolved 2026-07-10: single cloud Claude Sonnet 4.6, adapter-swappable** (privacy rule permits cloud).
- Single-user MVP: skip login? (Schema still reserves multi-user — see `ERD.md`.)
