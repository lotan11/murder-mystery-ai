# PR2 playback-state follow-up review

Reviewed ddf2778; latest12f2394 adds tests/documentation only, leaving this runtime path unchanged. Earlier0b2e809 review approval does not cover this contract. PR stays unmerged.

## Confirmed P1: guest read-aloud bypasses local microphone suppression

`frontend/src/App.tsx:640–647` lets guests enable device “Read dialogue aloud.” The suppression path at204–206 uses only `room.scholar_speaking`, while the local `browserSpeechActive` flag is excluded. Signaling at435–438 runs forTV views only. Original-function offline execution with local browserSpeechActive=true and room.scholar_speaking=false explicitly calls setSuppressed(false) and reports microphone live. A guest can therefore record/transcribe its own app narration.

Include local device/browser narration in the effective suppression state, and react when that local flag changes even without another room snapshot. Alternatively disallow guest read-aloud while capture is active, with clear UI and tests. Add a regression that uses the local guest speech path, not only an injected TV speaking event; verify tracks disabled, overlapping clip discarded and fresh capture resumes afterward.

## Scoped positive checks and limits

Code review found TV-capability authorization, aggregate multi-TV speaking state, disconnect cleanup, non-persisted state and unchanged narration revision sound in this diff. The approved Lewis playback pace is preserved. Animated hidden-tab completion recovery lacks an independent completion/lease test; no stuck-state reproduction was obtained, so this is a coverage gap rather than a confirmed defect.

Combined current-main host/guest/TV and saved-room checks follow after the avatar increment is committed. Green existing branch tests alone cannot close the confirmed local-narration gap. No real microphone/provider call, merge or live migration was performed.
