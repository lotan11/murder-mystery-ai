# Three-week part-time task board

Planning assumption: 10–12 hours/week, 30–36 hours total. The current repository establishes the vertical slice; the remaining time is for integration choices, polish, and real dinner-table testing. A production avatar, microphone pipeline, and custom voice together exceed this budget unless scope is reduced.

| Status | Workstream | Deliverable / acceptance |
| --- | --- | --- |
| Done | Repository | Initial GitHub application, Windows launcher, self-starting browser test and CI workflow |
| Done | Foundation | Inspect original ZIP, preserve source, document reuse decision |
| Done | Engine | One authored case, three gated acts, fixed culprit, spoiler-safe public state |
| Done | Synchronization | Real room creation, organizer permissions, guests, snapshots and reconnect |
| Done | TV | React/Three.js procedural detective, manor lighting, readable evidence and captions |
| Done | Guests | Join, text questions, evidence review, act-three accusations |
| Done | Organizer | Begin, reveal, advance, pause/resume, reset and share links |
| Done | Dialogue seam | Deterministic sarcastic Wobblebottom provider; external AI explicitly absent |
| Done | Handoff | Setup, architecture, limitations, automated tests and browser smoke flow |
| Next | Week 1 / 4h | Play the case with two readers; fix logical ambiguities and clue pacing |
| Next | Week 1 / 3h | Verify TV readability at 3 metres and two actual phones over Wi-Fi |
| Next | Week 1 / 3h | Record an end-to-end rehearsal and log friction; establish a 15-minute demo script |
| Planned | Week 2 / 4h | Add durable room storage and restore after process restart |
| Planned | Week 2 / 4h | Choose one real integration: grounded AI dialogue OR licensed rigged avatar; keep deterministic fallback |
| Planned | Week 2 / 2h | Add integration timeout/error tests and spoiler/adversarial dialogue checks |
| Planned | Week 3 / 4h | Run a 4–6 guest dinner rehearsal; capture pacing and comprehension feedback |
| Planned | Week 3 / 4h | Fix observed issues, improve transitions and evidence art within existing layout |
| Planned | Week 3 / 2h | Package stable build, rehearse recovery and document demo operation |
| Backlog | Audio | Consent, real microphone capture, echo handling, transcription and interruption |
| Backlog | Character | Licensed polished model, rigged gestures, custom TTS and real viseme lip sync |
| Backlog | Hosting | Accounts, HTTPS, rate limits, room expiry, shared store and deployment |

Parallel ownership: engine work can proceed alongside visual/character work and phone UX. Integrate against the WebSocket snapshot contract before introducing an external AI or audio provider. The release gate is a complete case across TV + organizer + two guest devices, including pause and reconnection, with no hidden solution exposed early.

Automated verification and its results are recorded in `VALIDATION.md`. Actual phone, television and dinner-party checks remain manual work; they are not claimed complete.
