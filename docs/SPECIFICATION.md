# AI Murder Mystery Dinner platform specification

Status: authoritative working specification, updated October 27, 2026.

## Product

Let an organizer run a dinner mystery from a host desk while guests participate on phones and a shared television presents Detective Reginald P. Wobblebottom, dialogue, and cinematic evidence. The user should test complete milestones rather than assemble work from separate conversations.

Launch case: **The Last Toast at Blackthorn Manor**. Tone: elegant intrigue with a dry, playfully sarcastic detective. Wobblebottom punctures weak deductions without humiliating guests. No slapstick host performance is required. The case must have an authored, consistent solution independent of an AI model.

## Users and surfaces

| Surface | Responsibilities |
| --- | --- |
| Host | Create room, invite, pace acts, release clues, pause/resume, resolve/reset |
| Guest | Join, review evidence, question detective, request hints/recaps, accuse |
| TV | Display the detective, readable evidence, captions, act and paused state |
| Lead/maintainer | Keep specification, story, backlog, decisions, verification and handoff in Git |

## Required system behavior

1. Server owns progression, clues, identities, votes and solution. Clients submit commands and replace state with authoritative snapshots.
2. Three acts gate five clues. All current clues must be released before the host advances. Accusations open in act three.
3. Reconnect restores the current room and guest identity. Committed game state survives server restart.
4. Guests cannot operate host controls. Public state never contains bearer credentials or unrevealed clue descriptions/solution.
5. Dialogue references only facts released to that room. Optional AI cannot advance the game or change the culprit.
6. Three.js avatar is a replaceable procedural placeholder with a fallback. Captions and guest participation work without WebGL or speech.
7. No microphone recording, paid AI, custom voice, or lip sync is implied by a mock. Speech is opt-in and labeled accurately.
8. Windows startup, automated tests and a reproducible full-case rehearsal remain supported.

## Playable milestones

| Milestone | Acceptance gate |
| --- | --- |
| M0: First slice | Host + guest + TV complete the authored case with real WebSockets and scripted detective |
| M1: Reliable rehearsal | Consistent Blackthorn canon, recoverable saved room, contextual detective questions, useful host gates, full browser flow and CI green |
| M2: Dinner participation | Assigned characters, private goals/secrets with per-player projection, optional introduction and private accusation rationale; four-guest automated flow plus a separately recorded human rehearsal |
| M3: Optional real dialogue | One explicit provider adapter, validated structured responses, no spoiler leakage, timeout/fallback behavior; offline/scripted mode preserved |
| M4: Voice and performance | Consented microphone/transcription, custom voice if selected, interruption, rigged character and visemes; each component optional and tested |
| M5: Hosted pilot | Durable deployment, account/session boundaries, room expiry, rate limits, monitoring, HTTPS and tested recovery |

M3–M5 require separate acceptance and actual integration work; they are not delivered by installing a package or labeling the detective “AI.” Character licensing, voice identity, provider spend and public hosting are material choices for the user when those milestones are prepared.

## Scope for the current rehearsal

One case, 3 authored suspects, 1–24 connected guest identities, trusted local network, one backend process, SQLite on one machine. Intended initial rehearsal: 3–6 guests, approximately 20–30 minutes. M2 assigns the first three guests to suspect characters and additional guests to visiting investigators. Character briefs and objectives use guest-only payloads. Introductions are optional and deliberately public; accusation reasons stay private until the finale. The culprit player receives actor knowledge, so they participate in the drama rather than a blind guessing contest. Actual phones and a physical TV must be rehearsed separately from viewport tests.

## Quality gate

Backend tests cover progression, persistence, access separation, malformed input and spoiler protection. Client tests cover snapshot validation and transport. Browser tests cover a full cross-screen case, restored identity, no horizontal overflow and avatar failure recovery. Build and CI must pass. Record failures and manual checks honestly in `VALIDATION.md` and `PROGRESS.md`.
