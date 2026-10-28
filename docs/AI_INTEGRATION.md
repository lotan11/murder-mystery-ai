# Optional AI assistance

M3 is a bounded OpenAI Responses planner, not unrestricted model-written dialogue. Default rehearsal remains scripted and requires no API key. Live provider operation has not been tested with a real account in this milestone; automated tests use mock transports or fake async planners.

## What the model does

For an eligible question during acts 1–3, the model may select zero to two released clue IDs and one approved Wobblebottom remark ID. The server composes the answer from the selected clues' authored summaries/descriptions and approved remark. The model cannot submit prose, create facts, choose the culprit, unlock clues or mutate the game.

This boundary deliberately goes beyond checking whether arbitrary prose contains citations: valid JSON is not proof that a generated claim is true. The structured plan permits only known IDs and the factual text stays authoritative. The adapter uses [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses), then independently validates the returned object.

Private role cards, objectives, roster, introductions, accusation reasons, credentials, hidden clues and the unrevealed solution are excluded from provider context. Requests contain the typed question and released evidence only. A guest may deliberately type private information into their question, so the UI discloses provider use before submission when available.

## Configure locally only when ready to use paid AI

No setup is required for scripted mode. For optional live assistance:

1. Copy `.env.example` to `.env` locally. The real file is ignored by Git.
2. Choose a model available to your account that supports the Responses API and strict structured outputs. There is no default paid model.
3. Set these values in `.env`:

```dotenv
MYSTERY_DIALOGUE_PROVIDER=openai
MYSTERY_ALLOW_PAID_AI=true
OPENAI_API_KEY=YOUR_LOCAL_KEY
MYSTERY_OPENAI_MODEL=YOUR_STRUCTURED_OUTPUT_MODEL
MYSTERY_AI_MAX_CALLS=5
MYSTERY_AI_TIMEOUT=4
```

The capitalized key/model values above are placeholders. Keep real credentials on the server; the app does not collect keys in a browser form. Start from the repository root on Windows:

```powershell
powershell -ExecutionPolicy Bypass -File .\start.ps1 -SkipSetup -EnvFile .\.env
```

Run without `-SkipSetup` for first setup or after code/dependency changes. Add `-Lan` for your trusted local network and `-Port 8018` if desired. The file is read only when `-EnvFile` is passed; inherited process environment takes precedence. Restart after configuration changes. Missing/invalid settings keep the scripted detective available with a visible configuration reason.

To return to scripted mode, set the provider to `scripted` or paid consent to `false`, then restart. Earlier model-assisted replies retain their actual source label; new scripted replies are labeled separately.

## Request limits and failure behavior

- `MYSTERY_AI_MAX_CALLS`: default 5 attempted requests per room, valid range 1–50.
- `MYSTERY_AI_TIMEOUT`: default 4 seconds, valid range 1–10.
- At most one external request is in flight per room. Attempts commit to SQLite before dispatch and survive reset/restart. Reset does not replenish the allowance.
- Failures count toward the allowance because a request may already have reached the provider. There are no automatic retries. This is a request-count control, not a dollar spending guarantee across models or newly created rooms.
- Requests use the fixed OpenAI HTTPS endpoint, `store:false`, no tools, and at most 512 output tokens. The chosen model must complete its structured response within that cap; incomplete output falls back.
- Hints, recaps, requests for the culprit, lobby/no-evidence questions and the final reconstruction stay scripted and do not consume requests.
- Host pause/reset/clue controls remain responsive while the provider is awaited. If the room changes, the old answer is discarded. Network/provider/refusal/validation errors use a safe scripted fallback without displaying raw provider diagnostics.
- A failed database reservation sends no provider request. If saving a completed answer fails, it is not applied; the reserved attempt remains recorded.

## How to verify

Automated coverage includes request shape/data minimization, strict output validation, invented/unknown clue rejection, malformed/refused/incomplete responses, timeouts, fallback, request limits, reset/restart, concurrency, same-socket host pause, late-result discard and schema migration. Tests forbid real outbound HTTP and force scripted defaults regardless of a developer's shell settings. Browser tests also force paid AI off.

For a deliberate live smoke test after configuring an account/model, begin a room, reveal a clue and ask a specific question such as “Explain the untouched port.” The host integration panel should show an attempted request and the actual reply source: AI-assisted or scripted fallback. Verify that the rendered facts come from released clues and that pausing remains responsive. That live smoke test is not claimed complete here.

Microphone capture, custom TTS and speech-driven lip sync are separate M4 integrations. Browser speech remains opt-in device synthesis.
