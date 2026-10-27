# Murder Mystery AI — Wobblebottom prototype

A runnable dinner-party mystery with a React host desk, guest notebooks, a Three.js TV detective, and an authoritative FastAPI engine. No API keys or paid services are required.

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
2. Each guest enters a name. The host selects **Begin case**, then **Reveal next clue**.
3. Guests review released evidence and send typed observations to Detective Reginald P. Wobblebottom.
4. Reveal all clues before selecting **Next act**. Pause and resume as needed.
5. Accusations open in act three. Guests can change their votes until the host resolves the case.
6. Reveal the final clue and select **Resolve the case**. Reload any screen to restore its current room snapshot.

The deterministic case has three suspects, five clues, three acts, and one fixed solution. The server controls clue gates and withholds unrevealed descriptions and the solution. Rooms and tokens are kept in memory: restarting the server clears them. The host credential is saved in that browser; keep it private. Guest reconnect tokens preserve identity without duplicating players.

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
| AI dialogue | Scripted provider; no external model calls. `backend/dialogue.py` defines the replacement interface |
| Microphone | Not connected. Typed text simulates a transcript; no recording or upload |
| Speech | Opt-in browser speech synthesis; device-dependent voice, no custom TTS service |
| Detective | Lightweight procedural Three.js avatar with idle movement and a CSS fallback |
| Lip sync | Not connected; idle motion is not speech-driven animation |
| Evidence | 3D stage combined with readable HTML evidence and guest notebooks |

External AI may phrase released facts but must never choose the solution or advance the game. Speech remains optional and captions work without it. The app works without external fonts using local fallback fonts.

## Scope and documentation

This is a trusted-local-network prototype for one server process, with up to 24 guest identities per room. It has no durable storage, accounts, room expiry, deployment hardening or multi-worker synchronization. Do not expose it as a public service without adding those capabilities.

- [API contract](backend/API.md)
- [Architecture and integration seams](docs/ARCHITECTURE.md)
- [Three-week task board](docs/TASK_BOARD.md)
- [Repository/source inspection](docs/ARCHIVE_REVIEW.md)
- [Validation results](docs/VALIDATION.md)
