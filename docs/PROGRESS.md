# Project progress and handoff

Updated October 27, 2026. This is the lead's authoritative handoff. Read it with `SPECIFICATION.md`, `TASK_BOARD.md`, `DECISIONS.md` and the spoiler-marked `GAME_DESIGN.md`.

## Current milestone: M1 — reliable Blackthorn rehearsal

**Accepted and pushed to main.** Source commit `e27ab9a` passes local acceptance and [GitHub CI](https://github.com/lotan11/murder-mystery-ai/actions/runs/40600489863). The acceptance-record commit only updates documentation. The application is ready for a short human rehearsal; this is not a claim that the entire production platform is complete.

Delivered in one application:

- Reviewed and integrated the existing verification branch/PR1 rather than creating a competing prototype.
- Canonical **The Last Toast at Blackthorn Manor**, with a coherent timeline and fair clue chain.
- Wobblebottom reviews referenced released clues, discusses suspects, offers hints and gives bounded recaps; no hidden-canon import into the dialogue provider.
- SQLite stores room progress, credentials, guests, dialogue, pause state and votes. Accepted mutations commit before acknowledgement; failed writes restore state. Case/version pins reject incompatible saves visibly without deleting them.
- Host controls follow actual clue gates. Guests get useful prompts and replies near their question field.
- Guest devices no longer render an invisible avatar. Fonts no longer require network access. TV fallback preserves captions/evidence after WebGL failure.
- Repository specification, game design, decisions, backlog, rehearsal guide and contributor operating agreement provide continuity across work sessions.

## Acceptance evidence

- 37 backend tests and 9 client tests pass; TypeScript/production build passes.
- Two browser scenarios pass: complete host/TV/phone flow and renderer recovery. Long TV dialogue uses compact evidence summaries and readable caption sizing; full descriptions remain in guest notebooks.
- The Windows launcher was stopped and restarted on port 8018: committed act-one evidence, pause state and host credential survived; the built React page returned HTTP 200.
- Original main and the pre-existing verification branch had CI timeouts in the full-case browser test. The new run removes remote font waits and hidden guest GPU work, uses serial browser scenarios and retains all progression/reconnect assertions under a bounded 90-second case limit. The complete independent check now passes: [M1 CI](https://github.com/lotan11/murder-mystery-ai/actions/runs/40600489863).

## What is still simulated or absent

AI dialogue remains deterministic; external model calls are not enabled. Browser speech is real but optional and device-dependent. Microphone capture, custom TTS, production rigged avatar, speech-driven lip sync and public deployment are absent. The procedural avatar is a placeholder. SQLite is real persistence for one backend process, not distributed storage or account authentication.

## Next milestone: M2 — private dinner characters

1. Define three character cards and investigator/spectator behavior for larger parties; retain fixed case IDs and authored solution.
2. Deliver private objectives through authenticated per-guest payloads, separate from the public room snapshot; test cross-guest and TV isolation.
3. Add a short introduction round and accusation rationale, then run the four-player rehearsal.

Do not introduce a real AI or microphone dependency to complete M2. Keep the provider seam and free scripted mode while the dinner game itself becomes more playable.

## Blockers and decisions

No user decision blocks M1 or M2 implementation. Real phone/TV/dinner rehearsal needs the user's participation and is explicitly unverified. Future provider credentials/spend, character licensing, voice identity and public hosting need concrete proposals when those milestones are ready. SQLite saves contain bearer credentials and stay ignored by Git; incompatible save versions require recovery/migration, not silent deletion.

## How to resume without relaying chat history

Inspect Git status, branches/PRs and CI first; read this handoff and the task board. Maintain one owner per component. Implement the next accepted milestone, run its tests, update these documents and commit the integrated result. No scheduled background work is configured; work continues when this chat is active or the user requests the next milestone.
