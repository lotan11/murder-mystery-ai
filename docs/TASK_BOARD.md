# Authoritative task backlog

**Integration deadline: November 10, 2026 (America/Denver).** Track the avatar critical path and readiness gates in INTEGRATION_PLAN.md. The approved portrait + Lewis remains the runnable fallback.

Updated October 30, 2026. Lead/integrator owns this board. Status reflects committed milestones and current acceptance; no duplicate component implementations.

## Current priorities — October 30, 2026

| Priority | Work | Current state / next gate |
| --- | --- | --- |
| P0 | Premium Scholar likeness and groom | Denser fitted facial groom tested; crown/hairline and matched-view facial likeness remain P0 |
| P0 | Browser-delivered materials | Three1K baked maps now embedded/decoded; grain delivery fixed, final color/skin/eye artistry still unfinished |
| P0 | Speech deformation and oral detail | Fixed real Lewis lab study works; full natural visemes, teeth/tongue and perceptual review unfinished |
| P1 | First-generation speech latency | Warm replay cache implemented; new/expired/evicted text still needs generation; no prefetch yet |
| Completed foundation | Bounded public replay cache | Four entries/32MiB/15-minute reuse lifetime; actual local cold12.107s/warm0.005724s, one worker |
| Completed foundation | Restrained iris material | Supported512px slate-grey texture on actualUV1; preserved eye anatomy; final eyes/likeness unfinished |
| Completed foundation | Portrait head comparison | Same approved image cropped in Face close-up; full bust/reset preserved; new hair experiment rejected |
| Done this increment | Core hair and skin refinement | Actual source-fitted textured silver hair and masked color bake; final likeness still open |
| Protected baseline | Playable Blackthorn case | Approved portrait/live Lewis, private roles, recovery and existing modes preserved |

November4 is the animated-character readiness gate; November10 remains integration deadline. See SCHOLAR_QUALITY_REVIEW.md for concrete visual priorities. Historical milestone records follow.

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

## First opt-in timed Scholar speech study — October 29, 2026

The weighted rig can now perform a fixed real Lewis line in the separate character lab. Choose Rig study and Play Lewis timing study. No autoplay. The clip is the verified5.502-second same-inference proof, at approved1.05 playback; its73 model-predicted cues follow audio.currentTime. A restrained, explicitly approximate phoneme-to-existing-mouth mapping drives real morph influences. Unknown symbols/gaps stay neutral. This is a speaking deformation study, not a complete viseme rig or finished natural lip-sync/likeness.

Client streams are bounded (512KiB metadata/8MiB WAV); PCM format/duration and SHA256 pairing are checked before Blob playback. Stop, pending-fetch cancellation, model change, graphics loss, hidden page and unmount cancel/reset/revoke resources. Idle GPU optimization remains. Reviewed an actual speaking-model screenshot: mouth motion remains small; sparse groom, wardrobe blockout, mouth interior and overall likeness still need substantial work. Approved game portrait/live Lewis remains the TV default.

The existing local worker now retains model timing from the same synthesis call in a separate optional sidecar. Backend validates exact source-clock/schema, finite sorted/nonoverlapping spans,4000-cue/512KiB bounds and safe file reads; missing sidecars retain legacy compatibility, malformed ones fail safely. Endpoint revalidates optional metadata and retains current-public-text auth/revision/pause protections. No default avatar activation, room schema change, paid call or download. Actual worker smoke:Lewis/5.502s/73cues/approved1.05 rate. Next: mouth interior and perceptual deformation/likeness polish, long-line timing review and lab-to-live integration only after quality gates. November10 animated-character quality risk remains; no new user decision required.

## Anatomical oral lining and longer narration evidence — October 29, 2026

Refined the weighted Scholar study's existing mouth cavity using the pinned anatomical inside-mouth UV mask. Assigned a dark rough oral-lining material to398 existing faces/418 vertices, with source hash and bounds recorded. No new geometry, fake black plane, teeth or tongue were added. Actual vertex/triangle counts, neutral shape and original jaw/blink displacement counts/magnitudes remain unchanged; only the head's material primitives split. Reviewed the actual open-jaw render. Detailed teeth/tongue, groom, wardrobe, likeness and natural speech shapes remain unfinished; the approved game portrait/live Lewis remains the default.

Ran the actual local worker on59 words/378 characters concatenated from canonical public welcome/start/advance narration. It produced25.0606s/391 model cues with zero overlap/out-of-bounds results, preserving Lewis0.92 synthesis and1.05 playback. The same-waveform sidecar passed backend validation. Generation took21.096s on this machine within the unchanged40s bound. This is one observed sample, not a max-length, internal-batch, perception or performance guarantee. Longer clips can have noticeable preparation latency; caching/prefetch/performance evaluation is now a tracked integration task. No paid calls/downloads or live-room changes.

Next: detailed mouth/face quality and perceived speech review, plus measured latency improvement before live3D integration. November10 risk remains final character quality and long-dialogue responsiveness. No new casting/voice decision is needed; preserve the working fallback.

Next performance task: evaluate bounded public-dialogue voice caching/prefetch without changing voice/pace, privacy, stale-state guards or the40s worker policy. Record cold/warm observations rather than assuming every1500-character input meets interactive latency.

## Bounded public speech replay cache and art quality review — October 29, 2026

Added a process-local memory cache for successful validated Lewis clips and their matching model timing. Default bounds: four entries,32MiB of immutable serialized payloads,15-minute non-sliding reuse lifetime. Expired entries are pruned on cache activity, not a background deletion timer. Hits decode a fresh result copy; oversized results, failures, timeouts and cancellations are not retained. Cache faults fall back to normal valid rendering. No extra audio files persist after the existing temporary-worker cleanup.

Authorization, current-public-text selection, pause/revision/stale checks and HTTP no-store remain on every endpoint request; room credentials/revisions are not cached. Approved voice,0.92 synthesis/1.05 playback and40s worker bound remain unchanged. A warm clip may be served while a different cold clip is preparing, without another worker.

Real isolated59-word renderer probe: one25.06s/391-cue clip took12.107s on the first cache miss and0.005724s on immediate replay, with one worker total and identical waveform/timing data. Retained payload was1,630,999bytes; generation directory was empty afterward. These are local observations for an empty renderer cache followed by one hit, not cold-machine or cross-device guarantees. New, expired or evicted lines remain cold; no prefetch is implemented. The new backend cache takes effect when the server is started with this source.

A separate actual-asset review confirms the model is not yet premium-ready: hair/beard silhouette, matched-camera likeness, materials and tailoring remain substantial gaps. Procedural Blender skin detail is absent from the actual GLB; supported baked PBR maps need explicit export/browser verification. See SCHOLAR_QUALITY_REVIEW.md. No new model, voice, casting request, purchase or game presentation change was made. Next visual priority: groom/likeness and browser-delivered skin detail, while preserving the playable portrait/Lewis fallback. November10 risk remains final art/perceived speech quality and first-generation latency; no input is required now.

Next P0visual task: use matched camera/lighting, refine silver hair/beard silhouette and deliver baked supported skin maps in the actual GLB/browser. Require visual comparison, deformation regressions and measured runtime texture inventory; source-only procedural detail is not completion. Cache miss/first-generation latency remains a separate performance task.

## Browser-delivered baked skin materials — October 29, 2026

Closed the missing-runtime-detail gap on the weighted Scholar study. A reproducible Blender helper now bakes existing skin base color (COLOR-only, no lighting), roughness and tangent normal maps at1024px, binds supported image nodes and packs them into editable source/GLB. The normal bake is compared with a real bump-disabled baseline over an emission coverage mask: measuredRMSXY0.009305, proving the source's shallow procedural grain is captured. This is not authored wrinkles, a skin scan, final skin artistry or subsurface reconstruction.

Actual GLB inventory has four embedded images (coat plus three skin maps); skin has baseColorTexture, normalTexture and metallicRoughnessTexture. Normal and base-color embedded image hashes exactly match source PNGs; roughness is packed into the glTF channel layout. Inspector now records actual material references/image dimensions/hashes. The browser confirms three decoded1K textures on the actual loaded skin material, not a model-mode label. Reviewed actual browser close-up and Blender open-jaw render: subtle grain survives export; the model is still visibly a blockout.

Original101,835 exported vertices/165,239 triangles,64 joints/11 morph names, normalized weights, oral lining, neutral/rest deformation and restrained Lewis timing study remain. Canonical static/face-only studies, game portrait/liveLewis(+5%), interfaces and saved rooms are unchanged. No paid calls/downloads/new casting decisions. Next P0: coherent silver hair/beard groom and matched-view likeness; more art and perceptual speech work remains before November4 readiness gate/November10 integration. First-generation speech latency also remains; replay cache is preserved.

## Fitted facial groom development refinement — October 29, 2026

Added denser fitted silver beard/moustache clumps to the weighted Scholar study. The selected facial-only helper creates2200beard/800moustache clumps (18,000vertices/12,000triangles) with stored head-triangle barycentric correspondence for normalized bone weights and four genuinely nonzero mouth targets. No dummy brow/viseme keys were added. Original head rest positions, head geometry/deformation ranges, skin maps, oral lining,64-joint skeleton and11global control names are preserved. Canonical static/face-only studies and approved game portrait/liveLewis remain unchanged.

Matched front/profile previews caught inverted-card shading and an overly angular crown experiment. Those were rejected before public export. The accepted development increment is facial hair only; original scalp/crown remain unchanged, including known cap/hairline gaps. Outward-face guard records zero inversions; normalized-weight and morph-correspondence errors are below one micrometre. Five restrained pose checks keep groom points outward from their source triangles; the rest lip-proxy gap is about2mm. These geometric checks do not certify every combined pose or natural-looking hair.

Actual browser playback on8018 loaded19renderprimitives/64joints/11controls/three skin maps, used approved1.05Lewis pace with pitch preserved, showed real mouth motion, and Stop returned to neutral. Reviewed the live screenshot and actual front/profile renders: moustache/beard are denser but still coarse ribbons/stubble with uneven coverage. No obvious new floating/black-face/lip-bridge issue appeared in those frames; this is not perceptual phoneme-level lip-sync certification. GLB16meshes/119,835vertices/177,239triangles, about13.27MB, no external resources.

Inspector now exposes component-level geometry/morph inventory so deliberate groom growth cannot hide changes to the original head. Tests check original head positions across material splits plus real new weighted geometry and fit guards. Next P0: crown/hairline shape and matched-view facial likeness, then finer groom/material/oral quality. November10 final-art and first-generation speech-latency risks remain; no new user decision or casting approval is needed. No paid calls/downloads or default-game activation.

## Crown fit and matched framing — October 29, 2026

Completed: cap-only surface projection and anatomical weight transfer; front/profile before/after review removes visible scalp holes. Added explicit face/full-bust framing for desktop/phone inspection. Existing 64 joints, eleven controls, skin maps, facial groom and original head are preserved.

Next: replace the helmet-like hairline/coarse guide appearance with coherent silver grooming, then refine portrait-matched facial proportions, eyes and tailoring. Sharp ear-edge cap coverage remains unresolved (raw triangle sign disagreements retained), as do full visemes and perceptual speech approval. November4 readiness gate and November10 portrait/Lewis fallback remain. No new casting selection or spending decision needed.

## Listener review — October 29

Completed deeper code/offline review of unmerged1f8bab0. **Blocked from merge**: pending permission/Stop/reset cancellation, broken Resume, invalid later WebM fragments,16KiB transport mismatch, Lewis interruption, dropped error states and false cross-clause claims. P2: theory retention and duration accounting. See LISTENER_REVIEW.md for evidence/reusable probes and ordered acceptance work. Branch baseline252pass/2skips; additional probes4fail/1migration pass. No provider calls or product activation. Avatar visual work resumes next; no avatar changes in this run.

PR2 follow-up: original listener repair probes pass, but merge remains blocked by unattributed snapshot contract and lobby Reset microphone cleanup; stale confirmation/error state also need repair. Formal review:reviews/PR2_INTEGRATION_REVIEW.md. Keep one authoritative main and rerun affected integrations on the repaired PR revision.

PR2 d160344 follow-up: null-attribution decoder blocker verified fixed (25client/build pass). Remaining lobby Reset capture blocker and Resume/error cleanup are unchanged; retain no-merge disposition pending their repair/retest and current CI.

PR2 0b2e809: scoped review clears previously reported reset/Resume/error defects;370backend+review checks and25client/build pass. Final24browser run and CI pending before integration disposition. No merge or microphone activation.

PR2 reviewed0b2e809: all previously reported findings cleared; independent370backend/review,25client,build,24browser checks pass (3Windows skips). Remote CI pending; no merge/activation. Actual device/provider acceptance stays separate from offline integration.

PR2 0b2e809 remote verification: both CI40996214412/40996209236 pass. Combined integration review cleared; PR remains unmerged.

## Iris material refinement — October29

Completed restrained512px radial iris albedo and supportedUV1 binding on the separate weighted Scholar. Actual front/profile before/after reviewed; eye geometry/pupils/sclera and all head/skin/rig/groom remain unchanged. Browser decoding and geometry/material guards accompany delivery. This reduces flat cyan appearance; heavy eyelids, anatomical likeness and premium eye finish remain open. Next P0 remains silver-hair silhouette/groom and portrait-matched face; tailoring/oral/perceived speech quality also remain. November4 gate/November10 fallback unchanged.

## October30 hair gate and comparison increment

Delivered display-only approved-portrait head crop synchronized with Faceclose-up; desktop/phone review and Reset/model restoration covered. Rejected two procedural tube-clump crown passes: helmet line/wire loops remained despite valid weights/attachment. Public rig/source unchanged; no new hair shipped. See reviews/HAIR_REFINEMENT_REVIEW.md.

Next P0: inspect/license/hash and visually assess an existing swept-hair asset, then fit actual Scholar geometry and validate exported materials/attachment. Official MakeHuman inventories are source leads only; no hair asset selected/downloaded. Likeness/lids/tailoring/oral/perceived-speech quality and November4/10 risk remain. ListenerPR2 remains reviewed/green/unmerged.

## October30 core hair/skin increment

Accepted bounded development improvement: real MHCLO-fitted short02silver hair and45%masked skin-color blend. Seven images embed; canonical studies, face/eyes/controls and defaultgame portrait/liveLewis retained. Excluded mixed-header community candidates and eye-obstructing short03. 317backend tests pass (3Windows skips); no finalhair/skin/likeness claim. NextP0: facial/eyelid proportions, shapedfacialgroom, tailoring/oral and loosehair refinement; November4gate/November10 risk unchanged.

ListenerPR2 advanced toddf2778 with speaking-state signaling; priorapproval0b2e809 doesnotcovernewhead. Freshreview finds guestdevice read-aloud bypasses local mic suppression. Keepunmerged pendingrepair/combinedchecks.

Finalvalidation: main6de53db CI41061277059 green;317backend/3Windows skips,21client/build,20browser pass. Combinedlistener generalchecks374+28client+28browser pass, but targetedguest-device-narration testfails (mictracklive); no PR2approval/merge. Resolve localaudio suppression and docs/PROGRESS conflict before integration.

## October30 listener repair and character experiments

Completed: reviewed/published local narration capture fix4646c5c to the existing listenerPR2;28client/build and30fullbrowser scenarios pass, including two new real fake-microphone regressions. Backend rerun/remoteCI follow. PR is still unmerged; current-main reconciliation and device acceptance remain.

Character: rejected wider alpha-card facial groom after actual browser review (patch-like appearance despite valid weights/deformations). Retained a modest localized eyelid preview for guarded future integration; not in publicsource/GLB. See reviews/SCHOLAR_EYELID_GROOM_REVIEW.md. Next: integrate declared eyelid offsets before groom with strict original-head guards, then natural facial-groom/tailoring/oral work and perceived speech review. Existing approved portrait/liveLewis1.05 remains the game default. November4/10 risk persists; no new casting decision or spending needed.

## October 30 eyelid integration and disconnect reliability

- Done: reviewed eyelid adjustment integrated before skin baking/groom fitting, with 419 explicit offsets and strict exported-head preservation. Source/GLB/maps rebuilt; actual app neutral/blink, Lewis pace/pitch and Stop verified.
- Local validation: 317 backend tests (three Windows skips), 16 asset checks, 21 client checks, build and 20 browser scenarios pass. Main CI 41125253884 passed.
- Listener PR2: reproduced disconnect cancellation race repaired on 2c6ecde. Cleanup precedes awaiting; recovery notification shielded for at most two seconds. Regression fails before repair and passes afterward. Branch backend: 368 pass/three skips. Combined current-main: 370 backend pass/three skips, 28 client checks/build; all 30 browser scenarios and branch CI 41125090564 pass. Sole conflict: progress document. PR unmerged.
- Next: natural facial groom, portrait likeness, tailoring/oral detail, perceived speech review and controlled listener integration with verified local startup/database recovery.
- Risk: November 4 character readiness and November 10 finished-avatar quality. Approved portrait/live Lewis at 1.05 remains the stable playable baseline. No new user input or purchase needed.
