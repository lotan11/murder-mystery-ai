# Authoritative task backlog

Updated October 27, 2026. Lead/integrator owns this board. Status reflects committed milestones and current acceptance; no duplicate component implementations.

## Current delivery: M1 â€” reliable Blackthorn rehearsal

| ID | Priority | Stream / owner | Status | Deliverable / acceptance |
| --- | --- | --- | --- | --- |
| M1-01 | P0 | Lead | Done | Inspect main, branches, PR1 and failed CI; reuse reviewed recovery fixes |
| M1-02 | P0 | Story | Done; local tests pass | Blackthorn canon, fair clue timeline, targeted released-fact dialogue, hints and recap |
| M1-03 | P0 | Backend | Done; local tests pass | SQLite room recovery, durable identities/votes/progress, atomic write failure handling |
| M1-04 | P0 | Guest/host | Done; local tests pass | Host clue gates, act instructions, guest quick questions, lighter phone rendering |
| M1-05 | P0 | QA / lead | In progress | Full case, storage restart, WebGL failure, client validation, Windows launcher and green remote CI |
| M1-06 | P0 | Lead | Done | Specification, decisions, game design, backlog and progress report in repo |

## Next playable milestones

| ID | Priority | Milestone | Status | Acceptance / dependency |
| --- | --- | --- | --- | --- |
| M2-01 | P1 | Private characters | Ready after M1 | Assign character cards; public identity and private goals separated server-side |
| M2-02 | P1 | Private characters | Planned | Guest-only secret delivery and host roster; reconnect restores assignment without leaking secrets |
| M2-03 | P1 | Participation | Planned | Introductory round, accusation rationale and final reconstruction tied to motives |
| M2-04 | P1 | Rehearsal | Manual test pending | Four actual players, phones + TV, 20â€“30 minute rehearsal and feedback record |
| M3-01 | P1 | Optional AI | Planned | Provider decision, released-fact context, validated structured response and deterministic fallback |
| M3-02 | P1 | Optional AI | Planned | Spoiler/injection/timeout/cost tests before enabling model-backed dialogue |
| M4-01 | P2 | Speech | Planned | Consent, push-to-talk transcription, pause/mute/interruption and visible audio state |
| M4-02 | P2 | Character | Planned | Licensed rigged avatar, expressive gestures and readable captions |
| M4-03 | P2 | Speech/avatar | Planned | Custom voice and timestamped visemes; actual lip-sync validation |
| M5-01 | P2 | Hosted pilot | Planned | HTTPS, authentication, session expiry, rate limits, monitoring and backup/restore |
| M5-02 | P2 | Scaling | Planned | Shared room store/pub-sub before any multi-worker deployment |
| OPS-01 | P1 | Resilience | Backlog | Bound slow-client sends and implement room expiry/pruning |
| OPS-02 | P1 | Data lifecycle | Backlog | Versioned case migrations/export and user-visible room deletion |

## Routine decisions and user decisions

The lead resolves architecture and implementation choices within the accepted scope. External model/voice spend, avatar licensing or public hosting need a concrete proposed integration before user input. No paid provider, recording, purchased asset or public deployment is enabled in M1.

Planning context: earlier availability was three weeks part-time, roughly 10â€“12 hours/week. M1 creates a reliable short rehearsal; M2 is the next playable target. Production-quality voice, avatar and hosting are separate milestones, not an implied three-week promise.
