# Validation results

## M1 local integration â€” October 27, 2026

| Check | Result |
| --- | --- |
| Backend | 37 passed: engine, identity/access separation, malformed input, store recovery/failures/corruption/version pins, story grounding and bounded dialogue |
| Client | 9 passed: transport, error handling, snapshot validation and available-clue metadata |
| TypeScript + Vite build | Passed |
| Browser | 2 passed: full host/TV/phone case and WebGL context-loss fallback; includes real host gating, restored guest identity and no hidden guest canvas |
| Windows process restart | Passed: saved act, evidence and pause checkpoint matched after restarting `start.ps1`; host credential authorized resume; React HTTP 200 |
| Remote CI | Pending milestone push; historical runs failed the whole-case 45-second budget |

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
| Playwright full-case browser flow | Passed after final layout changes; organizer, 1920Ã—1080 TV, and 390Ã—844 phone viewport in independent browser contexts |
| Browser runtime errors | None in the full-case test |
| Phone horizontal overflow | None in tested viewport |
| npm audit in frontend | 0 reported vulnerabilities at verification time |
| Visual inspection | TV and phone screenshots reviewed; TV fitted to viewport, phone controls prioritized |

The browser flow covers create â†’ guest join â†’ start â†’ reveal â†’ question â†’ pause/resume â†’ all three acts â†’ guest reload/identity restore â†’ accusation â†’ final solution â†’ TV reload. Tests use real local HTTP/WebSocket communication, not a mocked transport. Backend tests additionally check spoiler withholding and unauthorized control rejection.

Known non-failing tooling messages: Vite warns about the roughly 721 KB uncompressed combined Three.js/React bundle; Starlette emits an HTTPX test-helper deprecation warning. Neither prevented builds or tests.

Not verified: physical TV readability, actual phones over Wi-Fi, device speech quality, cross-browser compatibility, production hosting/load, external AI, audio capture, rigged animation or lip sync. Those integrations are absent or explicitly labeled in the UI.

Repository integration: tests were rerun from the cloned `murder-mystery-ai` repository with FastAPI 0.162.0 and Uvicorn 0.54.0 in its own virtual environment. Playwright starts an isolated backend on port 8001. A Windows socket-reset callback was printed during browser teardown after assertions passed; it did not affect the case flow. GitHub Actions is configured but its remote run is separate from local validation.

## Follow-up verification of the first runnable prototype

Inspected remote `main` at `92b5396` before changes. The requested FastAPI, React host/guest, WebSocket synchronization, procedural detective, tests, and Windows launcher were already present. Preserved that implementation and the earlier standalone local branch.

Fixed malformed credentials and binary WebSocket recovery, incomplete frontend snapshot/error validation, and WebGL context-loss fallback, with regression tests.

Fresh verification on October 27, 2026: 7 backend tests, 7 frontend client tests, production build, and the full organizer/TV/phone guest browser flow passed. Windows launcher started on port 8017 with health and built React returning HTTP 200. Port 8002 was occupied and correctly reported a conflict. Frontend npm audit reported zero known vulnerabilities. AI is scripted; browser speech remains opt-in. No paid provider was invoked.

The added browser regression for WebGL context loss also passed; captions and evidence remain available after renderer failure.
