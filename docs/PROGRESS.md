# Project progress and handoff

Updated October 27, 2026. Authoritative handoff for the integrated repository; read with SPECIFICATION.md, TASK_BOARD.md, DECISIONS.md and the spoiler-marked GAME_DESIGN.md.

## Current milestone: M2 — playable dinner characters

**Software milestone accepted and pushed to main.** Source commit `091aa6b` passes local tests and [GitHub CI](https://github.com/lotan11/murder-mystery-ai/actions/runs/40604506205). The follow-up acceptance commit updates documentation only. A four-person human dinner rehearsal remains pending; automated browser sessions do not establish story pacing or acting comfort.

Delivered in the existing application:

- Three exclusive suspect roles and expandable visiting investigators, with private briefs, objectives and performance guidance in `backend/characters.py`.
- Guest-private WebSocket packets bound to authenticated identity, separate from public state and never delivered to host, TV or other guests. The dialogue provider still receives only the public snapshot.
- Host assignment controls in the unpaused lobby; default assignments follow join order. Private cards start concealed and are not stored in browser storage.
- Optional guest-authored public introductions, persistent across reconnect/restart.
- Optional accusation reasons, private before act four and shared with the table at the finale.
- Reset preserves party identities and roles while clearing introductions, case progress, votes and reasons.
- Atomic schema-1-to-2 migration preserves existing M1 saves, credentials and progress. Invalid data or failed migration stops startup without deleting the database.

## Verification

- 57 backend tests pass, covering story/cards, progression, access/privacy, forged identity rejection, migration, rollback, restart and malformed data.
- 12 client tests and the TypeScript/production build pass.
- [Independent GitHub CI](https://github.com/lotan11/murder-mystery-ai/actions/runs/40604506205) passes backend/client tests, build and all browser scenarios.
- Three browser scenarios pass: full host/TV/phone case, four independent guests with isolated roles/introductions/reassignment/finale rationales, and WebGL fallback.
- A real Windows server upgrade migrated the existing schema-1 database to schema 2. Case progress, party identities, host credentials and HTTP 200 frontend were preserved.
- Four-guest mobile viewports have no horizontal overflow. Real phones, physical TV readability and a human dinner rehearsal remain manual work.

## How to test now

Run `start.ps1` using the root README, or refresh the local preview if the lead has it running. Create a fresh evening for the first character rehearsal. Join four guest screens. The first three receive suspect roles and the fourth becomes an investigator; the host can adjust roles before starting. Private briefs stay hidden until a guest chooses to reveal them. The culprit player has actor knowledge and helps stage the mystery; no player must fabricate evidence or lie. See TEST_PLAYBOOK.md for the full rehearsal.

## Next work

1. Capture the human rehearsal: pacing, clue comprehension, role comfort and mobile readability. Log concrete fixes in the task board.
2. M3: define a grounded optional AI provider, structured output validation, timeout/fallback and spoiler tests. Preserve free scripted mode. Live-provider testing needs configured credentials and an agreed spending choice; do not enable a paid dependency silently.
3. Keep microphone capture, custom TTS, a licensed rigged avatar and true lip sync in their separate M4 workstream.

## Current limits and blockers

No blocker prevents running this milestone. Dialogue is scripted, device speech optional, the avatar procedural; microphone, custom voice, lip sync and public hosting are not connected. SQLite remains single-process local persistence, not distributed hosting. Introductions are intentionally public user submissions; guests may disclose their own information voluntarily. Private data isolation protects automatic delivery, not statements a player chooses to share.

## Accepted history and continuity

M1 source `e27ab9a` established recoverable Blackthorn rehearsal and passed GitHub CI (run 40600489863); later documentation head `30d0ab9` also passed. PR1 was integrated rather than duplicated. M2 extends that codebase and retains case ID/version 1 because the murder facts and solution have not changed.

Inspect Git status, branches/PRs and CI before continuing; this report and the backlog carry context across sessions. Keep explicit file ownership for parallel work, integrate and test in one application, then update the handoff and commit. No scheduled background work is configured.
