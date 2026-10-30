# Validation results

## M3 local integration — October 27, 2026

| Check | Result |
| --- | --- |
| Backend | 134 passed, including 52 mocked Responses adapter cases and 25 async orchestration cases |
| Client | 15 passed, including actual-source/busy/usage metadata and safe diagnostic copy |
| TypeScript + build | Passed |
| Browser | 4 passed: private characters, scripted-default status, renderer recovery and complete synchronized case |
| Windows launcher/upgrade | Passed with explicit environment file; prior public state and host access preserved, schema 3 restored, paid AI disabled, frontend HTTP 200 |
| Remote CI | Passed on source `2485145`: [GitHub run](https://github.com/lotan11/murder-mystery-ai/actions/runs/40607478899) |
| Actual live model | Not invoked or verified; no paid requests made |

Tests cover strict request/output shape, data minimization, invented/unreleased facts, duplicate keys, malformed/refused/incomplete output, provider failure/timeout, durable reservation, reset/restart, budget exhaustion, storage failure, responsive same-socket pause, stale-result discard, concurrency and shutdown cancellation. Backend tests deny real outbound HTTP; browser-server settings force paid mode off. Live account/model compatibility, billing, actual speech and human playtesting are not inferred from mocks.

## M2 local integration — October 27, 2026

| Check | Result |
| --- | --- |
| Backend | 57 passed: includes private delivery, spoofing/access checks, character design, migration/recovery, rollback and unchanged case grounding |
| Client | 12 passed: includes separate private decoder, malformed private payloads and final-only public rationale validation |
| TypeScript + production build | Passed |
| Browser | 3 passed: four independent guests with reassignment/introductions/private reasons, full original case and renderer failure recovery |
| Windows upgrade | Passed on real existing schema-1 saves: atomic migration to schema 2, progress/party/credentials preserved and frontend HTTP 200 |
| Remote CI | Passed on source `091aa6b`: [GitHub run](https://github.com/lotan11/murder-mystery-ai/actions/runs/40604506205) |

The four-guest browser scenario inspects actual received WebSocket packets, checks that only the authenticated owner receives their private data, confirms host/TV receive none, and exercises concealed briefs, host reassignment, public introductions, reconnect and finale disclosure. Four phone-sized viewports have no horizontal overflow. Store tests validate additive migration and failure preservation. No paid AI/audio service was invoked.

Human dinner playtesting, real phone/TV readability and actor comfort remain unverified. Automated character roleplay does not count as a human rehearsal. Introductions are intentionally public after submission; accusation reasons become public only at resolution.

## M1 local integration — October 27, 2026

| Check | Result |
| --- | --- |
| Backend | 37 passed: engine, identity/access separation, malformed input, store recovery/failures/corruption/version pins, story grounding and bounded dialogue |
| Client | 9 passed: transport, error handling, snapshot validation and available-clue metadata |
| TypeScript + Vite build | Passed |
| Browser | 2 passed: full host/TV/phone case and WebGL context-loss fallback; includes real host gating, restored guest identity and no hidden guest canvas |
| Windows process restart | Passed: saved act, evidence and pause checkpoint matched after restarting `start.ps1`; host credential authorized resume; React HTTP 200 |
| Remote CI | Passed on source commit `e27ab9a`: [GitHub run](https://github.com/lotan11/murder-mystery-ai/actions/runs/40600489863); historical timeouts resolved |

Browser checks use real HTTP/WebSockets and isolated SQLite files, serial scenarios, retained failure traces and a bounded 90-second full-case allowance. They assert real host gating and that no avatar canvas is mounted on the guest view. No paid provider, microphone or speech service is used in automated tests.

A first manual restart comparison during integration observed the newly added public clue `summary` field because the story stream was still editing canon. After all component edits were frozen, the exact public snapshot comparison across a real server restart passed. No game progress or credentials were lost.

Known non-failing tooling messages: Vite reports the combined Three.js/React bundle size, and Starlette warns about its HTTPX test helper. Actual devices, physical TV readability, human dinner pacing, external AI, real audio capture and lip sync remain unverified.

## Historical M0 verification

Verified October 27, 2026 on Windows with Python 3.13 and Node 20.10 (setup recommends a maintained newer Node release).

| Check | Result |
| --- | --- |
| Windows launcher | `start.ps1 -SkipSetup -Port 8002` started successfully; health and built React page returned HTTP 200 |
| Backend pytest | 4 passed: full case gates/reset/spoiler protection; role permissions and restored guest identity; multiclient pause/votes/reconnect; malformed input recovery |
| Frontend client tests | 4 passed: secure URL credential encoding, malformed message recovery, server errors, unknown event handling |
| TypeScript and production build | Passed |
| Playwright full-case browser flow | Passed after final layout changes; organizer, 1920×1080 TV, and 390×844 phone viewport in independent browser contexts |
| Browser runtime errors | None in the full-case test |
| Phone horizontal overflow | None in tested viewport |
| npm audit in frontend | 0 reported vulnerabilities at verification time |
| Visual inspection | TV and phone screenshots reviewed; TV fitted to viewport, phone controls prioritized |

The browser flow covers create → guest join → start → reveal → question → pause/resume → all three acts → guest reload/identity restore → accusation → final solution → TV reload. Tests use real local HTTP/WebSocket communication, not a mocked transport. Backend tests additionally check spoiler withholding and unauthorized control rejection.

Known non-failing tooling messages: Vite warns about the roughly 721 KB uncompressed combined Three.js/React bundle; Starlette emits an HTTPX test-helper deprecation warning. Neither prevented builds or tests.

Not verified: physical TV readability, actual phones over Wi-Fi, device speech quality, cross-browser compatibility, production hosting/load, external AI, audio capture, rigged animation or lip sync. Those integrations are absent or explicitly labeled in the UI.

Repository integration: tests were rerun from the cloned `murder-mystery-ai` repository with FastAPI 0.162.0 and Uvicorn 0.54.0 in its own virtual environment. Playwright starts an isolated backend on port 8001. A Windows socket-reset callback was printed during browser teardown after assertions passed; it did not affect the case flow. GitHub Actions is configured but its remote run is separate from local validation.

## Follow-up verification of the first runnable prototype

Inspected remote `main` at `92b5396` before changes. The requested FastAPI, React host/guest, WebSocket synchronization, procedural detective, tests, and Windows launcher were already present. Preserved that implementation and the earlier standalone local branch.

Fixed malformed credentials and binary WebSocket recovery, incomplete frontend snapshot/error validation, and WebGL context-loss fallback, with regression tests.

Fresh verification on October 27, 2026: 7 backend tests, 7 frontend client tests, production build, and the full organizer/TV/phone guest browser flow passed. Windows launcher started on port 8017 with health and built React returning HTTP 200. Port 8002 was occupied and correctly reported a conflict. Frontend npm audit reported zero known vulnerabilities. AI is scripted; browser speech remains opt-in. No paid provider was invoked.

The added browser regression for WebGL context loss also passed; captions and evidence remain available after renderer failure.

## TalkingHead audition — October 28, 2026

157 backend tests passed, one Windows symlink privilege skip; 15 client tests passed; production build passed; all six browser scenarios passed. Actual SAPI Windows playback reviewed separately from clearly labeled synthetic browser fixtures: real mesh motion and stop reset observed, no page errors or external requests. Existing full case and privacy flows remain green. Premium voice quality and final detective asset remain untested/unselected.

## Local TV performance — October 28, 2026

188 backend tests pass; one Windows symlink privilege skip. Fifteen client tests and production build pass. New TV browser scenario verifies opt-in, actual mesh motion, pause, replay and mute across real WebSocket host changes; browser audio fixture is a synthetic tone. Shared audition regression passes. Real Windows SAPI generation and TV WAV playback are checked separately: actual moving visemes, restrained peak 0.252, expression weight 0.913, host pause stopped audio, no page errors. Public-only speech, scoped authorization, malformed bodies, stale state, timeouts, cancellation and output bounds are tested with injected renderers. Premium voice realism, final character art and physical TV/phone dinner rehearsal remain manual acceptance work.

Full integrated regression: all seven browser scenarios pass, including complete host/TV/guest case and private-character flow. No paid integration was invoked.

## Serious tone and case package — October 28, 2026

197 backend tests pass, one Windows symlink privilege skip. Production build and all seven browser scenarios pass, including the complete case, private-character flow, audition and TV speech interruption. Nine new package checks cover authoritative exports, malformed structural content/duplicates and known saved-tone conversion. Windows audition samples were regenerated and validated against the new neutral authored lines. Actual Windows TV speech generated the new serious welcome (9895 ms). No facts, solution or case identity changed. Synthetic word timings are spread across the clip so low-frame-rate CI can observe actual morph transitions without weakening motion assertions.

## Wobblebottom casting — October 28, 2026

215 backend tests pass, two Windows symlink privilege skips. All 15 client tests and production build pass. All nine browser scenarios pass: existing complete-case/private-role/TV/audition coverage plus all nine portrait/voice combinations with selection cancellation, no autoplay, captions, persistent shortlist and missing-recordings behavior. Browser test audio is an explicitly mocked waveform; separately all nine actual locally generated British neural clips played and decoded via the real server, with distinct hashes and no PCM clipping, page errors or external requests. Real desktop/mobile screenshots reviewed and no horizontal page overflow observed. Portrait framing adjusted to retain the full head. Concept portraits have no rig or simulated mouth animation. Perceived maturity, voice quality, inflection and final character selection remain human approval items.

## Approved Scholar live performance — October 28, 2026

247 backend tests pass, two Windows symlink privilege skips. Fifteen client tests and production build pass. All eleven browser scenarios pass, including Scholar current-public-line playback, exact 1.05 pace/pitch request, pause/mute/replay, missing optional runtime and explicit original-stage recovery. Existing complete case/private-role/animated sample/audition coverage remains. Real Windows TV decoded and played Lewis opening at 1.05x with pitch preservation enabled; pause stopped it; no page errors/mobile page overflow. Full authored finale generated in 17.09 seconds (41.56-second source WAV), within the 40-second limit. Browser automated audio fixtures remain synthetic waveforms; real audio was checked separately. Custom Scholar rig/likeness deformation and lip-sync remain undelivered, not claimed from static imagery.

## Actual Scholar authoring blockout — October 28, 2026

251 backend tests pass, two Windows symlink privilege skips. Fifteen client tests, production build and thirteen browser scenarios pass. New asset tests inspect actual embedded GLB geometry and distinguish the existing sample's missing silence target from full rig approval; malformed containers are rejected. Browser workbench loads 15 actual meshes, reports zero joints/morphs, handles camera presets/missing model/context loss and makes no speech requests. Real front/profile browser views and Blender renders inspected; clothing intersections fixed and static meshes merged from 736 to 15. The development model is not deployed in the game. Exact likeness, final groom/material quality, rigging and speech deformation remain unpassed art gates. No finished avatar quality is inferred from file loading or structural counts.

## October 28 hourly refinement checkpoint

Reviewed rebuilt front/profile render after symmetric eye-height/fold and eye-bag changes; eyes are more open while age, placement and approved reference remain stable. Denser beard remains a development proxy. GLB inspection: 15 meshes, 101835 exported vertices,165239 triangles, 4263452 bytes, zero joints/morphs and no external resources. This increment passes 251 backend tests (two Windows privilege skips), four asset checks, production build and both workbench browser scenarios including failure recovery. The live game health endpoint remains good. Previous full CI run 40792819175 passed; the new source run is checked after push. No rig/deformation gate is marked complete.

## October 28 weighted source and face study

252 backend tests pass, two Windows symlink privilege skips; 15 client checks and production build pass. All thirteen existing browser scenarios pass. The new face-control scenario initially failed solely on expected numeric attribute formatting (0.38 versus 0.380); corrected assertion and focused rerun recorded below after completion. Binary GLB inspection confirms actual nonzero jaw and eyelid deltas, 15 meshes/3 morph names/0 exported joints/no external resources. Source proof measures real head movement, full source weights and exact rest restoration. Visual review confirms closed eyelids in the blink render; hair, materials, mouth interior and complete deformation remain unfinished. No paid providers invoked.

Final local verification: all three character-lab browser scenarios pass after the assertion correction; thirteen existing browser scenarios passed in the full run. Backend 252 pass/2 Windows skips, client 15 pass, build pass. New push CI pending; preceding main run 40800185053 passed.

## October 28 bound bust checkpoint

253 backend tests pass with two Windows symlink privilege skips; 15 client checks and production build pass. Four focused character-lab browser scenarios pass, including measured movement of an actual skinned spectacle vertex, plus/minus ten-degree bone rotation and reset. Binary export test checks every mesh vertex has normalized weights and valid joint references; 15 meshes, one skin, 64 joints and three nonzero morphs. Blender checks neutral preservation/restoration within 0.000001m, fixed wardrobe under head turn and finite combined head/jaw/blink pose. Actual head-turn render visually inspected. Full browser regression and new push CI recorded after completion; preceding main CI 40812785651 is green. No paid calls.

Final local verification for the bound study: 253 backend tests pass (two Windows permission skips), 15 client checks pass, production build and all fifteen browser scenarios pass. Live local app health is good with scripted dialogue and paid AI disabled. Previous main CI 40812785651 passed; new increment CI follows push.

## October 28 brow expression increment

254 backend tests pass, two Windows symlink privilege skips. Production build, 15 client checks and four focused character-lab browser scenarios pass. New checks measure actual five-target deltas, source upper-face localization, skin/groom coverage, unchanged jaw/blink deformations and neutral/rest preservation. Browser exercises all five actual influences at their caps and resets. Reviewed the actual brow-lift render; appearance remains a development blockout. Source target hashes recorded; no paid calls or live game presentation changes. Previous main CI 40817990427 passed. Full browser regression and new source CI are recorded after completion.

Full regression completed: all fifteen browser scenarios pass, alongside backend254/client15/build. New increment CI follows push.

## October 29 mouth units

255 backend tests pass, two Windows symlink privilege skips. New binary checks measure nonzero mouth displacements, restrained preview limits, localized source motion and distinct target hashes. All eight prior displacement inventories compared equal against HEAD before this increment. Reviewed actual rounding/compression/slight-smile renders; no finished speech or interior claim. Previous main CI40823323676 passed. Frontend/browser results follow after completion.

During the full Windows browser run, the test server logged Proactor connection-reset callbacks as clients disconnected; affected guest/full-case scenarios still passed. This is a teardown-log observation, not a new application exception-handler suppression or an assertion of failure-free logs.

Final mouth-increment regression: all fifteen browser scenarios pass, production build and client15 pass; backend255 pass/two skips. New push CI follows.

## October29 CI performance correction and timing probe

Prior CI40829947023 failed only the90s rig browser budget (fourteen others passed). Root cause was unnecessary continuous drawing of the static dense model. New actual render-count tests prove idle settling and camera/pose redraw; no timeout relaxation.264 backend tests pass/two Windows skips, client15/build pass, all15 browser scenarios pass locally (rig5.7s). Optional real local timing probe:73 model spans/5.502s, same-inference audio object and PCM unchanged. Rejects empty, nonfinite, overlapping, out-of-range or extra-field timing data. Live voice worker untouched; no paid calls. New source CI follows push.

Hosted CI confirmation: run40836345515 passes for code commit7385b78. All browser scenarios pass without timeout relaxation; prior40829947023 rig timeout resolved.

## October29 first timed speech study

291 backend tests pass/three Windows permission skips,21 client checks pass. Optional realworker smoke accepted5.502s/73cues from bm_lewis at unchangedpace. Client tests verify exact clip hash/duration, sourceclock, gaps, soft/capped poses and malformed data rejection. Backend tests verify strict sidecar limits, exact sample-clock reconstruction, Unicode/surrogate rejection, legacy compatibility, projection/auth/stale protections. Reviewed actual timed-model screenshot; blockout quality remains explicit. Build/eight focusedlab scenarios pass, including realusergestureaudio1.05, actualmorph motion, missingmetadata/hashmismatch, cancellation/latefetch/hidden/contextloss/modelchange. Full browser regression follows; no paid calls/downloads.

Final local regression: all19 browser scenarios pass,291 backend tests pass/three Windows permission skips,21 client checks and production build pass. Actual fixed-study screenshot reviewed locally; routine CI retains failure screenshots. Hosted CI follows push.

Hosted CI40843961780 passes for code commit5a7ccca, including all19 browser scenarios. The timed lab study and existing playable game regression are green.

## October29 oral lining and longer narration

293 backend tests pass/three Windows permission skips,21 client checks, production build and all19 browser scenarios pass. Material test verifies the existing weighted cavity primitive, anatomical mask bounds and unchanged vertices/triangles plus jaw/blink displacement magnitude/count. Extra primitive reflects material separation only. Actual mouth-lining open-jaw render reviewed. Realworker59-word public narration:25.0606s/391cues, zerooverlap/outofbounds,21.096s observedgeneration under40s budget; source/hash/public-fields recorded. One sample is not maximum-length or perceptual/performance certification. Windows testserver still emits known Proactor socket-close logs during disconnection scenarios; scenarios pass. New source CI follows push.

CI portability correction: run40850873555 found a raw source-hash mismatch between Windows CRLF and Linux LF. Evidence now retains the raw observed hash and adds canonical JSON content SHA256 for cross-platform fact validation; an LF/CRLF and changed-content regression check protects the distinction. No game/voice/geometry change.

After portability correction:294 backend tests pass/three Windows permission skips. The application/asset code is unchanged from the passing21client/build/19browser local run. New CI follows the evidence-hash fix.

Hosted CI40851331046 passes for corrected code commitaf0d1a8, including backend/client/build/all19 browser scenarios. Prior40850873555 evidence-hash failure resolved without changing game/voice behavior.

## October29 bounded speech cache

310 backend tests pass/three Windows permission skips,21 client checks/build/all19 browser scenarios pass. Tests cover successful repeatedworker avoidance, pairedtiming/audio identity, freshcopies, exact UTF8payload budget, count/LRU/TTL, unavailable/textchecks beforelookup, warmhits duringothercoldgeneration, oversized/error/timeout/cancellation nonretention, cachefaultfallback and unchanged auth/pause/currentrevision/staleprojection. Realprobe:59publicwords,391cues/25.06s,12.107123s initialcachemiss/0.005724s immediatehit,oneworker,1,630,999retainedbytes and no generationfiles left. Local observation only; misses stillcold. Artreview documentsactualmissing skinmaps and remaininglikeness/groom/wardrobe/oral quality. New source CI follows push.

Hosted CI40859619619 passes for source commitb17ee59, including new cache boundaries and all19 browser regressions.

## October29 baked runtime skin maps

311 backend tests pass/three Windows permission skips,21 client checks/build/all19 browser scenarios pass. Actual1K Cycles color-only/roughness/normal bakes, bump-disablednormalbaselineRMSXY0.009305 over259045 coveredpixels. Embeddednormal/basecolorSHA matchsourcePNGbytes; inspectorverifies actualskin base/normal/ORM references andfour embeddedimages. Browsermaterialcheckcountsthree decoded1Ktextures(static/face-onlyzero). Actualbrowsercloseup+openjawrender reviewed: subtlegrain only, no finishedskin/groom/likeness claim. Geometry101835vertices/165239triangles,64joints/11targets preserved; oral material andapprovedspeech intact. New source CI follows push.

Hosted CI40867962436 passes for source commit5659c0e, including actual texture-binding checks and all19 browser scenarios.

## October29 fitted facial groom

313 backend tests pass/three Windows permission skips,21 client checks/build/all19 browser scenarios pass. Newexportcomponent checks preserve originalhead pointcloud/triangles/rest mouth-blink delta counts/magnitudes acrossmaterial splits while validating intentionalgroomaddition(18kverts/12ktris/4nonzero mouthtargets). Allverticesnormalized/validboneindices; zerooutwardfaceinversions, fiveindividualposeattachmentchecks0inwardpoints, weight/morphcorrespondenceerrorsunder1e-6, restlipproxygap2mm. Actualbrowser8018 confirms19primitives/64joints/11controls/3maps,1.05pitch-preservedLewis, visiblemouthmotion andStopneutral/noaudio. No pageerrors orroomAPIcalls. Screenshotreviewnotescoarse/unevendensity; no finalhair orphoneme-accuracy certification. Crownexperimentrejectedandnotexported. New source CI follows push.

Hosted CI40916235913 passes for source commita4888d6, including genuine fitted-groom/component checks and all19 browser scenarios.

## October 29, 2026 — crown coverage and face review framing

Completed during this scheduled run: repaired visible scalp-cap holes in the isolated weighted Scholar study, retaining original anatomy, cap topology/material,64bones/11controls and existing skin/facial-groom assets. Actual before/after front/profile renders show coverage improvement. Cap-only anatomical weights follow restrained head motion. Smooth-normal checks are positive;27/28 raw triangle sign disagreements near ears remain recorded and unresolved. Helmet hairline, coarse strands and premium likeness remain unfinished. Added geometry-based Face close-up/Full bust with actual crown/chin visibility, desktop/phone fitting and preserved orbit direction; Reset/model change restores full bust.

Validation:314backend tests pass,3Windows permission skips;21client checks pass; production build and all20browser scenarios pass, including complete synchronized case, private roles, speech/pause/cancellation and framing.13actual asset tests pass. Actual8018 browser playback confirms1.05 pace, pitch preserved, advancing source clock, Stop removes audio and zero page errors; reviewed actual exported close-up. GLB13,266,176bytes,119,835vertices/177,239triangles,64joints/11controls, no external resources.

Previous code CI40916235913 passed; this increment's remote CI pending push. No paid calls, purchase, public deployment, new casting choice or saved-room change. No claim of development between scheduled runs. Next: coherent silver hair silhouette, portrait-matched facial proportions/eyes/tailoring and perceived speech review. Custom-avatar readiness remains the main November10 risk; preserve November4 gate and approved portrait/liveLewis game fallback.

Remote verification: code commit `15f8f5f` passed CI run `40951937765`, including all20browser scenarios. This closes the crown/framing increment; the custom character remains a development study and the portrait/liveLewis fallback stays active.

## Listener branch review, October 29 evening

Pinned1f8bab0 isolated baseline:252backend pass/2Windows permission skips. Explicit review acceptance probes:4fail (Stop,reset,claim scoping,theory bound),1pass(schema3round-trip). These are recorded defects on the unmerged branch, not failures in main. Original-function VM and Chromium synthetic microphone evidence are recorded in docs/reviews/listener-1f8bab0-evidence.json; no real mic/provider. Formal findings and rerun commands:LISTENER_REVIEW.md. Product code/assets remain unchanged; preceding full main CI40951937765 green.

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
