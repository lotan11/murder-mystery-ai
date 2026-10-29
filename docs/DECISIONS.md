# Architectural decision log

Accepted decisions apply until superseded by a dated entry. Code remains the authority for actual behavior.

| ID / date | Decision | Reason and consequence |
| --- | --- | --- |
| ADR-001 / 2026-10-27 | One FastAPI authority, React surfaces, native WebSockets | A full room snapshot after each accepted command keeps TV and phones recoverable; no parallel browser engine |
| ADR-002 / 2026-10-27 | Deterministic authored case; dialogue cannot mutate progression | Solution and clue gates must remain consistent even if a future model fabricates text or fails |
| ADR-003 / 2026-10-27 | Blackthorn Manor is the canonical location | User explicitly selected this name; earlier Blackwood wording is replaced in current story/UI, stable clue and suspect IDs retained |
| ADR-004 / 2026-10-27 | SQLite persistence for single-process local rehearsal | Atomic saves survive restart without an external service; multi-worker/shared hosting remains out of scope |
| ADR-005 / 2026-10-27 | Browser-stored bearer tokens for host and guest recovery | Sufficient for trusted LAN prototype; not production authentication. No credentials in public snapshots or screenshots |
| ADR-006 / 2026-10-27 | HTML evidence/captions with procedural Three.js avatar | Readable clues survive renderer failures. A licensed rig and viseme controller will replace the placeholder later |
| ADR-007 / 2026-10-27 | Scripted dialogue and optional device speech by default | Every milestone can run without a paid provider. Microphone, AI generation, custom TTS and lip sync need distinct adapters and tests |
| ADR-008 / 2026-10-27 | Repository documents and explicit file ownership coordinate streams | The user should not move context across chats. The lead integrates reviewed changes and records acceptance evidence |
| ADR-009 / 2026-10-27 | Remove remote font dependency; avoid rendering avatar on guest phones | Offline startup and lower GPU load improve real phone usability and CI consistency |
| ADR-010 / 2026-10-27 | Bounded 90-second full-case browser test, serial browser specs, traces on failure | The original 45-second whole-case limit failed in CI at different late steps. Preserve assertions while removing unnecessary load and retaining useful diagnostics |

## Integration boundary for future services

Before an external AI, transcription or voice service becomes a dependency, add an ADR defining data sent, consent, failure behavior, credentials and spending controls. A provider error must fall back or leave a clear recoverable UI; it must never silently unlock clues. Licensed avatar assets need provenance and redistribution permission recorded in the repository.

## M2 decisions — October 27, 2026

- **ADR-011: Separate guest projection.** Authenticated guests receive `private` packets bound to their socket identity. Host/TV/public snapshots carry role names and submitted introductions, never private briefs or objectives. The dialogue provider still receives public facts only.
- **ADR-012: Fixed suspect characters, expandable investigators.** The first three joiners receive Ada, Felix and Vale; additional guests investigate. Named roles are exclusive and may be reassigned by the host only in the unpaused lobby. Character cards live in `backend/characters.py`, while murder facts remain in `backend/mystery.py`.
- **ADR-013: Actor knowledge is explicit.** The culprit's player knows their guilt privately and helps stage the deduction; other guests solve the case. No character requires fabricated evidence or forced lying. A blind-all-players game would need a different design, not secretly withholding a role's premise.
- **ADR-014: Additive saved-room migration.** Schema 2 adds assignments, introductions and accusation reasons. Existing schema-1 rooms validate before a single atomic migration transaction. Case ID/version and existing progress/credentials remain unchanged; invalid records or failed migration preserve the database and stop startup.
- **ADR-015: Deliberate disclosure.** Guest-authored introductions are public after submission. Accusation reasons are private until act four, then become part of the shared reconstruction. Reset retains identities/roles but clears introductions, votes and reasons. Private briefs are hidden by default and never written to browser storage.

## M3 decisions — October 27, 2026

- **ADR-016: Model-assisted planning, authored facts.** First live-provider interface selects only released clue IDs plus an approved remark. The server composes factual dialogue. Arbitrary model prose is excluded; JSON structure or evidence citations alone cannot establish factual grounding. Free-form model writing remains a separate future decision.
- **ADR-017: Explicit paid configuration.** Provider, paid consent, local key and explicit model are all required. Default scripted mode and UI remain runnable without credentials. No default model, credential collection form, paid test call or automatic retry is introduced. The existing HTTPX dependency calls Responses directly.
- **ADR-018: Durable attempt allowance.** Schema 3 adds request count and actual reply source/reason. Reservations commit before dispatch; reset/restart do not replenish attempts. Earlier schemas migrate atomically. The count is per room, not a dollar cap or an account-wide budget.
- **ADR-019: Responsive asynchronous orchestration.** A tracked background task performs the network request outside the room lock. One request per room may be in flight. Host controls remain available; revision/act/pause guards discard stale answers. Shutdown cancels outstanding tasks while preserving reservations.
- **ADR-020: Minimal context and offline verification.** Only the typed question and released evidence enter the provider request. Private cards and user-authored introductions/rationales are excluded. Automated tests forbid real outbound HTTP and use mocks; live account/model behavior is explicitly unverified. Actual-source and fallback labels remain visible in the application.

## Voice audition — October 28, 2026

- **ADR-021: Isolated local audition.** Lazy-load TalkingHead on a separate route; preserve the playable game and paid defaults. Use pinned-provenance CC0 sample geometry and MIT animation code. Installed Windows voice recordings remain local and ignored. Fixed authored lines use validated read-only endpoints, with no room state or external provider calls.
- **ADR-022: Honest synchronization evidence.** SAPI word starts plus estimated durations drive actual facial morphs. Browser automation uses clearly marked synthetic tones and observes real mesh motion; real Windows recordings receive separate playback review. Custom British voice, final detective asset and live game speech remain future work.

## TV performance integration — October 28, 2026

- **ADR-023: Local public-dialogue speech.** Optional TV TalkingHead speaks only the server-selected current public detective dialogue. A Windows SAPI subprocess receives UTF-8 JSON through fixed local files, never a client-supplied script or shell string. No external speech provider, microphone or paid dependency. Non-Windows and renderer failures preserve captions and the original stage.
- **ADR-024: Read-only TV capability.** Derive a room-specific speech capability from the organizer secret; it authorizes public speech rendering only, not room control or private data. Carry it in the TV link fragment and send it as an Authorization header. Existing organizer credentials remain local; no schema migration. Treat the capability as sensitive, share only the intended TV link.
- **ADR-025: Explicit playback and cancellation.** Animated TV performance is opt-in and silent until enabled by user gesture. New public dialogue may play while enabled. Pause, disconnect, changed state, stop/mute and unmount cancel audio and reject stale responses. Use one shared renderer for audition and TV so approved restrained visemes remain authoritative. Speech timing remains estimated, and the final detective appearance/voice remain separate choices.

## Serious tone and authoring foundation — October 28, 2026

- **ADR-026: Serious detective direction.** User requested a more serious character without sarcasm. Replace authored jokes across scripted/event/approved-AI dialogue and audition speech; preserve the approved facial profile. Normalize only known earlier authored phrases in saved narration when restoring rooms, preserving facts and player data.
- **ADR-027: Single server-only case package.** Move case facts, cards, hints, topic aliases and event narration into validated `backend/cases/blackthorn.json`. Keep existing import exports and case identity/version for content-preserving extraction. No case selection or unvalidated upload endpoint. Current fixed roster IDs, act count and Blackthorn visual theme remain explicit limits. Semantic story consistency still requires human review and regression tests.

## Character and voice casting — October 28, 2026

- **ADR-028: Latest personality direction overrides ADR-026.** Restore observant, respectful, playfully sarcastic dry humor with natural pacing and subtle expression. No slapstick, guest humiliation or exaggerated animation. Stop automatically rewriting saved narration into the earlier serious style; new narration uses the revised default. Facts, clue gates and approved facial profile remain unchanged.
- **ADR-029: Approval sandbox before activation.** Three generated concept portraits and three offline British neural voices are compared at a separate casting route. Fixed identical scripts across all nine pairings; local shortlist is not approval and cannot activate game assets. Portraits are explicitly not rigged avatars. Existing procedural/TalkingHead game views and Windows speech remain working.
- **ADR-030: Optional local neural generation.** Separate pinned Python environment, full-precision Kokoro model and verified upstream hashes; no paid account or runtime dependency in the core server. Fixed public scenes only, validated cached WAV/manifest routes, no arbitrary synthesis endpoint or guest data. Core runtime/model/dependency licenses are recorded separately. No unmeasured word timing, emotion-control or lip-sync claims.

## Approved Scholar activation — October 28, 2026

- **ADR-031: Approved pairing and exact pace.** User approved The Scholar and Lewis at the slightly faster pace. Live neural dialogue retains bm_lewis synthesis 0.92 and browser 1.05x playback with pitch preservation requested, matching the audition. No silent substitution of another voice/provider.
- **ADR-032: Honest incremental character integration.** Use approved Scholar concept portrait with actual Lewis narration in the TV while the custom rig is produced. Clearly label it as a portrait with 3D rig pending. Preserve original stage, animated sample, Windows speech and captions. Do not pass off the unrelated sample as the selected Scholar.
- **ADR-033: Bounded private-data-safe live neural speech.** Isolated optional Python runtime, fixed verified cached models, empty authenticated request, server-selected current public dialogue only. Bound child work outside room lock, validate WAV output, recheck state and cancel stale client playback. No model downloads or paid services at server startup, no arbitrary text synthesis or anonymous audio URL.

## Scholar asset authoring foundation — October 28, 2026

- **ADR-034: Reproducible local anatomical authoring.** Prepare a checksum-verified portable Blender and pinned MPFB anatomical base in ignored data, with no system-wide install/PATH edits or paid service. Retain an editable source, parametric settings and exported development GLB. Record distinct upstream software and asset licenses.
- **ADR-035: Development workbench before activation.** Inspect real geometry beside the approved portrait at a separate route with camera presets, actual counts and failure recovery. No voice or production activation path. Missing skeleton/facial controls remain explicit; a valid mesh is not an approved speaking avatar. Existing Scholar portrait/Lewis game mode stays intact.
- **ADR-036: Isolate project tests from authoring bundles.** Limit pytest discovery to backend/tests so optional bundled Blender/MPFB third-party test suites are not mistaken for application tests. Core game checks and offline-provider restrictions remain in force.

## November 10 delivery control — October 28, 2026

- **ADR-037: User-set integration deadline.** November 10, 2026 America/Denver is the integration deadline. Track internal art/rig/integration/freeze/rehearsal checkpoints in INTEGRATION_PLAN.md; flag the unfinished facial rig early and preserve the runnable approved portrait/Lewis baseline. Hourly automation now carries this date. The deadline does not authorize spending or deployment.

- **ADR-038: Separate measured rig proofs from production activation.** Keep the canonical static bust unchanged. A private weighted source proves actual skeletal deformation; a separate editable face-study export proves three nonzero pose-derived facial morphs with manual lab controls. Neither is a finished TalkingHead avatar. Require complete deformation, likeness and actual speech-alignment review before switching the game.

- **ADR-039: Measured bust binding before speech.** Export a separate rig study with actual anatomical source-weight transfer, rigid head accessories and rigid torso wardrobe. Check normalized binary weights, neutral preservation, restrained head motion and combined facial poses. Expose only a manual development head control; do not activate the unfinished avatar in TV or imply complete TalkingHead readiness.

- **ADR-040: Real expression units, restrained manual controls.** Reuse pinned MPFB raw brow target geometry, record hashes and transfer deltas to skin/groom with neutral preservation. Keep the original three facial controls unchanged. Limit manual brow lift/lowering separately; raw legacy units are not a complete ARKit or viseme pack and do not establish finished likeness or speech readiness.

- **ADR-041: Manual mouth units before speech mapping.** Add actual pinned anatomical rounding/compression/corner-puller geometry to the weighted study, transfer to skin/groom and cap controls independently. Do not label these three units as a complete phoneme/viseme set or connect unfinished shapes to live game narration. Preserve existing expression displacement inventories, neutral shape and approved portrait/Lewis fallback.
