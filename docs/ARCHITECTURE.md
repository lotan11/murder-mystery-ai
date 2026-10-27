# Architecture

The browser renders React views and a Three.js stage. FastAPI owns every room's canonical state. Clients send commands rather than editing local game state; each accepted mutation broadcasts a fresh snapshot. Reconnection receives the same public projection. Organizer and guest credentials confer distinct capabilities; the TV is a spectator.

The authored mystery and progression rules stay in the engine. Dialogue receives only released facts. A future language model may phrase those facts but must never select the killer, unlock evidence, advance an act, or override organizer controls. Add a provider that returns validated performance text and falls back to the deterministic provider on timeout or invalid output. Do not send hidden solution data before resolution.

Future microphone pipeline: explicit guest consent → audio capture → transcription → the existing dialogue command. Keep raw audio retention off by default, handle TV echo and mute/pause, and display recording state. This pipeline is absent from the slice.

Future avatar pipeline: licensed character with a rig and blend shapes → animation controller → audio timestamps/visemes. The current geometry, idle motion and optional browser voice do not implement this pipeline. Keep captions available when audio or WebGL fails.

The evidence stage deliberately combines a 3D host/environment with crisp HTML documents. This preserves readable clues on televisions and phones without embedding critical text in textures.

Sources consulted during implementation: [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/) and [Three.js scene fundamentals](https://threejs.org/manual/pages/creating-a-scene.html).

SQLite persists committed room records; live WebSocket clients and asyncio locks remain process-local. Startup restores rooms, and accepted commands save before acknowledging/broadcasting. Persistence failures roll back the candidate mutation. A single server process owns all rooms; do not use multiple workers against this design. Case/version pins protect future resumptions from incompatible canon changes. See `DECISIONS.md` for accepted tradeoffs.
