# Authoritative task backlog

Updated October 27, 2026. Lead/integrator owns this board. Status reflects committed milestones and current acceptance; no duplicate component implementations.

## Accepted foundation: M1 — reliable Blackthorn rehearsal

| ID | Priority | Stream / owner | Status | Deliverable / acceptance |
| --- | --- | --- | --- | --- |
| M1-01 | P0 | Lead | Done | Inspect main, branches, PR1 and failed CI; reuse reviewed recovery fixes |
| M1-02 | P0 | Story | Done; local + CI pass | Blackthorn canon, fair clue timeline, targeted released-fact dialogue, hints and recap |
| M1-03 | P0 | Backend | Done; local + CI pass | SQLite room recovery, durable identities/votes/progress, atomic write failure handling |
| M1-04 | P0 | Guest/host | Done; local + CI pass | Host clue gates, act instructions, guest quick questions, lighter phone rendering |
| M1-05 | P0 | QA / lead | Done; local + CI pass | Full case, storage restart, WebGL failure, client validation, Windows launcher and green remote CI |
| M1-06 | P0 | Lead | Done | Specification, decisions, game design, backlog and progress report in repo |

## Current delivery and next milestones

| ID | Priority | Milestone | Status | Acceptance / dependency |
| --- | --- | --- | --- | --- |
| M2-01 | P1 | Private characters | Done; local + CI pass | Assign character cards; public identity and private goals separated server-side |
| M2-02 | P1 | Private characters | Done; local + CI pass | Guest-only secret delivery and host roster; reconnect restores assignment without leaking secrets |
| M2-03 | P1 | Participation | Done; local + CI pass | Introductory round, accusation rationale and final reconstruction tied to motives |
| M2-04 | P1 | Rehearsal | Automated four-guest flow passed; human rehearsal pending | Four actual players, phones + TV, 20–30 minute rehearsal and feedback record |
| M3-01 | P1 | Optional AI | Done; local + CI pass | Explicit Responses adapter, released-fact plan, strict validation and deterministic fallback |
| M3-02 | P1 | Optional AI | Done; local + CI pass | Grounding/injection/timeout/request-budget tests, offline-only automation |
| M3-03 | P1 | Live validation | Not enabled | User-configured key/model/spend and deliberate live smoke test; no credentials in Git/chat |
| M3-04 | P2 | Dialogue design | Backlog | Evaluate factual validation before allowing arbitrary model-written prose |
| M4-01 | P2 | Speech | Planned | Consent, push-to-talk transcription, pause/mute/interruption and visible audio state |
| M4-02 | P2 | Character | Planned | Licensed rigged avatar, expressive gestures and readable captions |
| M4-03 | P2 | Speech/avatar | Planned | Custom voice and timestamped visemes; actual lip-sync validation |
| M5-01 | P2 | Hosted pilot | Planned | HTTPS, authentication, session expiry, rate limits, monitoring and backup/restore |
| M5-02 | P2 | Scaling | Planned | Shared room store/pub-sub before any multi-worker deployment |
| OPS-01 | P1 | Resilience | Backlog | Bound slow-client sends and implement room expiry/pruning |
| OPS-02 | P1 | Data lifecycle | Backlog | Versioned case migrations/export and user-visible room deletion |

## Routine decisions and user decisions

The lead resolves architecture and implementation choices within the accepted scope. External model/voice spend, avatar licensing or public hosting need a concrete proposed integration before user input. A paid provider adapter exists but remains disabled by default; no paid invocation, recording, purchased asset or public deployment is enabled in the current rehearsal.

Planning context: earlier availability was three weeks part-time, roughly 10–12 hours/week. M1 supplies reliable recovery; M2 now supplies playable character participation. M3 now adds optional bounded planning; human rehearsal and deliberate live-provider validation remain next. Production-quality voice, avatar and hosting are separate milestones, not an implied three-week promise.

## TalkingHead audition — October 28, 2026

| ID | Owner | Status | Acceptance |
| --- | --- | --- | --- |
| M4-A1 | Backend | Implemented | Local Windows recording generator; validated fixed sample API |
| M4-A2 | Frontend | Implemented | Lazy TalkingHead audition, actual word-timed visemes, stop/change and audio fallback |
| M4-A3 | Assets | Done | CC0 sample provenance; MIT library notices |
| M4-A4 | Lead / QA | Local checks passed; CI pending | Game regression, browser mouth movement, real Windows playback, CI |
| M4-A5 | Product | Pending later | Select final British voice and detective asset; live game speech integration |

- M4-A6: Implemented restrained lip strength and gentle upper-face expression from user feedback; production build and browser verification passed locally; remote CI pending. Final voice/face remain open.

## Current increment: playable local TV performance

| ID | Owner | Status | Acceptance |
| --- | --- | --- | --- |
| M4-T1 | Backend | Implemented; local tests pass | Bounded Windows local speech for authenticated current public dialogue only |
| M4-T2 | Frontend | Implemented; local playback pass | Shared approved renderer; opt-in TV speech and interruption |
| M4-T3 | Lead / QA | All seven browser tests pass; CI pending | Browser playback/pause/mute/stale/error and privacy regression |
| M4-T4 | Lead | Implemented | Windows setup, limits, decisions and verification record |

Approved animation refinement CI is green: run 40715846893. No final voice or asset purchase is authorized or needed for this increment.
