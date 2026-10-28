# Murder Mystery AI — Wobblebottom prototype

The Last Toast at Blackthorn Manor: a runnable dinner-party mystery with a React host desk, guest notebooks, a Three.js TV detective, and an authoritative FastAPI engine. No API keys or paid services are required.

## Windows quick start

Install Python 3.11+ and Node.js 20.19+ (or Node 22), with both available on PATH. In PowerShell:

```powershell
git clone https://github.com/lotan11/murder-mystery-ai.git
cd murder-mystery-ai
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

The script creates `.venv`, installs dependencies, builds the frontend, and starts the app. Open http://localhost:8000 and select **Create an evening**. Stop with Ctrl+C. For subsequent runs, use `powershell -ExecutionPolicy Bypass -File .\start.ps1 -SkipSetup`. Run without `-SkipSetup` after pulling source or dependency changes.

For phones on the same Wi-Fi, use `powershell -ExecutionPolicy Bypass -File .\start.ps1 -Lan`. Open `http://YOUR_COMPUTER_LAN_IP:8000` on the host computer before sharing guest links; `ipconfig` shows your active adapter's IPv4 address. Allow Python through Windows Firewall on your private network if prompted. `localhost` links only work on the computer running the server. Use `-Port 8080` if port 8000 is occupied.

## Play a complete case

1. Create a room in the organizer (host) view. Open **TV stage** on a second screen and share **Guest notebook** with players.
2. Each guest enters a name and receives a character card. The first three guests receive the three suspect roles; additional guests investigate. The host may change assignments in the lobby. Guests choose **Reveal private brief** on their own devices and may submit a public introduction. Then the host selects **Begin case** and **Reveal next clue**.
3. Guests review released evidence and send typed observations to Detective Reginald P. Wobblebottom.
4. Reveal all clues before selecting **Next act**. Pause and resume as needed.
5. Accusations open in act three. Guests may add a reason and change their votes until resolution. Reasons remain private to each guest until the finale, when the table can compare deductions.
6. Reveal the final clue and select **Resolve the case**. Reload any screen to restore its current room snapshot.

The deterministic case has three suspects, five clues, three acts, and one fixed solution. Character briefs provide dramatic objectives: the culprit player receives actor knowledge, while investigators solve from released clues. No one must lie or invent evidence. Start a fresh room for the first character rehearsal. The server controls clue gates and withholds unrevealed descriptions and the solution. Rooms, progress and credentials are saved in SQLite: restarting restores committed games. Keep the same browser and room links to recover guest and host access. The host credential is saved in that browser; keep it private. Guest reconnect tokens preserve identity, role and submitted introduction without duplicating players. Private briefs arrive only on the authenticated guest socket, stay out of public snapshots and are not saved in browser storage. Existing schema-1/2 SQLite saves upgrade atomically to schema 3 without deleting progress or credentials. AI request counts, when used, survive restart and reset.

For multiple test guests on one computer, use different browser profiles or different browsers. Normal tabs share a guest identity; real guests should use their own phones. To swap two occupied roles, temporarily assign one player to investigator first.

## Manual setup / development

From the repository root on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd frontend
npm.cmd ci
npm.cmd run build
cd ..
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --ws-max-size 16384 --no-access-log --log-level warning
```

For frontend development, keep the backend running on port 8000 and run `npm.cmd run dev` in `frontend` from another terminal. Vite proxies API and WebSocket requests. On macOS/Linux use `python3`, `.venv/bin/python`, and `npm` instead of the Windows commands above.

## Tests

```powershell
# From the repository root
.\.venv\Scripts\python.exe -m pytest backend/tests -q
cd frontend
npm.cmd test
npm.cmd run build
npx.cmd playwright install chromium
npm.cmd run test:e2e
```

The browser test starts its own backend on port **8001**, so leave that port free. It drives independent host, TV and phone-sized guest contexts through a complete case, checks pause and reconnect, and saves screenshots in `frontend/test-results`. Build first so the test backend can serve React. GitHub Actions runs backend, frontend, build and browser checks on every push/PR.

## Optional integrations

| Feature | Current implementation |
| --- | --- |
| Multiplayer | Real WebSockets, server snapshots, host permissions and guest identity |
| Mystery | Real deterministic engine and authored case |
| AI dialogue | Scripted by default. Optional OpenAI planning selects released facts and approved remarks; explicit local paid configuration required. See the AI guide |
| Microphone | Not connected. Typed text simulates a transcript; no recording or upload |
| Speech | Opt-in browser speech synthesis; device-dependent voice, no custom TTS service |
| Detective | Lightweight procedural Three.js avatar with idle movement and a CSS fallback |
| Lip sync | Not connected; idle motion is not speech-driven animation |
| Evidence | 3D stage combined with readable HTML evidence and guest notebooks |

The optional AI planner selects released clue IDs and an approved remark; the server supplies authored factual text. It does not generate arbitrary prose or advance the game. Speech remains optional and captions work without it. The app works without external fonts using local fallback fonts.

## Scope and documentation

This is a trusted-local-network prototype for one server process, with up to 24 guest identities per room. SQLite saves rooms in `data/mystery.sqlite3`; set `MYSTERY_DB_PATH` to choose another file. The database contains access credentials: keep it local and out of Git. There are no accounts, room expiry, deployment hardening or multi-worker synchronization. Do not expose it as a public service without adding those capabilities.

- [Optional AI configuration and limitations](docs/AI_INTEGRATION.md)
- [Project specification](docs/SPECIFICATION.md)
- [Latest progress and handoff](docs/PROGRESS.md)
- [Architectural decisions](docs/DECISIONS.md)
- [Game design — spoilers](docs/GAME_DESIGN.md)
- [Playable rehearsal guide](docs/TEST_PLAYBOOK.md)
- [API contract](backend/API.md)
- [Architecture and integration seams](docs/ARCHITECTURE.md)
- [Three-week task board](docs/TASK_BOARD.md)
- [Repository/source inspection](docs/ARCHIVE_REVIEW.md)
- [Validation results](docs/VALIDATION.md)

Project coordination lives in `AGENTS.md` and the linked documents. Each milestone integrates into this application and records acceptance evidence; the user does not need to transfer plans or story details between conversations.

## TalkingHead audition

Try the optional local voice and animated-face comparison at `/?view=audition`. Follow [Windows preparation and integration limits](docs/VOICE_AUDITION.md). The sample avatar and installed voices are placeholders; no paid service is used.
