# PR2 combined integration review

Reviewed October29,2026 (America/Denver). PR: https://github.com/lotan11/murder-mystery-ai/pull/2. Runtime snapshot tested: `7b2b918ff331b63e9b40d8e18fcf5a14e3f224e9`. PR advanced to `91b08e3e815ec3e3fe39ab183a57e0705ed1e568` during review; that delta adds backend/client test assertions only, with no runtime changes. Findings below apply to both. No merge, provider call, real microphone use or live saved-room migration.

## Findings

1. **P1: unattributed audio invalidates public snapshots.** `frontend/src/client.ts:111–112` requires a string `guest_id`, while the new confirmation path deliberately persists null for unknown speaker. A complete empty-listener snapshot decodes successfully; adding one legitimate null-attribution utterance yields `An incomplete room update arrived. Reconnect to recover.` Every client rejects subsequent snapshots while that item remains. PR author acknowledged this and is preparing a fix; no fixed revision was tested at this checkpoint. Require nullable type/validator and host/guest/TV regression through confirmation, later state changes and reload.
2. **P1: lobby Reset does not stop local capture.** `frontend/src/App.tsx:198–203` stops listener only on nonzero act to zero. Listener is available in lobby; resetting at act0 invalidates server session while leaving local capture/pending-permission generation alive. Later generic error events do not stop capture. Require an explicit listener/game-generation reset signal or equivalent reliable boundary, including same-act reset tests and pending permission/capture cleanup.
3. **P2: Resume keeps stale source confirmation.** `App.tsx:277–285,322–323` resumes without clearing local confirmation, while backend start/resume clears its pending confirmation. The old form remains and Confirm cannot succeed. Require a coherent discard/resume lifecycle and regression.
4. **P2: useful error text is overwritten.** Listener-error handler sets a provider/allowance reason, then `stopListener(false)` replaces it with generic stopped text. Capture stops, but the user loses the actionable reason. Preserve that reason after cleanup.

## Validation scope

- Isolated snapshot includes current main as ancestor; original cases, approved portraits, voice files and custom-avatar assets have no diff.
- Backend plus explicit review probes: **367pass/3Windows skips** (362normal backend +5review probes).
- Client: **24pass**; production build passes.
- All browser scenarios running at checkpoint; final result appended below. Includes synchronized host/guest/TV case, private roles, local Lewis listener-continuity test, actual finalized fake-device clips and real Uvicorn audio frames above old16KiB cap.
- Additional reviewer decoder reproduction confirms finding1. The same input without null attribution is accepted, avoiding a malformed-fixture false positive.
- A Windows Proactor connection-reset log appeared during browser teardown; no failed test at that point. This is not a paid provider/device rehearsal.
- Main code CI `40980550600` is green. PR CI still running at checkpoint. No approval or merge readiness inferred from green tests because source-confirmation and same-act reset coverage remain incomplete.

The original Stop/reset/pause/disconnect cancellation, fragmented-media, theory-retention and narration-revision fixes show real progress. Saved-room migration probes pass; backing up before schema4 adoption and human/device acceptance remain requirements. Keep the portrait/Lewis baseline and November4/10 gates.

Final local result: all22browser scenarios pass (2.5minutes), including synchronized host/guest/TV, private roles, audio transport and Lewis continuity. Re-ran backend+5review probes and24client checks with the91b08e3 test-only delta:367pass/3Windows skips and24pass. Build/runtime bytes are unchanged from tested7b2b918. PR CI remains running at review close. Findings1–4 remain applicable; no merge approval.

## Follow-up: d160344 nullable attribution fix

Reviewed `d16034465ae8fe0da00405a0337c6ad135826ab3`. Finding1 is resolved in the client contract: null attribution is accepted only with the fixed Unattributed audio label and no follow-up-answer attribution. All25client checks and production build pass locally. The original null-snapshot reproduction now accepts the legitimate record; a null record falsely claiming a follow-up answer is rejected. Backend/runtime outside this decoder is unchanged. No repeated full-browser claim: previous reviewer run22pass was before this decoder change; author reports22pass on8011, and d160344 CI is running.

Findings2–4 remain: same-act lobby Reset capture cleanup (P1), stale confirmation after Resume (P2), and overwritten actionable error status (P2). App.tsx is unchanged by d160344. PR2 remains unmerged and not approved.
