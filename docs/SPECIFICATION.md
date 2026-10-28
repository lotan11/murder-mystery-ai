# AI Murder Mystery Dinner platform specification

Status: authoritative working specification, updated October 27, 2026.

## Product

Let an organizer run a dinner mystery from a host desk while guests participate on phones and a shared television presents Detective Reginald P. Wobblebottom, dialogue, and cinematic evidence. The user should test complete milestones rather than assemble work from separate conversations.

Launch case: **The Last Toast at Blackthorn Manor**. Tone: elegant intrigue with a composed detective, playfully sarcastic dry humor, natural conversational timing and subtle expressions. Humor never humiliates guests, replaces facts or becomes slapstick. The case must have an authored, consistent solution independent of an AI model.

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
| M3: Optional grounded AI assistance | Responses adapter selects released facts/approved remarks; strict validation, request limits and timeout/fallback tests; offline mode preserved. Live account/model smoke test recorded separately |
| M4: Voice and performance | Consented microphone/transcription, custom voice if selected, interruption, rigged character and visemes; each component optional and tested |
| M5: Hosted pilot | Durable deployment, account/session boundaries, room expiry, rate limits, monitoring, HTTPS and tested recovery |

M3–M5 require separate acceptance and actual integration work; they are not delivered by installing a package or labeling the detective “AI.” Character licensing, voice identity, provider spend and public hosting are material choices for the user when those milestones are prepared.

## Scope for the current rehearsal

One case, 3 authored suspects, 1–24 connected guest identities, trusted local network, one backend process, SQLite on one machine. Intended initial rehearsal: 3–6 guests, approximately 20–30 minutes. M2 assigns the first three guests to suspect characters and additional guests to visiting investigators. Character briefs and objectives use guest-only payloads. Introductions are optional and deliberately public; accusation reasons stay private until the finale. The culprit player receives actor knowledge, so they participate in the drama rather than a blind guessing contest. Actual phones and a physical TV must be rehearsed separately from viewport tests.

## Quality gate

Backend tests cover progression, persistence, access separation, malformed input and spoiler protection. Client tests cover snapshot validation and transport. Browser tests cover a full cross-screen case, restored identity, no horizontal overflow and avatar failure recovery. Build and CI must pass. Record failures and manual checks honestly in `VALIDATION.md` and `PROGRESS.md`.

## Optional voice audition

A separate `?view=audition` route compares locally prepared David/Zira speech on a licensed TalkingHead sample. Must support explicit play/stop, voice changes, honest placeholder labels and audio-only failure recovery. It does not require or enable paid AI, microphone access or live game speech. See VOICE_AUDITION.md.

## Optional TV local performance

Keep the original TV stage available. An opt-in TalkingHead performance can speak current server-selected public dialogue with installed Windows voices, explicit enable/mute/replay, pause and disconnect cancellation, captions and clear sample-avatar labels. Guest private material and arbitrary request text must never reach synthesis. Stale generation must not play after state changes. Final British voice, bespoke detective rig, microphone and premium services are outside this increment.

## Character and voice approval sandbox

Offer three premium stylized-realistic mature detective concept portraits and three British male neural voice candidates at `?view=casting`. Compare the same three short scenes across every face/voice pairing without autoplay. Save a device-local shortlist; no candidate replaces active game assets until user approval. Distinguish concepts from rigged 3D avatars, generated voice audio from test tones, and performance direction from precise emotional control. See CASTING_APPROVAL.md.
