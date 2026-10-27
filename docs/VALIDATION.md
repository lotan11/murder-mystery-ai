# Validation results

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
