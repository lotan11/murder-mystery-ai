# Architecture

The browser renders React views and a Three.js stage. FastAPI owns every room's canonical state. Clients send commands rather than editing local game state; each accepted mutation broadcasts a fresh snapshot. Reconnection receives the same public projection. Organizer and guest credentials confer distinct capabilities; the TV is a spectator.

The authored mystery and progression rules stay in the engine. Dialogue receives only released facts. A future language model may phrase those facts but must never select the killer, unlock evidence, advance an act, or override organizer controls. Add a provider that returns validated performance text and falls back to the deterministic provider on timeout or invalid output. Do not send hidden solution data before resolution.

Future microphone pipeline: explicit guest consent → audio capture → transcription → the existing dialogue command. Keep raw audio retention off by default, handle TV echo and mute/pause, and display recording state. This pipeline is absent from the slice.

Future avatar pipeline: licensed character with a rig and blend shapes → animation controller → audio timestamps/visemes. The current geometry, idle motion and optional browser voice do not implement this pipeline. Keep captions available when audio or WebGL fails.

The evidence stage deliberately combines a 3D host/environment with crisp HTML documents. This preserves readable clues on televisions and phones without embedding critical text in textures.

Sources consulted during implementation: [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/) and [Three.js scene fundamentals](https://threejs.org/manual/pages/creating-a-scene.html).

SQLite persists committed room records; live WebSocket clients and asyncio locks remain process-local. Startup restores rooms, and accepted commands save before acknowledging/broadcasting. Persistence failures roll back the candidate mutation. A single server process owns all rooms; do not use multiple workers against this design. Case/version pins protect future resumptions from incompatible canon changes. See `DECISIONS.md` for accepted tradeoffs.

M2 adds a separate private projection for each authenticated guest socket. Public snapshots include role names, voluntary introductions and finale accusation explanations; character briefs/objectives never enter that projection or the dialogue provider. The room persists role assignments, introductions and accusation reasons, while canonical role-card text stays in `backend/characters.py`. Schema 1 is validated and upgraded atomically to schema 2 before serving requests. Browser storage retains only credentials, not private card contents.

M3 adds an explicitly enabled Responses planner that returns evidence IDs and an approved remark, never free-form factual prose. Public provider context is allowlisted; final dialogue comes from authored released facts. SQLite schema 3 retains request attempts and reply source/reason. Requests are reserved durably, then run in a tracked task outside the room lock; a changed revision/act/pause rejects stale output. Configuration and limitations are specified in `AI_INTEGRATION.md`.

## Optional local timed TV speech

`backend/local_speech.py` supplies public availability, host-only capability configuration and a scoped authenticated speech POST. The only accepted request content is a David/Zira voice ID. Current room dialogue and revision are captured under the existing room lock; generation runs outside it, then state is checked before returning. A single renderer slot, fixed executable/script, literal JSON input, bounded output/time and kill/reap cleanup contain Windows SAPI work. No audio URL/cache is exposed; validated WAV data is returned inline with word timings and no-store headers. Temporary files are removed.

`TalkingDetective.tsx` owns the shared restrained renderer and TV playback coordination; `VoiceAudition.tsx` uses the same renderer. The TV supplies an optional avatar slot to the existing `Stage.tsx`, preserving evidence and captions without a second procedural GPU renderer. Playback is opt-in and protected by generation counters, request aborts and room-state checks. The original stage and browser device read-aloud remain available; device read-aloud is disabled during animated mode. No database migration is required.

## Separate casting approval surface

`Casting.tsx` is lazy-loaded only at `?view=casting`; candidate portraits live under the dedicated public casting path. `backend/casting.py` exposes validated read-only authored manifest and WAV routes, with a strict finite set of voice/scene IDs, file bounds and symlink guards. Optional `scripts/prepare-casting.py` generates recordings from pinned verified model assets in an isolated runtime; no main-server dependency or HTTP synthesis endpoint is added. Cached recordings/models stay ignored. Casting UI selection/shortlisting has no command path to room state or active game speech.

## Approved live Lewis renderer

`scholar_speech.py` and its fixed local Python worker provide a separate authenticated current-public-dialogue endpoint using the optional isolated Kokoro runtime and verified cached assets. It reuses the existing host/read-only TV capability, accepts an empty request, and returns validated inline WAV with the approved 1.05 playback rate after a state recheck. No word timing is invented. `ScholarPerformance.tsx` owns selected portrait audio lifecycle; `Stage.tsx` still owns shared evidence/captions. Existing SAPI/TalkingHead and original procedural modes are preserved under explicit TV presentation selection.

## Reproducible Scholar asset workbench

Optional portable Blender and pinned MPFB generate the anatomical development asset from assets/character-production settings. The canonical editable blend, local GLB and inspection report are versioned. CharacterLab is a lazy, separate route with ordinary GLTFLoader/OrbitControls, real scene inventory and no game-state or audio integration. StaticFiles serves only its dedicated exported asset folder. Standard-library GLB inspection distinguishes missing bones/expressions from actual geometry loading; neither inventory nor rendering is treated as likeness or acting approval.
