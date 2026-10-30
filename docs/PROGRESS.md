## Fitted facial groom development refinement — October 29, 2026

Added denser fitted silver beard/moustache clumps to the weighted Scholar study. The selected facial-only helper creates2200beard/800moustache clumps (18,000vertices/12,000triangles) with stored head-triangle barycentric correspondence for normalized bone weights and four genuinely nonzero mouth targets. No dummy brow/viseme keys were added. Original head rest positions, head geometry/deformation ranges, skin maps, oral lining,64-joint skeleton and11global control names are preserved. Canonical static/face-only studies and approved game portrait/liveLewis remain unchanged.

Matched front/profile previews caught inverted-card shading and an overly angular crown experiment. Those were rejected before public export. The accepted development increment is facial hair only; original scalp/crown remain unchanged, including known cap/hairline gaps. Outward-face guard records zero inversions; normalized-weight error is below1e-6 and morph-correspondence error is below one micrometre. Five restrained pose checks keep groom points outward from their source triangles; the rest lip-proxy gap is about2mm. These geometric checks do not certify every combined pose or natural-looking hair.

Actual browser playback on8018 loaded19renderprimitives/64joints/11controls/three skin maps, used approved1.05Lewis pace with pitch preserved, showed real mouth motion, and Stop returned to neutral. Reviewed the live screenshot and actual front/profile renders: moustache/beard are denser but still coarse ribbons/stubble with uneven coverage. No obvious new floating/black-face/lip-bridge issue appeared in those frames; this is not perceptual phoneme-level lip-sync certification. GLB16meshes/119,835vertices/177,239triangles, about13.27MB, no external resources.

Inspector now exposes component-level geometry/morph inventory so deliberate groom growth cannot hide changes to the original head. Tests check original head positions across material splits plus real new weighted geometry and fit guards. Next P0: crown/hairline shape and matched-view facial likeness, then finer groom/material/oral quality. November10 final-art and first-generation speech-latency risks remain; no new user decision or casting approval is needed. No paid calls/downloads or default-game activation.

Verification:313 backend tests pass (three Windows permission skips),21 client checks, production build and all19 browser scenarios pass. Actual8018 playback/Stop and matched renders reviewed. Prior code CI40867962436 passed; new source CI follows push.

Hosted CI confirmation: source commita4888d6 passes run40916235913, including component head preservation and all19 browser scenarios. This follow-up updates documentation only.

## Browser-delivered baked skin materials — October 29, 2026

Closed the missing-runtime-detail gap on the weighted Scholar study. A reproducible Blender helper now bakes existing skin base color (COLOR-only, no lighting), roughness and tangent normal maps at1024px, binds supported image nodes and packs them into editable source/GLB. The normal bake is compared with a real bump-disabled baseline over an emission coverage mask: measuredRMSXY0.009305, proving the source's shallow procedural grain is captured. This is not authored wrinkles, a skin scan, final skin artistry or subsurface reconstruction.

Actual GLB inventory has four embedded images (coat plus three skin maps); skin has baseColorTexture, normalTexture and metallicRoughnessTexture. Normal and base-color embedded image hashes exactly match source PNGs; roughness is packed into the glTF channel layout. Inspector now records actual material references/image dimensions/hashes. The browser confirms three decoded1K textures on the actual loaded skin material, not a model-mode label. Reviewed actual browser close-up and Blender open-jaw render: subtle grain survives export; the model is still visibly a blockout.

Original101,835 exported vertices/165,239 triangles,64 joints/11 morph names, normalized weights, oral lining, neutral/rest deformation and restrained Lewis timing study remain. Canonical static/face-only studies, game portrait/liveLewis(+5%), interfaces and saved rooms are unchanged. No paid calls/downloads/new casting decisions. Next P0: coherent silver hair/beard groom and matched-view likeness; more art and perceptual speech work remains before November4 readiness gate/November10 integration. First-generation speech latency also remains; replay cache is preserved.

Verification:311 backend tests pass (three Windows permission skips),21 client checks, production build and all19 browser scenarios pass. Browser confirms three actual decoded1K skin maps; source normal/base-color hashes match embedded images. No final art/perceptual approval implied. Prior code CI40859619619 passed; new source CI follows push.

Hosted CI confirmation: source commit5659c0e passes run40867962436, including material/geometry checks and all19 browser scenarios. This follow-up updates documentation only.

## Bounded public speech replay cache and art quality review — October 29, 2026

Added a process-local memory cache for successful validated Lewis clips and their matching model timing. Default bounds: four entries,32MiB of immutable serialized payloads,15-minute non-sliding reuse lifetime. Expired entries are pruned on cache activity, not a background deletion timer. Hits decode a fresh result copy; oversized results, failures, timeouts and cancellations are not retained. Cache faults fall back to normal valid rendering. No extra audio files persist after the existing temporary-worker cleanup.

Authorization, current-public-text selection, pause/revision/stale checks and HTTP no-store remain on every endpoint request; room credentials/revisions are not cached. Approved voice,0.92 synthesis/1.05 playback and40s worker bound remain unchanged. A warm clip may be served while a different cold clip is preparing, without another worker.

Real isolated59-word renderer probe: one25.06s/391-cue clip took12.107s on the first cache miss and0.005724s on immediate replay, with one worker total and identical waveform/timing data. Retained payload was1,630,999bytes; generation directory was empty afterward. These are local observations for an empty renderer cache followed by one hit, not cold-machine or cross-device guarantees. New, expired or evicted lines remain cold; no prefetch is implemented. The new backend cache takes effect when the server is started with this source.

A separate actual-asset review confirms the model is not yet premium-ready: hair/beard silhouette, matched-camera likeness, materials and tailoring remain substantial gaps. Procedural Blender skin detail is absent from the actual GLB; supported baked PBR maps need explicit export/browser verification. See SCHOLAR_QUALITY_REVIEW.md. No new model, voice, casting request, purchase or game presentation change was made. Next visual priority: groom/likeness and browser-delivered skin detail, while preserving the playable portrait/Lewis fallback. November10 risk remains final art/perceived speech quality and first-generation latency; no input is required now.

Verification:310 backend tests pass (three Windows permission skips),21 client checks, production build and all19 browser scenarios pass. Actual cache probe confirms one worker, identical audio/cues and bounded retained payload. Prior code CI40851331046 passed; new source CI follows push.

Hosted CI confirmation: source commitb17ee59 passes run40859619619, including backend/client/build/all19 browser scenarios. This follow-up changes documentation only.

## Anatomical oral lining and longer narration evidence — October 29, 2026

Refined the weighted Scholar study's existing mouth cavity using the pinned anatomical inside-mouth UV mask. Assigned a dark rough oral-lining material to398 existing faces/418 vertices, with source hash and bounds recorded. No new geometry, fake black plane, teeth or tongue were added. Actual vertex/triangle counts, neutral shape and original jaw/blink displacement counts/magnitudes remain unchanged; only the head's material primitives split. Reviewed the actual open-jaw render. Detailed teeth/tongue, groom, wardrobe, likeness and natural speech shapes remain unfinished; the approved game portrait/live Lewis remains the default.

Ran the actual local worker on59 words/378 characters concatenated from canonical public welcome/start/advance narration. It produced25.0606s/391 model cues with zero overlap/out-of-bounds results, preserving Lewis0.92 synthesis and1.05 playback. The same-waveform sidecar passed backend validation. Generation took21.096s on this machine within the unchanged40s bound. This is one observed sample, not a max-length, internal-batch, perception or performance guarantee. Longer clips can have noticeable preparation latency; caching/prefetch/performance evaluation is now a tracked integration task. No paid calls/downloads or live-room changes.

Next: detailed mouth/face quality and perceived speech review, plus measured latency improvement before live3D integration. November10 risk remains final character quality and long-dialogue responsiveness. No new casting/voice decision is needed; preserve the working fallback.

Verification:294 backend tests pass (three Windows permission skips),21 client checks, production build and all19 browser scenarios pass. Reviewed actual open-jaw lining render; no production appearance approval implied. Prior code CI40843961780 passed; new source CI follows push.

Hosted CI confirmation: corrected source commitaf0d1a8 passes run40851331046, including all19 browser scenarios. The raw-line-ending evidence failure is resolved; this follow-up changes documentation only.

## First opt-in timed Scholar speech study — October 29, 2026

The weighted rig can now perform a fixed real Lewis line in the separate character lab. Choose Rig study and Play Lewis timing study. No autoplay. The clip is the verified5.502-second same-inference proof, at approved1.05 playback; its73 model-predicted cues follow audio.currentTime. A restrained, explicitly approximate phoneme-to-existing-mouth mapping drives real morph influences. Unknown symbols/gaps stay neutral. This is a speaking deformation study, not a complete viseme rig or finished natural lip-sync/likeness.

Client streams are bounded (512KiB metadata/8MiB WAV); PCM format/duration and SHA256 pairing are checked before Blob playback. Stop, pending-fetch cancellation, model change, graphics loss, hidden page and unmount cancel/reset/revoke resources. Idle GPU optimization remains. Reviewed an actual speaking-model screenshot: mouth motion remains small; sparse groom, wardrobe blockout, mouth interior and overall likeness still need substantial work. Approved game portrait/live Lewis remains the TV default.

The existing local worker now retains model timing from the same synthesis call in a separate optional sidecar. Backend validates exact source-clock/schema, finite sorted/nonoverlapping spans,4000-cue/512KiB bounds and safe file reads; missing sidecars retain legacy compatibility, malformed ones fail safely. Endpoint revalidates optional metadata and retains current-public-text auth/revision/pause protections. No default avatar activation, room schema change, paid call or download. Actual worker smoke:Lewis/5.502s/73cues/approved1.05 rate. Next: mouth interior and perceptual deformation/likeness polish, long-line timing review and lab-to-live integration only after quality gates. November10 animated-character quality risk remains; no new user decision required.

Verification:291 backend tests pass (three Windows permission skips),21 client tests, production build and all19 browser scenarios pass. Actual model screenshot reviewed; speech remains a fixed experimental approximation. Previous code CI40836345515 passed; this increment CI follows push.

Hosted CI confirmation: code commit5a7ccca passes run40843961780, including all19 browser scenarios. This follow-up updates documentation only.

## Lab performance correction and real Lewis timing proof — October 29, 2026

Investigated failed CI40829947023: fourteen browser scenarios passed; the expanding rig-control scenario exhausted its 90-second budget on the slower software-GPU runner. Replaced continuous static-lab GPU rendering/geometry diagnostics with change-driven draws. Orbit damping, resize, model loading and manual controls still render correctly; no timeouts or assertions were relaxed. Added actual render-count checks for idle settling, mouse orbit and pose-triggered redraw. Rig scenario dropped from52s locally to5.7s. Existing animated TV modes are untouched.

Direct inspection confirmed the approved pinned ONNX model exposes duration output. Added a separate optional local timing probe:73 model-predicted phoneme spans over5.502s, captured from the same inference inside existing create(), with the exact same audio object and identical PCM output. This corrects the earlier inference that another alignment service was necessarily required. The game worker currently discards these available timings and remains unchanged. Separate neural renders vary; always retain cues from their own waveform. These are model-supplied sample-clock timings, not text-proportional estimates, external forced alignment or manually annotated ground truth. At1.05 playback use audio.currentTime rather than speeding cue timestamps twice.

Verification:264 backend tests pass (two Windows permission skips),15 client checks, production build and all15 browser scenarios pass. No paid calls/downloads or presentation/schema changes. New CI follows push; prior failed run is explicitly recorded rather than reported green. Next: bounded worker/sidecar timing integration and lab-only speech deformation, plus mouth interior/likeness/groom polish. Final animated-character quality remains the main November10 risk; portrait/live Lewis stays playable. No user decision needed.

CI confirmation: source commit7385b78 passed run40836345515, including all fifteen browser scenarios on the hosted runner. The earlier90-second rig timeout is resolved. This follow-up changes documentation only.

## Restrained mouth-shape study — October 29, 2026

Added three real anatomical mouth units to the existing weighted Scholar study: lip rounding (0.25 cap), compression (0.25 cap) and slight bilateral smile (0.20 cap). Source target hashes are recorded; skin and nearby beard guides receive actual geometry deltas. The rig now has 64 joints and eleven facial controls. All eight earlier morph displacement inventories match the preceding commit exactly. Neutral/rest geometry is preserved.

Reviewed actual renders for each mouth control. At the manual caps, maximum displacement is about 4.1mm rounding, 2.2mm compression and 2.6mm smile; this is deliberately restrained. Binary tests verify actual motion, source localization, distinct targets, normalized skin weights and missing viseme inventory. These are manual expression units, not complete phoneme shapes or voice alignment. Mouth interior/teeth/tongue, final likeness/groom/materials and actual Lewis synchronization remain unfinished.

Approved portrait/live Lewis at +5%, original animation modes, playable mystery, interfaces and saved-room schema remain unchanged. No paid provider calls or purchases. Next: mouth-interior/deformation quality and real speech alignment; do not activate the unfinished study in the game. Final animated-character quality remains the main November 10 risk; the approved playable fallback is retained. No new user decision is needed.

Verification: 255 backend tests pass (two Windows permission skips), 15 client checks, production build and all fifteen browser scenarios pass. Local app health good, paid AI disabled. Previous main CI40823323676 passed; new increment CI follows push.

## Restrained Scholar brow expressions — October 28, 2026

Added five actual brow morphs to the existing weighted rig study: inner lift, independent outer lifts and independent lowering. These derive from pinned MPFB legacy expression-unit target geometry, with source hashes recorded and deltas transferred to skin and nearby brow/hair guides. This corrects an earlier incomplete tool inventory: data/expressions is empty, but raw targets/expression/units contains usable units. It is not a supplied complete ARKit/viseme package.

Rig study now has 64 weighted joints and eight real facial controls. Manual lifts cap at 0.35 and lowering at 0.25. Reviewed an actual close-up brow-lift render. Binary checks measure nonzero displacement and confirm the three original jaw/blink deformations are unchanged; source checks locate brow motion above 1.5m and neutral/rest errors remain below one micrometre. The original static and three-control face-only studies remain intact. Game portrait/Lewis at 1.05x, interfaces and saved rooms are unchanged. No paid provider or speech connection was added.

Next: mouth interior/lip shaping and complete speech deformation, followed by actual Lewis alignment. Likeness/groom/materials still need substantial polish. The animated Scholar remains the main November 10 risk; portrait/live Lewis stays the stable playable baseline. No user decision is required for this increment.

Verification: 254 backend tests pass (two Windows permission skips), all 15 client checks, production build and all 15 browser scenarios pass. Previous CI 40817990427 is green; new source CI follows push.

## Bound Scholar development study — October 28, 2026

Bound a separate copy of the Scholar face study to the actual imported MPFB skeleton. Public GLB now contains 15 skinned meshes, one skin, 64 joints and the same three real facial morphs. Every exported vertex has normalized positive weights and valid joint references. Skin uses anatomical source weights; groom uses four-neighbour weight transfer; glasses/eyes/scalp attach rigidly to Head and wardrobe to Spine2. This intentionally avoids claiming cloth or shoulder deformation.

Measured positive/negative ten-degree head turns, combined head/jaw/blink evaluation, neutral preservation and rest restoration. A real close-up render verifies head accessories following the head. Character lab adds a separate weighted-rig choice and manual restrained head-turn control, while static and face-only studies remain available. Browser validation measures both the actual bone quaternion and a skinned spectacle vertex. No live game activation, paid provider, speech connection or saved-room change. Likeness, groom/materials, mouth interior, complete facial controls and Lewis alignment remain unfinished and the main November 10 risk. Approved portrait/Lewis +5% remains the playable baseline.

## Weighted skeleton proof and facial study — October 28, 2026

Completed a real MPFB weighted-source experiment: 64 bones, all 19,158 source vertices weighted, measured head motion and exact rest restoration. This proof remains separate from the public bust. Created an editable face study with three actual pose-derived morphs (jawOpen, eyeBlinkLeft, eyeBlinkRight), transferred to the existing head and beard without changing neutral geometry. Export contains 15 meshes, three morph names and zero skeleton joints. Binary inspection measures nonzero displacement; these are not inventory placeholders.

The separate character lab now selects the face study and exposes real sliders: jaw capped at 0.38, full blinks and reset. Reviewed close-up neutral/jaw/blink renders; eyelids close, but groom, materials, mouth interior and production deformation still need refinement. This is an early study, not the finished Scholar or a speech-connected rig. Default game portrait, Lewis at 1.05x, existing animation modes and saved-room format are untouched. Next: refine deformation quality, complete expressive/viseme controls and bind the finished bust before voice alignment. November 10 risk remains custom avatar quality; the playable portrait/Lewis fallback is preserved.

# Hourly development checkpoint — October 28, 2026

Recorded the user's November 10, 2026 integration deadline in specification/backlog/INTEGRATION_PLAN.md and the existing hourly automation. Set internal likeness/rig/integration/freeze/rehearsal gates while preserving the runnable portrait + Lewis fallback. Confirmed authoring foundation CI 40792819175 passed. Initial read-only review found a separate unmerged feature/listener branch; its transcription/privacy/schema changes require code and migration review before reuse, with no paid calls enabled.

Refined the actual Scholar blockout: opened heavy upper lids using symmetric anatomical targets, reduced added eye bags, added modest cheekbone shaping and increased beard candidates 400 to 750. Reviewed actual front/profile renders against the prior version; eyes look more alert, while the mature identity and eye placement remain. Rebuilt editable blend, GLB, configuration and inventories together. Current GLB: 4,263,452 bytes, 15 meshes, 101,835 exported vertices, 165,239 triangles, zero joints/facial morphs and no external resources. No change to game presentation or approved Lewis/+5% playback.

Verified this increment: 251 backend tests pass (two Windows permission skips), all four asset inventory checks pass, the production build passes and both focused character-workbench browser scenarios pass. Previous full main CI is green; new source CI follows this push. Main deadline risk remains the unfinished custom facial rig and production likeness/groom/materials. Pinned MPFB provides a body rig/weight definition but its shipped expression directory is empty; actual facial deformation authoring remains necessary. No new user decision is required for the settled character/voice direction.

# Latest delivery: actual Scholar anatomical blockout and authoring workbench — October 28, 2026

Prepared verified portable Blender 4.5.15 and pinned MPFB 2.0.18 source locally, without system-wide installation or paid services. Built an actual anatomical MakeHuman-based Scholar development bust with glasses, grey hair/beard guides, jacket/waistcoat/shirt/tie blocking and an embedded procedural weave tile. The editable compressed Blender scene, parametric settings, reproducible script, GLB and actual front/profile renders are checked in. Iterated visible skin/clothing intersections and reduced 736 static objects to 15 meshes.

A separate `?view=character-lab` workbench loads the real GLB beside the approved portrait, with front/profile/three-quarter/orbit inspection, measured mesh/joint/morph counts and missing/context-loss recovery. The active TV portrait/Lewis presentation and existing animation modes are unchanged; the development model has no voice or activation path.

This is a modeling foundation, not the finished premium Scholar. Current export: 3,689,448 bytes, 15 meshes, 87,772 exported vertices, 144,575 triangles, embedded texture, no external resources, zero skeleton joints and zero facial morphs. Inspection reports the missing TalkingHead inventory rather than fabricating it. Hair/scalp proxy gaps, sparse beard, heavy eyelids, exact likeness, wardrobe finish, production materials and facial rigging remain explicit next art gates. No new casting decision is needed; selected look/Lewis/+5% pace stay settled.

Verification: 251 backend tests pass (two Windows symlink privilege skips), 15 client tests pass, production build and all thirteen browser scenarios pass, including actual model loading/camera controls, no accidental speech, missing asset and graphics-context loss. Real browser front/profile inspection succeeded without page errors; model inventory measured 15 meshes/0 joints/0 morphs. Authoring bundles are excluded from project pytest discovery to preserve the normal test command. Source CI follows the push. See CHARACTER_AUTHORING.md and assets/character-production/README.md.

# Latest delivery: approved Scholar + Lewis in the playable TV — October 28, 2026

User approved The Scholar and the +5% Lewis pace. TV now defaults to the approved Scholar portrait with live Lewis narration of current public detective dialogue. Audio is muted until Enable Lewis voice; stop, mute, replay, pause/disconnect/reset and stale-state protections remain. Presentation selection preserves the original procedural stage and the existing animated sample with Windows voices. No unrelated sample is represented as the finished Scholar.

A new isolated optional neural worker reuses verified cached Kokoro assets, fixed bm_lewis generation speed 0.92 and frontend 1.05x pitch-preserving playback, exactly matching the approved audition mechanism. Authenticated requests contain an empty object, never client text. Generation is outside room locks with bounded text/output/time, single-job control, cleanup and state recheck. SAPI/core dependencies and SQLite schema are unchanged; no paid service or automatic model download is added.

Verification: 247 backend tests pass, two Windows privilege skips; all 15 client tests and production build pass. All eleven browser scenarios pass, covering selected Scholar pace/privacy/control flow, missing-runtime recovery and the preserved game/character/audition/animated modes. Actual Windows live TV Lewis opening played at 1.05x with pitch preservation enabled; host pause stopped it, no page errors and no mobile overflow. The actual full finale rendered a 41.56-second source clip in 17.09 seconds, within the 40-second deadline. Focused browser checks repeat after portrait-framing and cancellation polish.

Remaining character production: the approved portrait is static, with no fake mouth animation or claimed lip alignment. A likeness-matched deformable Scholar 3D rig is not yet made. A detailed source-verified rig brief and inspected front/profile/three-quarter construction reference are in SCHOLAR_RIG_BRIEF.md and docs/assets/. Selected look/voice/pace are settled; the next asset work is production modeling/rigging, not another casting decision.

See SCHOLAR_PERFORMANCE.md for rehearsal/setup. Source CI follows the push.

# Lewis pace refinement — October 28, 2026

User likes the selected Lewis voice and asks for slightly faster delivery. Casting now opens on Scholar + Lewis, with a 1.05x pitch-preserving playback preview by default and Original pace available for comparison. This is an explicitly labeled playback preview; source recordings and active game speech remain unchanged pending approval. Production build passed; focused casting checks verify voice-specific speed, pitch-preservation request and original-pace switching.

# Selected character and voice — October 28, 2026

User selected **The Scholar + Lewis (`bm_lewis`)**. Record this as the chosen concept/voice direction, not approval of an undelivered 3D rig or final inflection. Next milestone: a focused Lewis delivery audition with measured natural pacing and restrained dry humor, then the selected character’s production rig/activation after the applicable approval. Existing playable avatar and local Windows speech remain available.

Casting commit `ec39e04` independently passed GitHub CI run 40769768890: backend/client/build and all nine browser scenarios.

# Latest delivery: character and British voice approval audition — October 28, 2026

User requested three premium stylized-realistic detective candidates, three mature British voice candidates and restored playfully sarcastic dry humor. The separate `?view=casting` page now presents three original generated concept portraits (Classic/Modern/Scholar), George/Daniel/Lewis British male Kokoro neural recordings, three identical scene scripts, all nine face/voice pairings, captions, explicit play/stop and a device-local shortlist. The portraits are concepts, not rigged 3D avatars. The shortlist is not approval and cannot activate anything in the game.

Nine real local full-precision neural WAVs were generated at speed 0.92 using verified public model assets in an isolated optional runtime. All nine API/audio paths were inspected and decoded in the real browser, with distinct audio hashes, no clipping at PCM limits, no page errors, no external playback requests and no mobile page overflow. Performance directions are provided for approval; no precise emotion control, measured word timing or candidate lip-sync is claimed. See CASTING_APPROVAL.md for regeneration, licensing boundaries, prompts and limits.

Latest personality direction overrides the earlier serious-only choice: restrained, respectful dry humor is restored in default game narration, scripted framing, hints and approved AI remarks. Existing saved lines are preserved rather than automatically rewritten to serious text. Case facts, solution and identity remain unchanged. Working procedural/TalkingHead avatar, approved mouth/expression profile, local Windows speech and all game interfaces remain intact; no new face or neural voice replaces an active game asset.

Verification: 215 backend tests pass, with two Windows symlink privilege skips; 15 client tests and production build pass; all nine browser scenarios pass (previous seven plus casting comparison/missing-recordings). Real desktop/mobile casting screenshots were reviewed. Character, voice and inflection approval are pending; final 3D production/rigging and any activation follow that approval. Remote CI follows the source push.

# Latest direction: serious detective and case authoring — October 28, 2026

User requested a serious detective without sarcasm and asked for easier story changes. Scripted framing, all event narration, approved AI remarks and local audition lines now use a composed, factual delivery. Existing local David/Zira samples were regenerated. Known earlier authored phrases in saved narration normalize on restore; case facts, credentials and private player data are preserved. Approved restrained avatar animation is unchanged.

Case facts, suspect profiles, role cards, hints, topic aliases and case-event narration now live in the single server-only `backend/cases/blackthorn.json` package, validated at startup. Existing Python exports preserve the engine and case identity. See CASE_AUTHORING.md. This is an authoring foundation, not a multi-case selector/editor: fixed role IDs, three investigation acts and the Blackthorn visual theme remain explicit limits. Material plot edits require fresh-room rehearsal and a versioning/migration decision before use with active saves.

197 backend tests pass, with one Windows symlink privilege skip. Production build and all seven browser scenarios pass. Real Windows speech generated the new serious opening successfully (9.895 seconds). Focused animation checks are repeated after spacing the synthetic fixture transitions for slow CI runners. Previous TV performance source passed independent CI in run 40720750631 (same code as the earlier source run; the earlier run missed closely spaced synthetic mouth transitions on a slow runner; current fixtures spread word timings across the clip to improve observation without weakening assertions). Current milestone CI follows its push.

# Latest delivery: playable local TV performance — October 28, 2026

The approved TalkingHead animation now speaks the game’s current public detective dialogue in optional TV mode. The original evidence stage remains the default; one shared renderer serves both the audition and TV. Explicit enable, voice selection, stop, mute and replay are available. Pause, disconnect, revision change and navigation cancel audio and invalidate delayed responses. Identical dialogue is not repeated for unrelated room updates.

A bounded hidden Windows PowerShell subprocess uses installed David/Zira voices and the existing SAPI timing helper. The HTTP request accepts only a voice choice, not text. A derived read-only TV capability travels in the TV link fragment and Authorization header, leaving organizer control credentials separate. Generated files are temporary and responses are no-store. No database migration, microphone, paid speech provider or final detective appearance is added.

Verification: 188 backend tests pass (one Windows symlink privilege skip); 15 client tests and production build pass. Audition and new TV browser scenarios pass. Real Windows API generation and real TV playback were separately exercised: actual mouth influence 0.252, moving visemes and active upper-face expression observed; host pause stopped playback; no page errors. Screenshot reviewed in the local work folder. All seven browser regression scenarios pass. Source commit `28e8996` is pushed. [Independent CI](https://github.com/lotan11/murder-mystery-ai/actions/runs/40720061315) passed backend/client/build checks and was installing browser dependencies at handoff; remote browser completion is not yet claimed.

Try it: open the organizer, create an evening, follow its TV stage link, select Animated detective and Enable local voice. Use the host tab to advance/pause. See TV_PERFORMANCE.md for setup and limitations. Final British voice, bespoke detective rig and microphone remain future choices; existing US voices and female CC0 sample are explicitly provisional.

# Performance refinement — October 28, 2026

User accepted TalkingHead but requested smaller lip movement and more expression. Reduced final viseme strength to 45%, capped at 0.38; added subtle speech-weighted upper-face acting and modest head motion. Playback completion now waits until speech has actually begun, addressing a race exposed by prior remote CI. Synthetic browser recordings last at least eight seconds so slow CI can test interruption during playback. Real local Windows samples remain unchanged. Production build and all six browser flows passed; live Windows playback observed mouth influence 0.209 with upper-face expression active. Screenshot reviewed. Latest audition checks rerun after generation-reset guard.

# Latest delivery: TalkingHead audition — October 28, 2026

Separate local audition at `/?view=audition` now compares actual installed David/Zira speech on the CC0 TalkingHead sample. Real SAPI starts drive actual facial morphs; durations are estimated. Windows browser review observed mouth movement and stop reset with no external requests or page errors. The female sample is not final Wobblebottom; no premium voice, microphone or live game speech integration is claimed. See VOICE_AUDITION.md for Windows preparation.

Local verification: 157 backend tests passed, one Windows symlink privilege skip; 15 client tests and production build passed. All six browser scenarios passed, covering the existing game and new audition. Remote CI follows the source push.

# Project progress and handoff

Updated October 27, 2026. Authoritative handoff for the integrated repository. Read SPECIFICATION.md, TASK_BOARD.md, DECISIONS.md, AI_INTEGRATION.md and the spoiler-marked GAME_DESIGN.md.

## Current delivery: M3 — optional grounded AI planning

**Software foundation accepted and pushed to main.** Source commit `2485145` passes local tests and [independent GitHub CI](https://github.com/lotan11/murder-mystery-ai/actions/runs/40607478899). The acceptance-record commit changes documentation only. Live provider/account/model operation is not claimed tested or enabled. The application continues to run in free scripted mode by default.

Delivered in the existing application:

- Optional OpenAI Responses adapter accepts only a structured selection of released clue IDs plus an approved Wobblebottom remark. The server renders authored factual text; arbitrary model-written prose is not accepted.
- Provider requests exclude private cards, roster, introductions, accusation reasons, credentials and hidden case facts. Only the typed question and released evidence are sent.
- Provider mode, paid consent, local key and explicit model are all required. No default paid model, automatic paid calls or retries.
- Durable per-room request allowance, default five attempts. Reservations save before dispatch; reset/restart do not replenish attempts.
- Tracked background requests run outside the room lock. Same-socket host controls remain responsive; stale answers are discarded after room changes.
- Timeouts, refusal, provider errors, malformed plans and exhausted allowance use safe scripted behavior. Raw diagnostics and credentials never become UI messages.
- Actual-source, busy, fallback, configuration and usage indicators appear in host/guest views. Configured provider use is disclosed before questions are submitted.
- SQLite schema 3 migrates schemas 1 and 2 atomically; source/reason and attempt counters persist.
- Windows launcher accepts an explicit environment file. `.env.example` stays offline by default; real environment files remain ignored.

## Verification

- 134 backend tests pass: previous game/privacy/migration tests plus 52 mocked adapter tests and 25 orchestration cases.
- 15 client tests and production build pass. [GitHub CI](https://github.com/lotan11/murder-mystery-ai/actions/runs/40607478899) independently passes all backend, client, build and browser checks.
- Four browser scenarios pass: full host/TV/phone case, four-guest role privacy/introductions/rationales, renderer failure and explicit scripted-default status.
- A real Windows launch with `-EnvFile .\.env.example` migrated schema-2 saves to schema 3; every previous public-state field and host access were preserved. Health confirms paid AI disabled and React returns HTTP 200.
- All automated tests force offline defaults and forbid real outbound HTTP. The integration is tested with injected transports/fake planners, not a live account.

## How to test now

Refresh the existing preview or follow README/start.ps1, create an evening and play as before. The host integration panel identifies the actual reply source and provider state. Nothing needs an API key to rehearse. Private characters, clues, votes, introductions and saved games remain available.

For deliberate optional live assistance, follow AI_INTEGRATION.md and configure a local key, compatible explicit model and paid consent, then restart with the selected environment file. A real provider smoke test and human dinner rehearsal remain manual acceptance steps, separate from the completed software checks.

## Next work

1. Human rehearsal: pacing, clue comprehension, role comfort and real phone/TV readability. Log observed issues in TASK_BOARD.md.
2. Optional live-provider smoke test only after the user configures account/model/spend locally; record exact model and observed fallback behavior without recording credentials.
3. M4: consented microphone/transcription and custom voice/rigged avatar/lip sync remain separate features. No microphone access is implemented by the model planner.
4. Free-form model-written dialogue, if desired later, requires a stronger factual validation design rather than silently widening this bounded adapter.

## Current limits and blockers

No blocker prevents the scripted game. Live AI use requires explicit local configuration and account/model access; no paid invocation has been performed. Model assistance selects authored facts and remarks rather than inventing natural-language case testimony. Device speech remains optional; microphone, custom voice, rigged avatar, lip sync and public hosting remain absent. SQLite supports one backend process. Request allowance is per room and is not a dollar or account-wide budget.

## Accepted history and continuity

M1 source e27ab9a established durable Blackthorn rehearsal. M2 source 091aa6b added private characters and four-guest participation; CI run 40604506205 passed, and documentation head 5cc18a2 also passed. M3 extends that single application and preserves case version 1 because the murder facts/solution are unchanged.

Inspect Git status, branches/PRs and CI before continuing. Keep one file owner per parallel stream, integrate tests, update these documents and commit accepted increments. No scheduled background work is configured.

Final local verification: all three character-lab browser scenarios pass after the assertion correction; thirteen existing browser scenarios passed in the full run. Backend 252 pass/2 Windows skips, client 15 pass, build pass. New push CI pending; preceding main run 40800185053 passed.

Final local verification for the bound study: 253 backend tests pass (two Windows permission skips), 15 client checks pass, production build and all fifteen browser scenarios pass. Live local app health is good with scripted dialogue and paid AI disabled. Previous main CI 40812785651 passed; new increment CI follows push.

CI portability correction: run40850873555 found a raw source-hash mismatch between Windows CRLF and Linux LF. Evidence now retains the raw observed hash and adds canonical JSON content SHA256 for cross-platform fact validation; an LF/CRLF and changed-content regression check protects the distinction. No game/voice/geometry change.

## October 29, 2026 — crown coverage and face review framing

Completed during this scheduled run: repaired visible scalp-cap holes in the isolated weighted Scholar study, retaining original anatomy, cap topology/material,64bones/11controls and existing skin/facial-groom assets. Actual before/after front/profile renders show coverage improvement. Cap-only anatomical weights follow restrained head motion. Smooth-normal checks are positive;27/28 raw triangle sign disagreements near ears remain recorded and unresolved. Helmet hairline, coarse strands and premium likeness remain unfinished. Added geometry-based Face close-up/Full bust with actual crown/chin visibility, desktop/phone fitting and preserved orbit direction; Reset/model change restores full bust.

Validation:314backend tests pass,3Windows permission skips;21client checks pass; production build and all20browser scenarios pass, including complete synchronized case, private roles, speech/pause/cancellation and framing.13actual asset tests pass. Actual8018 browser playback confirms1.05 pace, pitch preserved, advancing source clock, Stop removes audio and zero page errors; reviewed actual exported close-up. GLB13,266,176bytes,119,835vertices/177,239triangles,64joints/11controls, no external resources.

Previous code CI40916235913 passed; this increment's remote CI pending push. No paid calls, purchase, public deployment, new casting choice or saved-room change. No claim of development between scheduled runs. Next: coherent silver hair silhouette, portrait-matched facial proportions/eyes/tailoring and perceived speech review. Custom-avatar readiness remains the main November10 risk; preserve November4 gate and approved portrait/liveLewis game fallback.

Remote verification: code commit `15f8f5f` passed CI run `40951937765`, including all20browser scenarios. This closes the crown/framing increment; the custom character remains a development study and the portrait/liveLewis fallback stays active.

## October 29 evening — listener review after user question

During this scheduled run, reviewed unmerged listener1f8bab0 and ran an isolated branch snapshot:252backend tests pass/2Windows skips, including5listener tests. Added explicit offline probes:4expected failures reproduce stale transcripts after Stop/reset, fabricated cross-clause claims and unbounded theory links;1schema3migration round-trip passes. Frontend original-function VM/fake-device Chromium reproduces late microphone activation, broken Resume and non-independent WebM fragments. Code inspection also finds16KiB transport mismatch, dropped error state and Lewis narration interruption. Recorded prioritized findings, acceptance order and reproducible scripts in LISTENER_REVIEW.md.

No listener merge, paid calls, actual microphone capture, room migration, public deployment or avatar change. No development is claimed between scheduled runs. Last product CI40951937765 is green (314backend/3Windows skips,21client,20browser/build locally). Next: return to Scholar grooming/likeness, preserving portrait/liveLewis. Listener remains blocked pending repairs rather than silently importing unsafe code. Custom-avatar visual/perceived-speech quality remains the November10 risk; November4 gate unchanged.

Main regression rerun after adding review tooling:314backend tests pass,3Windows permission skips. Frontend probe rerun succeeds using synthetic capture; the pinned branch acceptance probes intentionally remain4fail/1pass. New review increment CI follows push.

PR2 review: isolated7b2b918 passes367backend+review checks/3Windows skips,24client/build; runtime unchanged at91b08e3 test-only update. Found null-attribution snapshot rejection, same-act lobby Reset capture gap, stale confirmation after Resume and overwritten errors. See reviews/PR2_INTEGRATION_REVIEW.md. Main CI40980550600 green; no merge or paid/live microphone call. Browser/PR CI result follows.

Final local result: all22browser scenarios pass (2.5minutes), including synchronized host/guest/TV, private roles, audio transport and Lewis continuity. Re-ran backend+5review probes and24client checks with the91b08e3 test-only delta:367pass/3Windows skips and24pass. Build/runtime bytes are unchanged from tested7b2b918. PR CI remains running at review close. Findings1–4 remain applicable; no merge approval.

## Follow-up: d160344 nullable attribution fix

Reviewed `d16034465ae8fe0da00405a0337c6ad135826ab3`. Finding1 is resolved in the client contract: null attribution is accepted only with the fixed Unattributed audio label and no follow-up-answer attribution. All25client checks and production build pass locally. The original null-snapshot reproduction now accepts the legitimate record; a null record falsely claiming a follow-up answer is rejected. Backend/runtime outside this decoder is unchanged. No repeated full-browser claim: previous reviewer run22pass was before this decoder change; author reports22pass on8011, and d160344 CI is running.

Findings2–4 remain: same-act lobby Reset capture cleanup (P1), stale confirmation after Resume (P2), and overwritten actionable error status (P2). App.tsx is unchanged by d160344. PR2 remains unmerged and not approved.

## Follow-up: 0b2e809 remaining review fixes

Reviewed pinned head `0b2e809b91bdd98b09464711121eb6e69a2570bf`, including fixes in `ccef65e`. Main is an ancestor of this snapshot; authored case and approved portrait/voice/avatar assets are unchanged. Scoped review clears the remaining reported defects: a guest-only explicit reset signal cancels capture/pending permission in lobby-to-lobby reset; new consented start/Resume clears stale confirmation; terminal error text survives cleanup and stopped acknowledgements. Nullable-speaker contract fix remains. No further concrete blocker found in this diff.

Independent local checks:365backend tests plus5explicit review probes pass (370total),3Windows permission skips;25client checks and production build pass. Saved-room tests cover progress/votes/credentials recovery, rollback and schema3migration. Full24browser scenarios and PR CI are still running at this checkpoint; final result follows. No paid calls, real microphone use, live database migration or merge. Reviewer browser capture uses synthetic devices and an isolated server on8022.

Final independent local result for0b2e809: **365backend +5review probes pass (370total),3Windows permission skips;25client checks; production build; all24browser scenarios pass (2.6minutes).** This includes saved-game restart/migration, host/guest/TV case completion, role privacy, real local Lewis continuity, synthetic-microphone reset/Resume/error regressions and real local WebSocket audio-frame validation. All previously reported PR2 findings are cleared in this reviewed scope; no additional concrete blocker found. PR CI is still completing browser checks, so remote readiness is pending. PR remains unmerged. Actual-device and authorized live-provider testing remain separate acceptance steps.

Remote verification complete for exact head0b2e809: both CI runs `40996214412` and `40996209236` succeeded, including the24browser scenarios. Combined local and remote checks now pass; no remaining blocker from the recorded review findings. PR2 is still unmerged, with no live-room migration or paid-provider/device acceptance implied.

## October29 late scheduled run — restrained iris detail

Added supported project-authored512px slate-grey radial iris albedo to the separate Scholar weighted study, with explicitUV1 and preservedUV0. Actual front/profile previews reviewed; the model reads less uniformly cyan. No eye/pupil/sclera/head anatomy change, new geometry/bones/morphs, gaze/corneal reconstruction or final likeness claim. Fullbuilder and pose/rest checks pass. GLB13,424,544bytes; geometry unchanged119,835vertices/177,239triangles,64joints/11controls; five embedded images, with original skin maps untouched. Source irisPNG hash matches actual GLB image.

Validation on authoritative main:315backend tests pass/3Windows permission skips;14actual asset checks pass;21client checks, production build and all20browser scenarios pass. New eye comparison uses world-space positions because skeletal binding bakes static node translations; two-micrometre export tolerance. Browser confirms actual512x512 sRGB iris texture onUV1 and3skin maps, not a model-mode label. Actual8018 Lewis playback remains1.05 with pitch preserved, source clock advances, peak restrained mouth motion0.24, Stop removes audio and returns neutral, zero page errors. Observed screenshot reviewed; this is still an unfinished mannequin-like development study. Windows Proactor connection-reset teardown logs appeared without failed scenarios.

Since the previous scheduled report, PR2 fixes at0b2e809 also cleared independent370backend/review,25client/build,24browser checks and both remoteCI runs; PR remains unmerged. This scheduled run returned to avatar material work. No unattended development is implied, no paid calls/assets/public deployment or live-room migration. Game portrait/liveLewis and saved rooms remain protected. Current increment CI follows push; prior main CI40980550600 green. Next P0: coherent silver hair silhouette and portrait-matched face, followed by eyes/lids/tailoring/oral and perceived speech quality. November4 gate and November10 risk remain; portrait/Lewis is the stable playable baseline.

Remote verification: iris-material code commit `fedda03` passed CI `41004279027`, including all20browser scenarios. Local315backend/3Windows skips,21client/build and actual8018 iris/Lewis checks remain verified. Development rig only; no finished likeness or final gaze/viseme claim.

## October30 scheduled run — hair gate and portrait comparison

During this run, built and visually reviewed two rounded/tapered crown-clump experiments. Both rejected for public integration: helmet hairline and exposed side/back loops remained, despite valid normalized existing Head weights and neutral/±10degree attachment checks. No new hair, model, canonical source, builder, case or voice was shipped. Active publicGLB is byte-identical to preceding main; hash/rejection evidence and front/profile renders recorded under reviews/HAIR_REFINEMENT_REVIEW.md. Experimental source archived locally under ignored data/character-tools/hair-experiment. No claim of work between scheduled runs.

Delivered display-only approved-portrait head crop synchronized to Faceclose-up in the isolatedlab. Sameoriginal1145×1374PNG; completehair/ears/chin/collar in SVGregion, letterboxed on phones. Fullbust/Reset/modelchange restores originalimage. Actual desktop/phone screenshots reviewed; test now waits real post-resize render instead of accepting stale camera diagnostics.

Validation:315backend tests pass/3Windows permission skips;21client checks and productionbuild pass; all20browser scenarios pass (2.3minutes), including private roles, synchronized host/guest/TV, approvedLewis playback, interruption and crop/restoration. Existing publicrig/skin/iris/groom controls remain intact. Lastmain CI41004279027 green; newincrement CI follows push.

Next: visually assess existing swept-hair geometry/material, inspect individual source/license/hash, then fit/export/attachment-test before reuse. Official MakeHuman inventory leads recorded with primary links; no hairasset downloaded, paidcall/purchase/publicdeployment/live-room migration. PR2 remains reviewed/green/unmerged. Premiumcustomavatar visualquality remains the November10 risk; November4gate and playableportrait/liveLewis baseline preserved. No user decision required for this bounded experiment.
