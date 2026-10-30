# PR2 playback-state follow-up review

Reviewed ddf2778; latest12f2394 adds tests/documentation only, leaving this runtime path unchanged. Earlier0b2e809 review approval does not cover this contract. PR stays unmerged.

## Confirmed P1: guest read-aloud bypasses local microphone suppression

`frontend/src/App.tsx:640–647` lets guests enable device “Read dialogue aloud.” The suppression path at204–206 uses only `room.scholar_speaking`, while the local `browserSpeechActive` flag is excluded. Signaling at435–438 runs forTV views only. Original-function offline execution with local browserSpeechActive=true and room.scholar_speaking=false explicitly calls setSuppressed(false) and reports microphone live. A guest can therefore record/transcribe its own app narration.

Include local device/browser narration in the effective suppression state, and react when that local flag changes even without another room snapshot. Alternatively disallow guest read-aloud while capture is active, with clear UI and tests. Add a regression that uses the local guest speech path, not only an injected TV speaking event; verify tracks disabled, overlapping clip discarded and fresh capture resumes afterward.

## Scoped positive checks and limits

Code review found TV-capability authorization, aggregate multi-TV speaking state, disconnect cleanup, non-persisted state and unchanged narration revision sound in this diff. The approved Lewis playback pace is preserved. Animated hidden-tab completion recovery lacks an independent completion/lease test; no stuck-state reproduction was obtained, so this is a coverage gap rather than a confirmed defect.

Combined current-main host/guest/TV and saved-room checks follow after the avatar increment is committed. Green existing branch tests alone cannot close the confirmed local-narration gap. No real microphone/provider call, merge or live migration was performed.

## Combined integration and real-app reproduction

Tested currentmain `6de53db` plus PRruntime `12f2394` with726dda9's additional browser regression (726dda9 changes tests/docs only). A no-checkout Git merge-tree rehearsal found one documentation conflict in docs/PROGRESS.md and no runtime conflict. The isolated test snapshot chose currentmain's progress document for that conflict only; no actual merge or branch change occurred.

Combined results:369backend +5review probes pass (374total),3Windows skips;28client checks/build and all28existing browser scenarios pass. Host/guest/TV case completion, saved-room restart/migration, newhair/skin bindings, roleprivacy, Lewis pace and existing listenerpermission/pause/TVspeaking tests remain compatible.

**Additional targeted real-app acceptance test fails:** local guest device narration triggers speech.onstart while room.scholar_speaking=false; synthetic microphone reports `{spoken:true, enabled:[{enabled:true,state:live}]}`. The test uses original app code, controlled native SpeechSynthesis callbacks and Chromium's fake microphone, with paidtranscription disabled; no actual microphone/provider. This confirms the previously isolated predicate defect beyond code inspection. Repro source is PR2_LOCAL_NARRATION.spec.ts; copy it into the isolated combined frontend/e2e and run explicitly on its own local port. It is outside main's default test discovery, since main has no listener.

PR2 remains blocked on local-narration suppression and documentation conflict resolution despite green general suites. Require trackdisable, discarded overlap and freshresume for guest speech transitions, including pending permission; do not depend on another roomsnapshot. Hidden animated-tab completion remains a coverage gap, not a reproduced bug.

## Local-narration repair — 4646c5c

Root reviewed and published the repair on the existing feature/listener branch (parent726dda9), without merging it into main. Effective capture suppression now combines room playback with an immediate local-browser speech ref; local start/end updates capture without waiting for a room packet, and permission granted mid-narration reads the latest combined state. Existing controller discards interrupted clips and restarts a fresh segment. All cancellation sites clear the local flag. TV authorization/aggregation, transient state, room revisions and approved Lewis settings are unchanged.

Independent full browser run: **30 scenarios pass in2.8minutes** on isolated8024, including two new native Chromium fake-microphone regressions. They verify disabled tracks, no overlapping audio header upload, fresh recorder start after local narration ends, pending-permission handling and zero transcription usage. Agent validation:28client checks and production build pass;10focused media scenarios pass. No real microphone or paid provider was used. Backend rerun and remote CI are pending at this checkpoint. The original confirmed P1 is repaired in this branch; hidden animated-tab completion coverage and final current-main integration/documentation reconciliation still remain. Main and its running8018app are unchanged.

Backend follow-up: initial quiet local run stalled without a failing assertion and was terminated; diagnostic verbose rerun with30s stack timeout completed **367passed/3Windows skips in15.95s**. No backend code changed. This is branch-only scope; earlier374combined count included newer main assets and five review probes. RemoteCI41093819389 is still on backend tests, so readiness remains pending and the stall is not claimed fixed.
