# Local API contract

`POST /api/rooms` (no body) creates a room and returns `room_id` and a secret `organizer_token`. `GET /api/rooms/{room_id}/state` returns its public snapshot. Room IDs are case insensitive.

Connect to `/ws/{room_id}?role=tv`, `?role=guest`, or `?role=organizer&token=SECRET`. Invalid rooms or organizer credentials close with code 1008. Each connection receives `{type:"state",data:SNAPSHOT}` immediately. Every successful command increments `revision` and broadcasts a complete snapshot to all connected screens. Reconnect receives current authoritative state; the frontend should replace its state rather than merge event fragments.

Commands:

- Guest `{type:"join",name:"Jamie"}` returns `{type:"joined",guest_id,guest_token}` privately, followed by the broadcast. Save that token and reconnect with `role=guest&guest_token=...`; this receives a state followed by joined confirmation. A reconnect does not duplicate a guest.
- Organizer `{type:"control",action:"start"|"pause"|"resume"|"reset"|"advance"|"reveal"}`. Reveal accepts an optional `evidence_id`; without it the next current-act clue is revealed. Start opens act 1. Advance requires every clue in the current act. Advance from act 3 resolves act 4. Reset clears progress and votes while preserving the party and credentials.
- Joined guest or organizer `{type:"dialogue",text:"What about the tea?"}`. This invokes a deterministic mock provider constrained to revealed facts; no external AI request is made.
- Joined guest `{type:"accuse",suspect:"ada"|"felix"|"margot"}` in act 3. One vote per guest; a new vote replaces their previous vote.

Invalid commands return `{type:"error",message:"..."}` only to the sender. A paused room blocks dialogue, voting and act progression; joining, reset and resume still work.

Snapshots include room_id, title, act (0 lobby, 1–3 investigation, 4 resolution), phase, paused, revision, guests, evidence, available_evidence, suspects, dialogue, performance, votes, solution and integrations. Evidence includes only revealed descriptions. available_evidence lists current-act unrevealed clue IDs/titles/acts; solution is null until act 4. Public snapshots contain no guest or organizer credentials. Votes are aggregate counts keyed by suspect ID.

Rooms are persisted to SQLite at `data/mystery.sqlite3` by default. Set `MYSTERY_DB_PATH` before starting the server to use another database file. The database is initialized and restored during application startup, not on module import. Keep the file private: saved room records include organizer and guest bearer credentials. Public snapshots exclude those credentials.

Every accepted mutation commits its complete durable room record before a joined confirmation or state broadcast. Storage failure returns an error to the sender and restores the previous in-memory state; failed room creation returns HTTP 503. Restart restores guests, reconnect credentials, act, pause state, released evidence IDs, votes, dialogue and revision. Static case definitions, sockets and asyncio locks are not stored. Reset clears progress and votes while preserving party identities and room credentials, and is also persisted.

The server still requires one process/worker. SQLite provides durable local storage, not shared live WebSocket fan-out across workers. Do not run multiple server workers against the same file. Use localhost or a trusted LAN; HTTPS, session expiration and deployment hardening remain on the task board. Back up the database only while the server is stopped. A corrupt database fails startup visibly rather than silently discarding saved progress. `/health` reports `storage: "sqlite"`.

Saved records pin `case_id` and `case_version` from the canonical case definition. Startup validates the persisted fields, guest credentials, clue IDs and vote references. Unknown record fields, invalid values, or an incompatible case version fail startup with a recovery message and preserve the file. Restore the matching case definitions or choose a different `MYSTERY_DB_PATH` explicitly; the server never silently rewrites an incompatible save.
