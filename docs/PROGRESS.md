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
