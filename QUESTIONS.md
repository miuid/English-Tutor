# Delivery Questions

This document is the canonical record of unresolved and resolved delivery decisions. Do not remove answered questions; preserve the decision history.

## Rules
- An `OPEN` question with `Severity: BLOCKING` forces `ISSUES.md` Delivery Gate to `BLOCKED`.
- Every blocking question must be listed in `ISSUES.md` under `Blocking questions`.
- Resolving a question requires updating its linked issues and re-evaluating the delivery gate.
- Do not record credentials, tokens, private keys, or personal data here.

## Question Index
| ID | Decision | Status | Severity | Related issue |
|---|---|---|---|---|
| Q-001 | Source for Year 9-12 QCAA standard descriptors | `OPEN` | `NON_BLOCKING` | `ISS-002, ISS-024` |
| Q-002 | Beta recruitment channel | `OPEN` | `NON_BLOCKING` | `ISS-023` |
| Q-003 | GA billing provider and tax posture | `OPEN` | `NON_BLOCKING` | `None` |
| Q-004 | GA public deployment and data residency posture | `OPEN` | `NON_BLOCKING` | `None` |

## Questions

## Q-001 - Source for Year 9-12 QCAA standard descriptors
- Status: `OPEN`
- Severity: `NON_BLOCKING`
- Raised by: `plan`
- Related issue: `ISS-002, ISS-024`
- Related requirements: `PRD: §9 FR-GA-003; ERD: curriculum_outcome`
- Raised: `2026-08-19T13:44:45+10:00`
- Answered: `None`

### Decision needed
Decide whether the existing research files are sufficient for Year 9-12 QCAA standard descriptors, or whether official syllabus PDFs must be imported before content depth is claimed.

### Why it matters
The answer affects how much evidence ISS-002 and ISS-024 must cite before marking content packs complete.

### Options and recommendation
1. Use existing research files and mark any uncertain descriptor as derived, not verbatim.
2. Import official QCAA syllabus/source PDFs first and cite them directly.

Recommendation: Start with existing research files for Year 9-10; require official sources before public launch claims or senior IA1 depth.

### Answer and resolution
- Answer: Pending
- Resolution: Pending

## Q-002 - Beta recruitment channel
- Status: `OPEN`
- Severity: `NON_BLOCKING`
- Raised by: `plan`
- Related issue: `ISS-023`
- Related requirements: `PRD: §7 deferred Beta scope; ERD: Deployment/migration`
- Raised: `2026-08-19T13:44:45+10:00`
- Answered: `None`

### Decision needed
Choose the first beta recruitment channel: friend families, school parent group, or another local Queensland network.

### Why it matters
The channel changes the tone and onboarding detail required in the beta handbook.

### Options and recommendation
1. Friend families first: fastest feedback, lower onboarding polish required.
2. School parent group: better reach, needs clearer privacy and install documentation.

Recommendation: Friend families first, then school parent group after B1-B3 are stable.

### Answer and resolution
- Answer: Pending
- Resolution: Pending

## Q-003 - GA billing provider and tax posture
- Status: `OPEN`
- Severity: `NON_BLOCKING`
- Raised by: `plan`
- Related issue: `None`
- Related requirements: `PRD: §9 FR-GA-005; ERD: GA planned entities/TD-GA-001`
- Raised: `2026-08-19T13:44:45+10:00`
- Answered: `None`

### Decision needed
Choose the GA billing provider for AUD subscriptions and confirm tax/invoicing obligations.

### Why it matters
This matters before any public paid launch, but it does not change the current local Phase 2 teaching backlog.

### Options and recommendation
1. Stripe: flexible, common, more integration ownership.
2. Paddle/merchant-of-record style: less tax surface, different constraints.

Recommendation: Defer until GA planning; spike Stripe first unless tax obligations force a merchant-of-record decision.

### Answer and resolution
- Answer: Pending
- Resolution: Pending

## Q-004 - GA public deployment and data residency posture
- Status: `OPEN`
- Severity: `NON_BLOCKING`
- Raised by: `plan`
- Related issue: `None`
- Related requirements: `PRD: §9 NFR-GA-001/NFR-GA-002; ERD: TD-GA-003`
- Raised: `2026-08-19T13:44:45+10:00`
- Answered: `None`

### Decision needed
Choose the public deployment target and data-residency posture for Australian families.

### Why it matters
This affects hosted privacy, latency, backups, and operational cost before GA, but not the current local Beta path.

### Options and recommendation
1. Australia-region managed Postgres + containers.
2. Single VPS first with documented backup/restore, then managed services.

Recommendation: Defer until GA planning; prefer Australia-region managed Postgres for public launch if budget allows.

### Answer and resolution
- Answer: Pending
- Resolution: Pending

## Change Log
- `2026-08-19T13:44:45+10:00` - Initialized by `/plan`; no `BLOCKING` questions are open, so `ISSUES.md` Delivery Gate is `OPEN`.
