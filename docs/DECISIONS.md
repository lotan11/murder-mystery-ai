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
