# Latest delivery: character and British voice approval audition — October 28, 2026

User requested three premium stylized-realistic detective candidates, three mature British voice candidates and restored playfully sarcastic dry humor. The separate `?view=casting` page now presents three original generated concept portraits (Classic/Modern/Scholar), George/Daniel/Lewis British male Kokoro neural recordings, three identical scene scripts, all nine face/voice pairings, captions, explicit play/stop and a device-local shortlist. The portraits are concepts, not rigged 3D avatars. The shortlist is not approval and cannot activate anything in the game.

Nine real local full-precision neural WAVs were generated at speed 0.92 using verified public model assets in an isolated optional runtime. All nine API/audio paths were inspected and decoded in the real browser, with distinct audio hashes, no clipping at PCM limits, no page errors, no external playback requests and no mobile page overflow. Performance directions are provided for approval; no precise emotion control, measured word timing or candidate lip-sync is claimed. See CASTING_APPROVAL.md for regeneration, licensing boundaries, prompts and limits.

Latest personality direction overrides the earlier serious-only choice: restrained, respectful dry humor is restored in default game narration, scripted framing, hints and approved AI remarks. Existing saved lines are preserved rather than automatically rewritten to serious text. Case facts, solution and identity remain unchanged. Working procedural/TalkingHead avatar, approved mouth/expression profile, local Windows speech and all game interfaces remain intact; no new face or neural voice replaces an active game asset.

Verification: 215 backend tests pass, with two Windows symlink privilege skips; 15 client tests and production build pass; all nine browser scenarios pass (previous seven plus casting comparison/missing-recordings). Real desktop/mobile casting screenshots were reviewed. Character, voice and inflection approval are pending; final 3D production/rigging and any activation follow that approval. Remote CI follows the source push.

# Latest direction: serious detective and case authoring — October 28, 2026

User requested a serious detective without sarcasm and asked for easier story changes. Scripted framing, all event narration, approved AI remarks and local audition lines now use a composed, factual delivery. Existing local David/Zira samples were regenerated. Known earlier authored phrases in saved narration normalize on restore; case facts, credentials and private player data are preserved. Approved restrained avatar animation is unchanged.

Case facts, suspect profiles, role cards, hints, topic aliases and case-event narration now live in the single server-only `backend/cases/blackthorn.json` package, validated at startup. Existing Python exports preserve the engine and case identity. See CASE_AUTHORING.md. This is an authoring foundation, not a multi-case selector/editor: fixed role IDs, three investigation acts and the Blackthorn visual theme remain explicit limits. Material plot edits require fresh-room rehearsal and a versioning/migration decision before use with active saves.

197 backend tests pass, with one Windows symlink privilege skip. Production build and all seven browser scenarios pass. Real Windows speech generated the new serious opening successfully (9.895 seconds). Focused animation checks are repeated after spacing the synthetic fixture transitions for slow CI runners. Previous TV performance source passed independent CI in run 40720750631 (same code as the earlier source run; the earlier run missed closely spaced synthetic mouth transitions on a slow runner; current fixtures spread word timings across the clip to improve observation without weakening assertions). Current milestone CI follows its push.

# Latest delivery: playable local TV performance — October 28, 2026

The approved TalkingHead animation now speaks the game’s current public detective dialogue in optional TV mode. The original evidence stage remains the default; one shared renderer serves both the audition and TV. Explicit enable, voice selection, stop, mute and replay are available. Pause, disconnect, revision change and navigation cancel audio and invalidate delayed responses. Identical dialogue is not repeated for unrelated room updates.

A bounded hidden Windows PowerShell subprocess uses installed David/Zira voices and the existing SAPI timing helper. The HTTP request accepts only a voice choice, not text. A derived read-only TV capability travels in the TV link fragment and Authorization header, leaving organizer control credentials separate. Generated files are temporary and responses are no-store. No database migration, microphone, paid speech provider or final detective appearance is added.

Verification: 188 backend tests pass (one Windows symlink privilege skip); 15 client tests and production build pass. Audition and new TV browser scenarios pass. Real Windows API generation and real TV playback were separately exercised: actual mouth influence 0.252, moving visemes and active upper-face expression observed; host pause stopped playback; no page errors. Screenshot reviewed in the local work folder. All seven browser regression scenarios pass. Source commit `28e8996` is pushed. [Independent CI](https://github.com/lotan11/murder-mystery-ai/actions/runs/40720061315) passed backend/client/build checks and was installing browser dependencies at handoff; remote browser completion is not yet claimed.

Try it: open the organizer, create an evening, follow its TV stage link, select Animated detective and Enable local voice. Use the host tab to advance/pause. See TV_PERFORMANCE.md for setup and limitations. Final British voice, bespoke detective rig and microphone remain future choices; existing US voices and female CC0 sample are explicitly provisional.

# Performance refinement — October 28, 2026

User accepted TalkingHead but requested smaller lip movement and more expression. Reduced final viseme strength to 45%, capped at 0.38; added subtle speech-weighted upper-face acting and modest head motion. Playback completion now waits until speech has actually begun, addressing a race exposed by prior remote CI. Synthetic browser recordings last at least eight seconds so slow CI can test interruption during playback. Real local Windows samples remain unchanged. Production build and all six browser flows passed; live Windows playback observed mouth influence 0.209 with upper-face expression active. Screenshot reviewed. Latest audition checks rerun after generation-reset guard.

# Latest delivery: TalkingHead audition — October 28, 2026

Separate local audition at `/?view=audition` now compares actual installed David/Zira speech on the CC0 TalkingHead sample. Real SAPI starts drive actual facial morphs; durations are estimated. Windows browser review observed mouth movement and stop reset with no external requests or page errors. The female sample is not final Wobblebottom; no premium voice, microphone or live game speech integration is claimed. See VOICE_AUDITION.md for Windows preparation.

Local verification: 157 backend tests passed, one Windows symlink privilege skip; 15 client tests and production build passed. All six browser scenarios passed, covering the existing game and new audition. Remote CI follows the source push.

# Project progress and handoff

Updated October 27, 2026. Authoritative handoff for the integrated repository. Read SPECIFICATION.md, TASK_BOARD.md, DECISIONS.md, AI_INTEGRATION.md and the spoiler-marked GAME_DESIGN.md.

## Current delivery: M3 — optional grounded AI planning

**Software foundation accepted and pushed to main.** Source commit `2485145` passes local tests and [independent GitHub CI](https://github.com/lotan11/murder-mystery-ai/actions/runs/40607478899). The acceptance-record commit changes documentation only. Live provider/account/model operation is not claimed tested or enabled. The application continues to run in free scripted mode by default.

Delivered in the existing application:

- Optional OpenAI Responses adapter accepts only a structured selection of released clue IDs plus an approved Wobblebottom remark. The server renders authored factual text; arbitrary model-written prose is not accepted.
- Provider requests exclude private cards, roster, introductions, accusation reasons, credentials and hidden case facts. Only the typed question and released evidence are sent.
- Provider mode, paid consent, local key and explicit model are all required. No default paid model, automatic paid calls or retries.
- Durable per-room request allowance, default five attempts. Reservations save before dispatch; reset/restart do not replenish attempts.
- Tracked background requests run outside the room lock. Same-socket host controls remain responsive; stale answers are discarded after room changes.
- Timeouts, refusal, provider errors, malformed plans and exhausted allowance use safe scripted behavior. Raw diagnostics and credentials never become UI messages.
- Actual-source, busy, fallback, configuration and usage indicators appear in host/guest views. Configured provider use is disclosed before questions are submitted.
- SQLite schema 3 migrates schemas 1 and 2 atomically; source/reason and attempt counters persist.
- Windows launcher accepts an explicit environment file. `.env.example` stays offline by default; real environment files remain ignored.

## Verification

- 134 backend tests pass: previous game/privacy/migration tests plus 52 mocked adapter tests and 25 orchestration cases.
- 15 client tests and production build pass. [GitHub CI](https://github.com/lotan11/murder-mystery-ai/actions/runs/40607478899) independently passes all backend, client, build and browser checks.
- Four browser scenarios pass: full host/TV/phone case, four-guest role privacy/introductions/rationales, renderer failure and explicit scripted-default status.
- A real Windows launch with `-EnvFile .\.env.example` migrated schema-2 saves to schema 3; every previous public-state field and host access were preserved. Health confirms paid AI disabled and React returns HTTP 200.
- All automated tests force offline defaults and forbid real outbound HTTP. The integration is tested with injected transports/fake planners, not a live account.

## How to test now

Refresh the existing preview or follow README/start.ps1, create an evening and play as before. The host integration panel identifies the actual reply source and provider state. Nothing needs an API key to rehearse. Private characters, clues, votes, introductions and saved games remain available.

For deliberate optional live assistance, follow AI_INTEGRATION.md and configure a local key, compatible explicit model and paid consent, then restart with the selected environment file. A real provider smoke test and human dinner rehearsal remain manual acceptance steps, separate from the completed software checks.

## Next work

1. Human rehearsal: pacing, clue comprehension, role comfort and real phone/TV readability. Log observed issues in TASK_BOARD.md.
2. Optional live-provider smoke test only after the user configures account/model/spend locally; record exact model and observed fallback behavior without recording credentials.
3. M4: consented microphone/transcription and custom voice/rigged avatar/lip sync remain separate features. No microphone access is implemented by the model planner.
4. Free-form model-written dialogue, if desired later, requires a stronger factual validation design rather than silently widening this bounded adapter.

## Current limits and blockers

No blocker prevents the scripted game. Live AI use requires explicit local configuration and account/model access; no paid invocation has been performed. Model assistance selects authored facts and remarks rather than inventing natural-language case testimony. Device speech remains optional; microphone, custom voice, rigged avatar, lip sync and public hosting remain absent. SQLite supports one backend process. Request allowance is per room and is not a dollar or account-wide budget.

## Accepted history and continuity

M1 source e27ab9a established durable Blackthorn rehearsal. M2 source 091aa6b added private characters and four-guest participation; CI run 40604506205 passed, and documentation head 5cc18a2 also passed. M3 extends that single application and preserves case version 1 because the murder facts/solution are unchanged.

Inspect Git status, branches/PRs and CI before continuing. Keep one file owner per parallel stream, integrate tests, update these documents and commit accepted increments. No scheduled background work is configured.
