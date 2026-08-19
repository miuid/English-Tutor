# English Tutor — PRD (MVP baseline + GA delta)

> Scoped to what `MEMORY.md` and `MVP-Plan.md` don't already cover: user stories, the daily-loop UX, the North Star metric, and non-functional requirements. Read those two first for vision/scope/architecture — this file does not repeat them.
>
> **Product boundary (2026-08-19):** V1 remains a **local MVP**. The GA direction is a **public paid product** for Australian secondary students. This file keeps the V1 delivery boundary explicit and records the GA delta so future planning does not mistake the local MVP for the final product scope.

Last updated: 2026-08-19

## 1. Users

- **Primary (V1 MVP):** one Year 8 student in Queensland working after school, largely self-directed.
- **Future/GA:** Year 8–12 students broadly; a parent/oversight role; paying families on a hosted public product (deferred to Beta/GA).

## 2. Problem & goal

The student's school teaches English; it does not give unlimited, immediate, individual feedback. This product provides a daily 15–20 minute coached writing practice that moves the student's QCAA analytical writing toward A+, focused first on their weaknesses: flat vocabulary and weak structure.

GA expands the same core promise from one local student to a public product for Australian secondary students: guided, conversational English tutoring with per-student progress and history.

## 3. User stories (V1 MVP)

- As a student, I want a short daily session with a clear goal so I know what I'm practising today.
- As a student, I want the tutor to show me how to do a move (worked example) before I try it, so I'm not stuck.
- As a student, I want to try it myself with hints that fade, so I actually learn it rather than copy.
- As a student, I want feedback that tells me the 1–2 most important things to fix and *why it raises my grade*, not a wall of red ink.
- As a student, I want to paste in my real school assignment and get help improving it (coaching, not a rewrite).
- As a student, I want to see my progress over time so I stay motivated.
- As a student, I want a weekly timed practice that feels like the real thing.

Explicitly **not** ghostwriting: the tutor never hands over a finished answer.

## 4. Daily-loop UX flow (V1 MVP)

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

## 6. Non-functional requirements (V1 MVP)

- **Privacy (minor's data):** the student's writing **may** be sent to a cloud LLM API to get high-quality feedback, but **all persisted V1 data stays local** (on the user's machine) and is **deletable at any time**. No third-party analytics on student content. This is a child's data — default to minimal retention and clear deletion.
- **Local-first V1:** runs on one machine via `docker compose up` (FastAPI + SQLite + React). No cloud account required to run V1.
- **Model-swappable:** LLM behind an adapter; switch provider (Kimi / Anthropic / OpenAI-compatible / local Ollama) by config without code changes.
- **Prod-ready seams:** multi-user schema, future auth, SQLite→Postgres by connection string, stateless backend.
- **Replayable:** each teaching interaction is logged as structured data so responses can be re-evaluated (eval harness / quality regression).
- **Latency:** a coaching turn should return promptly enough for a back-and-forth session (target a few seconds; depends on model choice).
- **GA trajectory:** the local MVP is not the final deployment target; GA must become a hosted public product with Google sign-in, paid subscriptions, and scaling headroom (see §9).

## 7. Out of scope (V1 MVP delivery)

For V1 only: motivation layer (streaks, persona), parent layer (reports, oversight), voice/oral practice, multi-tenant public deployment, real auth, payment/billing, and Years 9–12 / persuasive-imaginative *content depth* (the framework supports them; depth comes later). See `MEMORY.md` §4, §8.

These are **deferred**, not rejected as product scope. The GA direction in §9 explicitly pulls auth, billing, public deployment, broader subject coverage, and scaling back into the product roadmap.

## 8. Open questions

- ~~Which LLM for MVP~~ **Resolved 2026-07-10: single cloud Claude Sonnet 4.6, adapter-swappable.** Revised later: DeepSeek (2026-07-17), then Kimi K3 (2026-08-12).
- ~~Single-user MVP: skip login?~~ **Resolved 2026-08-19: V1 local MVP skips login; GA public product requires Google sign-in first.**
- GA billing provider and subscription taxonomy (Stripe vs Paddle; AUD 9.9/month baseline) — open, non-blocking for V1.
- GA subject coverage source of truth: which Australian English exam subjects/text types are modelled first beyond QCAA — open, blocking before public launch.

## 9. GA public paid product delta (directional requirements)

V1 stays local. GA must become a public paid product for Australian secondary students, without changing the teaching core: coach don't ghostwrite, gradual release, curriculum-anchored, bounded feedback.

### Functional requirements

- **FR-GA-001:** A student can sign in with Google and reach their own learning space.
- **FR-GA-002:** Each signed-in student has a profile containing year level, curriculum/state context, focus text types, and school feedback priorities.
- **FR-GA-003:** A student can choose the English exam subject/text type they are practising; coverage expands beyond the V1 Year 8 QCAA analytical depth toward the Australian secondary English exam set defined in the curriculum model.
- **FR-GA-004:** Each signed-in student has private progress and history: sessions, attempts, feedback, rubric scores, and interaction logs are isolated per student.
- **FR-GA-005:** A student or parent can start a paid subscription at the baseline price of **AUD 9.9/month**; access can be gated by subscription state without changing the teaching loop.
- **FR-GA-006:** A lesson keeps a fixed time budget and supports pause/resume across days, as proven in V1.
- **FR-GA-007:** A student can delete their hosted data; deletion cascades across profile, sessions, attempts, feedback, scores, logs, auth links, and billing references where law/provider constraints allow.

### Non-functional requirements

- **NFR-GA-001:** The hosted product must have a credible scaling path to **1,000 registered users** without redesigning the teaching core: stateless backend, Postgres, horizontal web/API scaling, and queue/isolation strategy for slow LLM calls.
- **NFR-GA-002:** Minor's data remains high-sensitivity: minimal retention, no third-party analytics on student content, clear deletion, and explicit cloud-LLM processing boundaries.
- **NFR-GA-003:** The LLM remains config-swappable; provider choice must not require business-logic changes.
- **NFR-GA-004:** The V1 local data model must migrate cleanly to hosted Postgres: UUID keys, portable column types, and per-student ownership preserved.

### GA acceptance boundary

GA is ready only when a new family can sign in with Google, create/select a student profile, choose a supported English exam subject/text type, complete a fixed-time guided session, pause and resume it, see per-criterion progress, manage an AUD 9.9/month subscription, and delete their data — with teaching quality still governed by the skill files and eval harness.
