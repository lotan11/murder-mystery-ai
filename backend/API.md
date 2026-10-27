# Local API contract

`POST /api/rooms` (no body) creates a room and returns `room_id` and a secret `organizer_token`. `GET /api/rooms/{room_id}/state` returns its public snapshot. Room IDs are case insensitive.

Connect to `/ws/{room_id}?role=tv`, `?role=guest`, or `?role=organizer&token=SECRET`. Invalid rooms or organizer credentials close with code 1008. Each connection receives `{type:"state",data:SNAPSHOT}` immediately. Every successful command increments `revision` and broadcasts a complete snapshot to all connected screens. Reconnect receives current authoritative state; the frontend should replace its state rather than merge event fragments.

Commands:

- Guest `{type:"join",name:"Jamie"}` returns `{type:"joined",guest_id,guest_token}` privately, followed by the public state and this guest's private character packet. Save that token and reconnect with `role=guest&guest_token=...`; this receives state, joined confirmation, then the guest-private packet. A reconnect does not duplicate a guest.
- Organizer `{type:"control",action:"start"|"pause"|"resume"|"reset"|"advance"|"reveal"}`. Reveal accepts an optional `evidence_id`; without it the next current-act clue is revealed. Start opens act 1. Advance requires every clue in the current act. Advance from act 3 resolves act 4. Reset clears progress, introductions, votes and rationales while preserving the party, character assignments and credentials.
- Joined guest or organizer `{type:"dialogue",text:"What about the tea?"}`. This invokes a deterministic mock provider constrained to revealed facts; no external AI request is made.
- Organizer `{type:"control",action:"assign",guest_id:"...",character_id:"ada"|"felix"|"margot"|"investigator"}` changes a joined guest's character only in the unpaused lobby. Named characters are exclusive: move an occupant to investigator before reusing their character. An assignment change clears that guest's submitted introduction.
- Joined guest `{type:"introduce",text:"A public greeting"}` in the unpaused lobby or act one, 1–240 trimmed characters. This deliberately publishes the guest's text; the app never copies a private brief into it automatically. A later submission replaces the same guest's introduction. Introductions are optional and never block progression.
- Joined guest `{type:"accuse",suspect:"ada"|"felix"|"margot",rationale:"My reasoning"}` in act 3. Rationale is optional, at most 300 characters. One vote per guest; a new vote replaces the previous vote and rationale. Aggregate counts are public; individual rationale is private until act four. All guest identity comes from the authenticated connection; supplying a `guest_id` command field is rejected.

Invalid commands return `{type:"error",message:"..."}` only to the sender. A paused room blocks dialogue, voting, introductions, character reassignment and act progression; joining, reset and resume still work.

Snapshots include room_id, title, act (0 lobby, 1–3 investigation, 4 resolution), phase, paused, revision, guests, evidence, available_evidence, suspects, dialogue, performance, votes, solution and integrations. Evidence includes only revealed descriptions. available_evidence lists current-act unrevealed clue IDs/titles/acts; solution is null until act 4. Public snapshots contain no guest or organizer credentials. Votes are aggregate counts keyed by suspect ID. Public guests additionally include `character_id`, `character_name` and `introduced`. `introductions` contains voluntarily submitted `{guest_id,name,character_name,text}` entries. `accusations` is an empty list before act four, then contains `{guest_id,name,suspect,rationale}` for the final discussion. No public snapshot includes character briefs, private objectives or performance notes.

## Guest-private delivery

After join/reconnect and each accepted mutation, each authenticated guest socket receives only its own packet:

```json
{"type":"private","data":{"guest_id":"...","character":{"id":"ada","name":"Ada Blackthorn","public_intro":"...","private_brief":"...","objectives":["..."],"performance_notes":"..."},"introduction_submitted":false,"own_vote":null}}
```

Once that guest has voted, `own_vote` is `{suspect,rationale}`. State broadcasts remain public, followed by a separate identity-specific private packet for each guest socket. Host and TV sockets never receive private packets, even when a guest token is appended to their URL. Unknown guest tokens cannot recover an identity; public guest IDs confer no private access. There is no HTTP endpoint for reading a card by guest ID. The first three new identities receive Ada, Felix and Margot; additional identities receive the non-exclusive investigator role. Reconnect and reset preserve assignments. Private character definitions live in `backend/characters.py`, separate from released mystery facts. The dialogue provider receives only the public snapshot, never private cards.

Rooms are persisted to SQLite at `data/mystery.sqlite3` by default. Set `MYSTERY_DB_PATH` before starting the server to use another database file. The database is initialized and restored during application startup, not on module import. Keep the file private: saved room records include organizer and guest bearer credentials. Public snapshots exclude those credentials.

Every accepted mutation commits its complete durable room record before a joined confirmation or state broadcast. Storage failure returns an error to the sender and restores the previous in-memory state; failed room creation returns HTTP 503. Restart restores guests, reconnect credentials, act, pause state, released evidence IDs, votes, dialogue, revision, character assignments, introductions and private rationales. Static case definitions, sockets and asyncio locks are not stored. Reset clears progress, introductions, votes and rationales while preserving party identities, assignments and room credentials, and is also persisted.

The server still requires one process/worker. SQLite provides durable local storage, not shared live WebSocket fan-out across workers. Do not run multiple server workers against the same file. Use localhost or a trusted LAN; HTTPS, session expiration and deployment hardening remain on the task board. Back up the database only while the server is stopped. A corrupt database fails startup visibly rather than silently discarding saved progress. `/health` reports `storage: "sqlite"`.

Saved records pin `case_id` and `case_version` from the canonical case definition. Startup validates the persisted fields, guest credentials, clue IDs and vote references. Unknown record fields, invalid values, or an incompatible case version fail startup with a recovery message and preserve the file. Restore the matching case definitions or choose a different `MYSTERY_DB_PATH` explicitly; the server never silently rewrites an incompatible save.


## Compatible save migration

M2 uses room-record schema 2 while retaining canonical case version 1. A validated M1 schema-1 save is upgraded additively: existing guests receive deterministic roles in saved join order, introductions start empty and prior votes receive empty rationales. Progress, pause state, revision and all credentials stay unchanged. Startup validates every record before atomically saving all legacy upgrades in one SQLite transaction; invalid or unsupported records leave the database untouched. Fresh schema-2 saves validate unique named-role assignments, guest references, introduction limits and rationale/vote consistency. Back up the database while the server is stopped before upgrades; never delete an old save to make a migration appear to pass.
