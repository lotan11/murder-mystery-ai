# Authoritative task backlog

**Integration deadline: November 10, 2026 (America/Denver).** Track the avatar critical path and readiness gates in INTEGRATION_PLAN.md. The approved portrait + Lewis remains the runnable fallback.

Updated October 29, 2026. Lead/integrator owns this board. Status reflects committed milestones and current acceptance; no duplicate component implementations.

## Accepted foundation: M1 — reliable Blackthorn rehearsal

| ID | Priority | Stream / owner | Status | Deliverable / acceptance |
| --- | --- | --- | --- | --- |
| M1-01 | P0 | Lead | Done | Inspect main, branches, PR1 and failed CI; reuse reviewed recovery fixes |
| M1-02 | P0 | Story | Done; local + CI pass | Blackthorn canon, fair clue timeline, targeted released-fact dialogue, hints and recap |
| M1-03 | P0 | Backend | Done; local + CI pass | SQLite room recovery, durable identities/votes/progress, atomic write failure handling |
| M1-04 | P0 | Guest/host | Done; local + CI pass | Host clue gates, act instructions, guest quick questions, lighter phone rendering |
| M1-05 | P0 | QA / lead | Done; local + CI pass | Full case, storage restart, WebGL failure, client validation, Windows launcher and green remote CI |
| M1-06 | P0 | Lead | Done | Specification, decisions, game design, backlog and progress report in repo |

## Current delivery and next milestones

| ID | Priority | Milestone | Status | Acceptance / dependency |
| --- | --- | --- | --- | --- |
| M2-01 | P1 | Private characters | Done; local + CI pass | Assign character cards; public identity and private goals separated server-side |
| M2-02 | P1 | Private characters | Done; local + CI pass | Guest-only secret delivery and host roster; reconnect restores assignment without leaking secrets |
| M2-03 | P1 | Participation | Done; local + CI pass | Introductory round, accusation rationale and final reconstruction tied to motives |
| M2-04 | P1 | Rehearsal | Automated four-guest flow passed; human rehearsal pending | Four actual players, phones + TV, 20–30 minute rehearsal and feedback record |
| M3-01 | P1 | Optional AI | Done; local + CI pass | Explicit Responses adapter, released-fact plan, strict validation and deterministic fallback |
| M3-02 | P1 | Optional AI | Done; local + CI pass | Grounding/injection/timeout/request-budget tests, offline-only automation |
| M3-03 | P1 | Live validation | Not enabled | User-configured key/model/spend and deliberate live smoke test; no credentials in Git/chat |
| M3-04 | P2 | Dialogue design | Backlog | Evaluate factual validation before allowing arbitrary model-written prose |
| M4-01 | P2 | Speech | Planned | Consent, push-to-talk transcription, pause/mute/interruption and visible audio state |
| M4-02 | P2 | Character | Planned | Licensed rigged avatar, expressive gestures and readable captions |
| M4-03 | P2 | Speech/avatar | Planned | Custom voice and timestamped visemes; actual lip-sync validation |
| M5-01 | P2 | Hosted pilot | Planned | HTTPS, authentication, session expiry, rate limits, monitoring and backup/restore |
| M5-02 | P2 | Scaling | Planned | Shared room store/pub-sub before any multi-worker deployment |
| OPS-01 | P1 | Resilience | Backlog | Bound slow-client sends and implement room expiry/pruning |
| OPS-02 | P1 | Data lifecycle | Backlog | Versioned case migrations/export and user-visible room deletion |

## Routine decisions and user decisions

The lead resolves architecture and implementation choices within the accepted scope. External model/voice spend, avatar licensing or public hosting need a concrete proposed integration before user input. A paid provider adapter exists but remains disabled by default; no paid invocation, recording, purchased asset or public deployment is enabled in the current rehearsal.

Planning context: earlier availability was three weeks part-time, roughly 10–12 hours/week. M1 supplies reliable recovery; M2 now supplies playable character participation. M3 now adds optional bounded planning; human rehearsal and deliberate live-provider validation remain next. Production-quality voice, avatar and hosting are separate milestones, not an implied three-week promise.

## TalkingHead audition — October 28, 2026

| ID | Owner | Status | Acceptance |
| --- | --- | --- | --- |
| M4-A1 | Backend | Implemented | Local Windows recording generator; validated fixed sample API |
| M4-A2 | Frontend | Implemented | Lazy TalkingHead audition, actual word-timed visemes, stop/change and audio fallback |
| M4-A3 | Assets | Done | CC0 sample provenance; MIT library notices |
| M4-A4 | Lead / QA | Local checks passed; CI pending | Game regression, browser mouth movement, real Windows playback, CI |
| M4-A5 | Product | Pending later | Select final British voice and detective asset; live game speech integration |

- M4-A6: Implemented restrained lip strength and gentle upper-face expression from user feedback; production build and browser verification passed locally; remote CI pending. Final voice/face remain open.

## Current increment: playable local TV performance

| ID | Owner | Status | Acceptance |
| --- | --- | --- | --- |
| M4-T1 | Backend | Implemented; local tests pass | Bounded Windows local speech for authenticated current public dialogue only |
| M4-T2 | Frontend | Implemented; local playback pass | Shared approved renderer; opt-in TV speech and interruption |
| M4-T3 | Lead / QA | All seven browser tests pass; CI pending | Browser playback/pause/mute/stale/error and privacy regression |
| M4-T4 | Lead | Implemented | Windows setup, limits, decisions and verification record |

Approved animation refinement CI is green: run 40715846893. No final voice or asset purchase is authorized or needed for this increment.

## Serious detective and editable case — October 28, 2026

- Implemented: serious, respectful detective throughout game narration, scripted replies, approved AI remarks and local audition recordings. Known earlier saved narration is normalized on restore.
- Implemented: one server-only JSON case package, validated at startup, with facts, suspects, private cards, hints, topic aliases and event narration. Compatibility exports preserve the engine.
- Pending later: multiple-case selection, arbitrary role IDs/rosters, editor UI and reusable visual themes. The current prototype keeps fixed role IDs and three investigation acts.
- Verification: 197 backend tests pass (one Windows privilege skip); production build and all seven browser checks pass locally; current CI pending.

## Current approval milestone: Wobblebottom casting

| Task | Owner | Status | Evidence |
| --- | --- | --- | --- |
| Three premium concept portraits | Lead / image generation | Done | Classic, Modern, Scholar; source PNGs and exact prompts in repo |
| Three British neural voice candidates | Backend | Done | George, Daniel, Lewis; nine actual local WAVs, fixed identical scenes |
| Nine-pair comparison studio | Frontend | Done | Separate casting route, captions, play/stop and local-only shortlist |
| Restore restrained dry humor | Lead | Done | Default narration, scripted framing and approved remarks; no slapstick |
| Regression / playback checks | Lead / QA | Local pass; CI pending | 215 backend, 15 client, nine browser scenarios; actual nine-clip playback |
| Character / voice selection | User | Selected Scholar + Lewis | User selection recorded October 28, 2026; no game activation yet |
| Delivery / inflection approval | User / lead | Approved +5% pace | Proceed with Scholar and Lewis |
| Selected 3D rig | Lead | Production pending | Approved concept; three-view construction sheet and technical brief prepared |

Casting source commit `ec39e04` passed independent CI run 40769768890, including all nine browser scenarios. Next direction is The Scholar with Lewis; preserve the working game during delivery refinement and rig preparation.

- Lewis pacing revision: requested slightly faster; 1.05x comparison preview prepared with original pace retained. User subsequently approved the +5% pace; live game integration now delivered.

## Approved Scholar + Lewis integration

- User approved pairing and slightly faster Lewis pace. No further selection approval is needed to implement that direction.
- Backend: live selected Lewis neural rendering of current public dialogue; bounded isolated runtime — implemented and tested.
- Frontend: selected Scholar portrait/voice stage, explicit audio controls, preserved original/animated modes — implemented and tested.
- QA: auth/privacy, stale audio, pause/mute, approved pace, full existing regression — 247 backend / 15 client / eleven browser checks pass locally; CI pending.
- Asset production: likeness-matched Scholar 3D rig remains pending; concrete brief recorded separately. Portrait mode must not be represented as the finished rig.

## Scholar 3D authoring foundation

- Done: verified portable Blender and pinned anatomical MPFB authoring environment, no paid service/system install.
- Done: actual editable development bust, reproducible settings/build, exported 15-mesh GLB and front/profile renders; zero rig joints/facial morphs explicitly recorded.
- Done: separate character workbench with actual geometry inventory and camera/failure controls; active TV remains approved portrait + Lewis.
- Local checks: 251 backend / 15 client / thirteen browser scenarios and production build pass; source CI pending.
- Next: improve likeness, eyelids, hair/scalp/beard and wardrobe materials, then create real facial topology/targets and compatible rig. This blockout is not awaiting another casting decision and is not production ready.

## Deadline planning checkpoint — October 28, 2026

- Recorded November 10 deadline and internal asset/rig/integration/freeze/rehearsal checkpoints; hourly automation now includes the deadline.
- Confirmed authoring milestone CI run 40792819175 passed.
- Active asset increment: reduce heavy eyelids and refine mature facial proportions/beard against approved reference; no TV activation.
- Remote feature/listener discovered and documented as unmerged; saved-room/privacy/transcription review needed before reuse. No paid transcription or branch merge performed.

- Completed this checkpoint: alert-eye/cheek refinement and denser beard guide; editable source/export/renders/inventory rebuilt together. Verified 251 backend tests, build and both focused browser scenarios. Live game health remains good. Facial rig still absent; next priority is actual weighted/deformable rig work under the deadline plan.

## Weighted skeleton proof and facial study — October 28, 2026

Completed a real MPFB weighted-source experiment: 64 bones, all 19,158 source vertices weighted, measured head motion and exact rest restoration. This proof remains separate from the public bust. Created an editable face study with three actual pose-derived morphs (jawOpen, eyeBlinkLeft, eyeBlinkRight), transferred to the existing head and beard without changing neutral geometry. Export contains 15 meshes, three morph names and zero skeleton joints. Binary inspection measures nonzero displacement; these are not inventory placeholders.

The separate character lab now selects the face study and exposes real sliders: jaw capped at 0.38, full blinks and reset. Reviewed close-up neutral/jaw/blink renders; eyelids close, but groom, materials, mouth interior and production deformation still need refinement. This is an early study, not the finished Scholar or a speech-connected rig. Default game portrait, Lewis at 1.05x, existing animation modes and saved-room format are untouched. Next: refine deformation quality, complete expressive/viseme controls and bind the finished bust before voice alignment. November 10 risk remains custom avatar quality; the playable portrait/Lewis fallback is preserved.

## Bound Scholar development study — October 28, 2026

Bound a separate copy of the Scholar face study to the actual imported MPFB skeleton. Public GLB now contains 15 skinned meshes, one skin, 64 joints and the same three real facial morphs. Every exported vertex has normalized positive weights and valid joint references. Skin uses anatomical source weights; groom uses four-neighbour weight transfer; glasses/eyes/scalp attach rigidly to Head and wardrobe to Spine2. This intentionally avoids claiming cloth or shoulder deformation.

Measured positive/negative ten-degree head turns, combined head/jaw/blink evaluation, neutral preservation and rest restoration. A real close-up render verifies head accessories following the head. Character lab adds a separate weighted-rig choice and manual restrained head-turn control, while static and face-only studies remain available. Browser validation measures both the actual bone quaternion and a skinned spectacle vertex. No live game activation, paid provider, speech connection or saved-room change. Likeness, groom/materials, mouth interior, complete facial controls and Lewis alignment remain unfinished and the main November 10 risk. Approved portrait/Lewis +5% remains the playable baseline.

## Restrained Scholar brow expressions — October 28, 2026

Added five actual brow morphs to the existing weighted rig study: inner lift, independent outer lifts and independent lowering. These derive from pinned MPFB legacy expression-unit target geometry, with source hashes recorded and deltas transferred to skin and nearby brow/hair guides. This corrects an earlier incomplete tool inventory: data/expressions is empty, but raw targets/expression/units contains usable units. It is not a supplied complete ARKit/viseme package.

Rig study now has 64 weighted joints and eight real facial controls. Manual lifts cap at 0.35 and lowering at 0.25. Reviewed an actual close-up brow-lift render. Binary checks measure nonzero displacement and confirm the three original jaw/blink deformations are unchanged; source checks locate brow motion above 1.5m and neutral/rest errors remain below one micrometre. The original static and three-control face-only studies remain intact. Game portrait/Lewis at 1.05x, interfaces and saved rooms are unchanged. No paid provider or speech connection was added.

Next: mouth interior/lip shaping and complete speech deformation, followed by actual Lewis alignment. Likeness/groom/materials still need substantial polish. The animated Scholar remains the main November 10 risk; portrait/live Lewis stays the stable playable baseline. No user decision is required for this increment.

## Restrained mouth-shape study — October 29, 2026

Added three real anatomical mouth units to the existing weighted Scholar study: lip rounding (0.25 cap), compression (0.25 cap) and slight bilateral smile (0.20 cap). Source target hashes are recorded; skin and nearby beard guides receive actual geometry deltas. The rig now has 64 joints and eleven facial controls. All eight earlier morph displacement inventories match the preceding commit exactly. Neutral/rest geometry is preserved.

Reviewed actual renders for each mouth control. At the manual caps, maximum displacement is about 4.1mm rounding, 2.2mm compression and 2.6mm smile; this is deliberately restrained. Binary tests verify actual motion, source localization, distinct targets, normalized skin weights and missing viseme inventory. These are manual expression units, not complete phoneme shapes or voice alignment. Mouth interior/teeth/tongue, final likeness/groom/materials and actual Lewis synchronization remain unfinished.

Approved portrait/live Lewis at +5%, original animation modes, playable mystery, interfaces and saved-room schema remain unchanged. No paid provider calls or purchases. Next: mouth-interior/deformation quality and real speech alignment; do not activate the unfinished study in the game. Final animated-character quality remains the main November 10 risk; the approved playable fallback is retained. No new user decision is needed.

Follow-up: obtain and validate real audio-derived phoneme/viseme timing for the approved local Lewis WAVs; the current worker manifest contains audio duration, not phoneme timestamps. Preserve approved synthesis/playback speeds. Do not substitute invented text-proportional timing for an alignment claim.

## Lab performance correction and real Lewis timing proof — October 29, 2026

Investigated failed CI40829947023: fourteen browser scenarios passed; the expanding rig-control scenario exhausted its 90-second budget on the slower software-GPU runner. Replaced continuous static-lab GPU rendering/geometry diagnostics with change-driven draws. Orbit damping, resize, model loading and manual controls still render correctly; no timeouts or assertions were relaxed. Added actual render-count checks for idle settling, mouse orbit and pose-triggered redraw. Rig scenario dropped from52s locally to5.7s. Existing animated TV modes are untouched.

Direct inspection confirmed the approved pinned ONNX model exposes duration output. Added a separate optional local timing probe:73 model-predicted phoneme spans over5.502s, captured from the same inference inside existing create(), with the exact same audio object and identical PCM output. This corrects the earlier inference that another alignment service was necessarily required. The game worker currently discards these available timings and remains unchanged. Separate neural renders vary; always retain cues from their own waveform. These are model-supplied sample-clock timings, not text-proportional estimates, external forced alignment or manually annotated ground truth. At1.05 playback use audio.currentTime rather than speeding cue timestamps twice.

Verification:264 backend tests pass (two Windows permission skips),15 client checks, production build and all15 browser scenarios pass. No paid calls/downloads or presentation/schema changes. New CI follows push; prior failed run is explicitly recorded rather than reported green. Next: bounded worker/sidecar timing integration and lab-only speech deformation, plus mouth interior/likeness/groom polish. Final animated-character quality remains the main November10 risk; portrait/live Lewis stays playable. No user decision needed.
