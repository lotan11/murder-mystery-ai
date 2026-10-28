# Validation results

## M3 local integration — October 27, 2026

| Check | Result |
| --- | --- |
| Backend | 134 passed, including 52 mocked Responses adapter cases and 25 async orchestration cases |
| Client | 15 passed, including actual-source/busy/usage metadata and safe diagnostic copy |
| TypeScript + build | Passed |
| Browser | 4 passed: private characters, scripted-default status, renderer recovery and complete synchronized case |
| Windows launcher/upgrade | Passed with explicit environment file; prior public state and host access preserved, schema 3 restored, paid AI disabled, frontend HTTP 200 |
| Remote CI | Passed on source `2485145`: [GitHub run](https://github.com/lotan11/murder-mystery-ai/actions/runs/40607478899) |
| Actual live model | Not invoked or verified; no paid requests made |

Tests cover strict request/output shape, data minimization, invented/unreleased facts, duplicate keys, malformed/refused/incomplete output, provider failure/timeout, durable reservation, reset/restart, budget exhaustion, storage failure, responsive same-socket pause, stale-result discard, concurrency and shutdown cancellation. Backend tests deny real outbound HTTP; browser-server settings force paid mode off. Live account/model compatibility, billing, actual speech and human playtesting are not inferred from mocks.

## M2 local integration — October 27, 2026

| Check | Result |
| --- | --- |
| Backend | 57 passed: includes private delivery, spoofing/access checks, character design, migration/recovery, rollback and unchanged case grounding |
| Client | 12 passed: includes separate private decoder, malformed private payloads and final-only public rationale validation |
| TypeScript + production build | Passed |
| Browser | 3 passed: four independent guests with reassignment/introductions/private reasons, full original case and renderer failure recovery |
| Windows upgrade | Passed on real existing schema-1 saves: atomic migration to schema 2, progress/party/credentials preserved and frontend HTTP 200 |
| Remote CI | Passed on source `091aa6b`: [GitHub run](https://github.com/lotan11/murder-mystery-ai/actions/runs/40604506205) |

The four-guest browser scenario inspects actual received WebSocket packets, checks that only the authenticated owner receives their private data, confirms host/TV receive none, and exercises concealed briefs, host reassignment, public introductions, reconnect and finale disclosure. Four phone-sized viewports have no horizontal overflow. Store tests validate additive migration and failure preservation. No paid AI/audio service was invoked.

Human dinner playtesting, real phone/TV readability and actor comfort remain unverified. Automated character roleplay does not count as a human rehearsal. Introductions are intentionally public after submission; accusation reasons become public only at resolution.

## M1 local integration — October 27, 2026

| Check | Result |
| --- | --- |
| Backend | 37 passed: engine, identity/access separation, malformed input, store recovery/failures/corruption/version pins, story grounding and bounded dialogue |
| Client | 9 passed: transport, error handling, snapshot validation and available-clue metadata |
| TypeScript + Vite build | Passed |
| Browser | 2 passed: full host/TV/phone case and WebGL context-loss fallback; includes real host gating, restored guest identity and no hidden guest canvas |
| Windows process restart | Passed: saved act, evidence and pause checkpoint matched after restarting `start.ps1`; host credential authorized resume; React HTTP 200 |
| Remote CI | Passed on source commit `e27ab9a`: [GitHub run](https://github.com/lotan11/murder-mystery-ai/actions/runs/40600489863); historical timeouts resolved |

Browser checks use real HTTP/WebSockets and isolated SQLite files, serial scenarios, retained failure traces and a bounded 90-second full-case allowance. They assert real host gating and that no avatar canvas is mounted on the guest view. No paid provider, microphone or speech service is used in automated tests.

A first manual restart comparison during integration observed the newly added public clue `summary` field because the story stream was still editing canon. After all component edits were frozen, the exact public snapshot comparison across a real server restart passed. No game progress or credentials were lost.

Known non-failing tooling messages: Vite reports the combined Three.js/React bundle size, and Starlette warns about its HTTPX test helper. Actual devices, physical TV readability, human dinner pacing, external AI, real audio capture and lip sync remain unverified.

## Historical M0 verification

Verified October 27, 2026 on Windows with Python 3.13 and Node 20.10 (setup recommends a maintained newer Node release).

| Check | Result |
| --- | --- |
| Windows launcher | `start.ps1 -SkipSetup -Port 8002` started successfully; health and built React page returned HTTP 200 |
| Backend pytest | 4 passed: full case gates/reset/spoiler protection; role permissions and restored guest identity; multiclient pause/votes/reconnect; malformed input recovery |
| Frontend client tests | 4 passed: secure URL credential encoding, malformed message recovery, server errors, unknown event handling |
| TypeScript and production build | Passed |
| Playwright full-case browser flow | Passed after final layout changes; organizer, 1920×1080 TV, and 390×844 phone viewport in independent browser contexts |
| Browser runtime errors | None in the full-case test |
| Phone horizontal overflow | None in tested viewport |
| npm audit in frontend | 0 reported vulnerabilities at verification time |
| Visual inspection | TV and phone screenshots reviewed; TV fitted to viewport, phone controls prioritized |

The browser flow covers create → guest join → start → reveal → question → pause/resume → all three acts → guest reload/identity restore → accusation → final solution → TV reload. Tests use real local HTTP/WebSocket communication, not a mocked transport. Backend tests additionally check spoiler withholding and unauthorized control rejection.

Known non-failing tooling messages: Vite warns about the roughly 721 KB uncompressed combined Three.js/React bundle; Starlette emits an HTTPX test-helper deprecation warning. Neither prevented builds or tests.

Not verified: physical TV readability, actual phones over Wi-Fi, device speech quality, cross-browser compatibility, production hosting/load, external AI, audio capture, rigged animation or lip sync. Those integrations are absent or explicitly labeled in the UI.

Repository integration: tests were rerun from the cloned `murder-mystery-ai` repository with FastAPI 0.162.0 and Uvicorn 0.54.0 in its own virtual environment. Playwright starts an isolated backend on port 8001. A Windows socket-reset callback was printed during browser teardown after assertions passed; it did not affect the case flow. GitHub Actions is configured but its remote run is separate from local validation.

## Follow-up verification of the first runnable prototype

Inspected remote `main` at `92b5396` before changes. The requested FastAPI, React host/guest, WebSocket synchronization, procedural detective, tests, and Windows launcher were already present. Preserved that implementation and the earlier standalone local branch.

Fixed malformed credentials and binary WebSocket recovery, incomplete frontend snapshot/error validation, and WebGL context-loss fallback, with regression tests.

Fresh verification on October 27, 2026: 7 backend tests, 7 frontend client tests, production build, and the full organizer/TV/phone guest browser flow passed. Windows launcher started on port 8017 with health and built React returning HTTP 200. Port 8002 was occupied and correctly reported a conflict. Frontend npm audit reported zero known vulnerabilities. AI is scripted; browser speech remains opt-in. No paid provider was invoked.

The added browser regression for WebGL context loss also passed; captions and evidence remain available after renderer failure.

## TalkingHead audition — October 28, 2026

157 backend tests passed, one Windows symlink privilege skip; 15 client tests passed; production build passed; all six browser scenarios passed. Actual SAPI Windows playback reviewed separately from clearly labeled synthetic browser fixtures: real mesh motion and stop reset observed, no page errors or external requests. Existing full case and privacy flows remain green. Premium voice quality and final detective asset remain untested/unselected.
