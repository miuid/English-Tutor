# English Tutor — ERD (simple, MVP)

> Data model for the MVP, kept deliberately small. Designed so the North Star metric (per-criterion A–E progression, `PRD.md` §5) is a direct query, teaching interactions are replayable, and a minor's data is local and deletable. Multi-user is reserved but not exercised in the single-user MVP.

Last updated: 2026-07-10

## Diagram

```mermaid
erDiagram
    STUDENT ||--o{ SESSION : has
    STUDENT ||--o{ ATTEMPT : writes
    SESSION ||--o{ SUCCESS_CRITERION : sets
    SESSION ||--o{ ATTEMPT : contains
    SESSION ||--o{ INTERACTION_LOG : records
    ATTEMPT ||--o| FEEDBACK : receives
    FEEDBACK ||--o{ RUBRIC_SCORE : contains
    CURRICULUM_OUTCOME ||--o{ SUCCESS_CRITERION : anchors
    CURRICULUM_OUTCOME ||--o{ RUBRIC_SCORE : graded_against
    SKILL ||--o{ ATTEMPT : practised_in
    SKILL ||--o{ INTERACTION_LOG : produced_by

    STUDENT {
        uuid id PK
        string name
        int year_level
        string curriculum
        datetime created_at
    }
    CURRICULUM_OUTCOME {
        uuid id PK
        string code
        string strand
        int year_level
        string text_type
        text descriptor
    }
    SKILL {
        uuid id PK
        string name
        string version
        string loop_stage
    }
    SESSION {
        uuid id PK
        uuid student_id FK
        datetime started_at
        datetime ended_at
        text learning_intention
    }
    SUCCESS_CRITERION {
        uuid id PK
        uuid session_id FK
        uuid outcome_id FK
        text text
        string self_rating
        bool met
    }
    ATTEMPT {
        uuid id PK
        uuid session_id FK
        uuid student_id FK
        uuid skill_id FK
        string task_type
        string mode
        text task_prompt
        text student_text
        datetime created_at
    }
    FEEDBACK {
        uuid id PK
        uuid attempt_id FK
        text strength
        text next_steps
        datetime created_at
    }
    RUBRIC_SCORE {
        uuid id PK
        uuid feedback_id FK
        uuid outcome_id FK
        string criterion_name
        string level
        text note
        datetime scored_at
    }
    INTERACTION_LOG {
        uuid id PK
        uuid session_id FK
        uuid skill_id FK
        string model
        text input
        text output
        datetime created_at
    }
```

## Entities

- **student** — the learner. Multi-user ready; MVP has one row.
- **curriculum_outcome** — a QCAA outcome/descriptor (strand, year, text type). Year 8 analytical filled first; 9–12 rows added later.
- **skill** — registry entry for each agent skill (name, version, loop stage). The behaviour lives in the `skills/` files; this table lets attempts/logs reference which skill + version ran.
- **session** — one practice session; holds the learning intention.
- **success_criterion** — the "I can…" criteria for a session, anchored to an outcome, with the student's self-rating.
- **attempt** — a piece of student writing (paragraph or timed mock), tied to the skill practised.
- **feedback** — the coaching response for an attempt: one strength + the 1–2 next steps.
- **rubric_score** — **the North Star table.** One row per criterion per graded attempt: `criterion_name` + `level` (A–E) + timestamp. Progress = these rows over time.
- **interaction_log** — every LLM turn (input, output, model), for replay and the eval harness.

## Key queries this supports

- **North Star:** `rubric_score` filtered by `student` + `criterion_name`, ordered by `scored_at` → the A–E progression curve per criterion.
- **Weekly mock trend:** `attempt.mode = 'assessment'` joined to its `rubric_score`s.
- **Replay/eval:** `interaction_log` by `skill_id` + `model` → re-score against golden expectations.

## Privacy & retention (minor's data)

- All tables live in the local database (SQLite MVP). Nothing persisted off-machine.
- `student_text`, `feedback`, and `interaction_log` hold the child's writing — treat as sensitive.
- **Deletion:** deleting a `student` cascades to sessions, attempts, feedback, scores, and logs. Provide a "delete my data" path from day one.
- Cloud LLM may *process* `student_text` in transit (per `PRD.md` §6) but must not be used to persist or train on it.

## Prod-readiness notes

- UUID PKs and a `student_id` on session/attempt make multi-tenant migration clean.
- SQLite → Postgres: types chosen to port directly (uuid, datetime, text).
- `skill.version` lets us correlate quality changes with skill edits.
