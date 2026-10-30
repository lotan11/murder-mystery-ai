# Listener integration review

Reviewed October 29, 2026 (America/Denver), against `origin/feature/listener` commit `1f8bab0bcf7092b360b213b8796af778d94654d7`. Main remains authoritative. **Disposition: do not merge or enable live microphone transcription yet.** This is a code review with offline reproductions, not a live paid-provider or human microphone acceptance test.

## What is sound enough to reuse after repair

Explicit guest opt-in, a separate paid-transcription enable flag, authenticated guest socket identity, released-evidence input, injected transcription transport, persisted usage reservation before provider invocation, generic provider errors and no raw-audio disk writes are useful foundations. The default remains disabled without both flags and a key. The deterministic listener does not decide guilt. These properties do not establish safe cancellation or correct claim interpretation.

The isolated branch's existing backend suite passes: **252 tests, two Windows permission skips**, including its five listener tests. An additional schema-3-to-4 round-trip probe passes with guest/assignment/game fields preserved. This sample is not an exhaustive migration/rollback certification. Main cannot read schema4: retain a database backup and define rollback before adopting it.

## Findings requiring repair before integration

References below are to the pinned listener revision, not current main line numbers.

| Priority | Finding and evidence | Required acceptance |
| --- | --- | --- |
| P1 | `backend/main.py:540–546` awaits transcription inside the socket receive loop. Stop/Mute commands cannot update the local flags during that await. Injected delayed-provider tests show a transcript published after Stop, and old audio published into fresh memory after host Reset (`:322`). The post-await boolean check does not invalidate work across a reset or pause/resume cycle. | Keep receiving control messages during bounded transcription; session/game-generation invalidation plus cancellation and commit-time checks. Reject delayed work after Stop, pause/resume, reset, disconnect and reconnect. No queued stale chunks may restart processing. |
| P1 | `frontend/src/App.tsx:250–267` has no cancellation check after pending `getUserMedia`. Original function reproduction: Stop, then resolve permission, starts recording with `listening=false` and zero stopped tracks. | Session-guard the permission promise, stop a late stream immediately, handle component/room/socket changes, and test pause/Stop/disconnect while permission is pending. |
| P1 | `App.tsx:975` calls `stopListener(!muted)` for Resume. A muted session invokes `stopListener(false)`, sends `listener.stop` and never resumes capture. | Explicit resume transition with renewed consent where required, fresh guarded capture and server acknowledgement; meaningful browser test. |
| P1 | `App.tsx:258–267` sends each `MediaRecorder.start(3000)` fragment as a standalone transcription file. Actual Chromium fake-device capture: the first 40,532-byte WebM chunk independently decodes to3s; the second49,298-byte fragment lacks the initialization header and independently fails with `EncodingError`. No real provider was used, so provider-specific rejection is not claimed. | Use independently finalized, decodable clips or a deliberately supported streaming protocol; verify second/subsequent clips before testing a paid endpoint. |
| P1 | Standard `start.ps1:36` and README use a16,384-byte WebSocket message limit. Both observed3s fake-device chunks exceed it, although the branch advertises512KiB audio frames. The transport rejects oversized frames before the app's512KiB validation can accept them. | Align the actual transport with a separately bounded audio-upload design, retaining small text-command limits. Test using a real local server/transport, not only TestClient. |
| P1 | Listener acceptance increments `room.revision` (`backend/main.py:589`), while `App.tsx:158–162` and `ScholarPerformance.tsx:240–252` stop narration on revisions. Dialogue text remains unchanged, so the already-spoken guard prevents automatic restart. | Separate narration identity from unrelated listener-state updates, preserving existing stale-speech/pause/reset guards; test a listener observation during real Lewis playback. |
| P1 | Listener errors/status are not handled in `App.tsx:121–190` / `client.ts:177`. Provider errors are discarded while UI can continue saying microphone live. | Show accurate server/capture status, stop or explicitly back off on errors, bound queued work, and test provider failure/allowance exhaustion. |
| P1 | `_claims` (`backend/listener.py:140–172`) cross-products all subjects/places against the first time in the utterance. The sentence “Ada was in the library at9:20; Felix was in the music room at9:40” produces four claims, including invented Ada/music-room and Felix/library accounts, all at9:20. Negation is also not understood. `_released_alibi(:175)` ignores its time argument. | Restrict extraction to unambiguous, scoped affirmative clauses or require structured/confirmed claims. Abstain on ambiguous/negative/reported statements. Never imply a released clue supports an unrelated time. Add adversarial multi-clause tests. |
| P2 | Theory support/challenge references append without retention bounds (`listener.py:239–240`). After200 observations, transcript retention is120 but theory links remain200 and continue growing; snapshots/storage/restore validation do not cap these lists. | Prune references with retained utterances, cap all persisted collections and validate shape/size on reload. |
| P2 | Audio duration and usage estimates trust the client's constant `duration_seconds:3` (`App.tsx:262`; server`:523`). Browser timeslice delays and arbitrary uploads are not guaranteed to match that duration. A call-count cap exists, but this is not an accurate audio-time or monetary cap. | Validate independent clip duration/format, reject mismatches, account conservatively and disclose estimates. No live spend until separately authorized/configured. |

## Reproducible offline evidence

`docs/reviews/listener-1f8bab0-evidence.json` records the original-function VM and actual Chromium fake-device observations. No audio recordings, real microphone samples, keys or participant data are committed.

The repaired backend regression probes are `scripts/review-listener-cases.py`. They are deliberately outside normal main test discovery because main has no listener module. From the `feature/listener` working tree, run them explicitly; the fixture uses a temporary SQLite database:

From the authoritative repository in PowerShell:

```powershell
& ".venv/Scripts/python.exe" -m pytest scripts/review-listener-cases.py -q
```

Existing frontend dependencies/Playwright and the local8018 app are prerequisites for the independent frontend probe:

```powershell
node scripts/review-listener-frontend.mjs
```

It extracts the pinned original functions into a mocked VM, then uses Chromium's **synthetic** microphone to examine media fragments. It never enables the listener in the working game or calls a transcription provider. Output goes to ignored `data/listener-review-frontend/evidence.json`. Clip sizes/timing can vary by run. This script preserves the review reproduction for the original implementation; the repaired behavior is exercised by `frontend/e2e/listener-media.spec.ts`.

## Integration order

1. Repair cancellation/generation boundaries, permission lifecycle, resume/error states and independent audio framing/transport, with offline tests.
2. Correct claim extraction/retention and validated usage accounting; preserve authored case facts and public/private boundaries.
3. Integrate narration without listener-induced Lewis interruption, and add host/guest/TV browser scenarios.
4. Validate schema migration/backups, full main regression and CI; keep default microphone off.
5. Human/device and authorized live-provider acceptance remain separate gates. No purchase, paid provider call or public deployment occurred in this review.

## Repair status on `feature/listener`

This section records the implementation after the pinned review. It supersedes the original disposition for code defects, while preserving the review evidence and its live-provider limits.

| Finding | Repair and regression evidence |
| --- | --- |
| Stale work after controls or connection changes | Bounded worker queue, per-session and room generations, cancellation, commit-time checks, queue draining; tests cover Stop, Reset, pause/resume, and disconnect/reconnect. |
| Late microphone permission and Resume lifecycle | Permission promise is session-guarded and late streams release tracks; explicit resumed capture requests consent and cleans up on stop/error; client lifecycle tests cover late permission and finalized data after Stop. |
| Fragmented containers / message-size mismatch | New finalized recorder per clip, exact declared MIME, Uvicorn/Playwright cap 614400 bytes with app cap 512 KiB; fake-Chromium decodes consecutive clips and the real Uvicorn scenario validates a >16 KiB clip. |
| Unsupported contradiction claims and evidence | Claim parsing abstains on negation, hearsay, uncertainty and ambiguous clauses; evidence must match the canonical released clue and authored time/location scope. Adversarial claim and clue tests pass. |
| Lewis narration interrupted by listener updates | Listener changes do not increment narration revision. A browser test submits a table observation while Lewis is actually playing and checks playback advances without another audio start. Device echo cancellation is requested; headphones/TV mute remain useful for room acoustics. |
| Missing status and provider errors | Client handles listener status/errors, stops capture on terminal errors, and preserves only backpressure as recoverable. Provider failure and allowance exhaustion are covered offline. |
| Unbounded theory links | Theory references are pruned to retained utterances and restored memory validation bounds/validates collections. Retention probes pass. |
| Client-trusted duration accounting | EBML/WebM, Ogg Opus and MP4 duration is parsed server-side; invalid type/duration and header mismatch are rejected before provider call; cost allowance uses verified duration. |

The main Work follow-up review found three additional integration defects: a room Reset in the lobby did not stop the guest's microphone, Resume could leave an obsolete transcript prompt visible, and server stop acknowledgements replaced the actionable capture/provider error. These are fixed with a guest-only `listener.reset` event, confirmation clearing on new consented sessions, and retained terminal status. The same review caught the `guest_id: null` state-decoder mismatch; it is fixed and malformed unknown-speaker records remain rejected. MediaRecorder's timer can drift around one second from container duration; the header mismatch tolerance accounts for that scheduling jitter while usage remains based only on parsed container duration.

Local verification after these repairs: 365 backend passed/3 skipped, 5 main-review probes passed, 25 client passed, build passed and all24 browser scenarios passed. No paid transcription was called. A physical microphone test has not occurred. The branch remains unmerged until remote CI and main-team combined integration checks pass; any device-specific or live-provider acceptance should use explicitly configured credentials and a deliberate test session.

This review does not change the November4 custom-avatar gate or November10 integration deadline. Scholar visual work remains the critical path; listener integration must not destabilize the playable portrait/Lewis baseline.
