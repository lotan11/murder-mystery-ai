# November 10 integration plan

**User deadline: November 10, 2026, America/Denver.** No exact handoff hour was specified. This is the integration deadline, not an authorization for paid providers, purchases or public deployment.

## Acceptance and critical path

The delivery must retain a runnable, complete Blackthorn case with synchronized organizer/guest/TV interfaces, private character isolation, saved-room recovery, the approved Scholar identity and Lewis voice at the approved +5% pace, responsive interruption and readable captions. The existing portrait + real Lewis mode is already playable and must remain the reliable fallback.

The custom animated Scholar is the main schedule risk: the canonical blockout stays static; the separate development rig now has **64 weighted joints and eleven facial morphs**, with full expression/viseme controls and production deformation quality still missing. A finished likeness, compatible deformable rig, actual voice alignment and quality review are not delivered by a file-loading test. These remain the priority work rather than more casting alternatives.

## Internal checkpoints

These are engineering planning targets, not promises that unavailable art work is already complete.

| Date | Target | Gate |
| --- | --- | --- |
| October 29–31 | Likeness/head/eyelid/hair/wardrobe refinement | Compare real front/profile renders with the approved portrait; keep reversible source and config |
| November 1–3 | Skeleton, facial deformation and voice-alignment prototype | Real targets/weights, TalkingHead loading and restrained speech motion; no dummy controls |
| November 4 | Animated-character readiness decision | If quality/inventory/actual speech gates remain unmet, flag risk immediately and keep portrait/Lewis as the stable integration baseline |
| November 5–7 | End-to-end integration and regression | Complete case across host/guest/TV with pause/reset/reconnect, no private-data leaks or stale speech |
| November 8 | Feature freeze | Fix defects and deadline blockers; avoid optional scope expansion |
| November 9 | Rehearsal and recovery verification | Human dinner/device rehearsal still requires actual participants/devices; record observed issues rather than claiming automated viewport tests are a rehearsal |
| November 10 | Integration handoff | Runnable repository, setup, known limitations, test/CI evidence and a clear list of any deferred visual polish |

## Integration inventory

- Main: full playable mystery, private roles, persistence, default dry humor, approved Scholar portrait/live Lewis and separate 3D authoring lab.
- Latest main source at deadline planning: `645dad7`; independent CI run `40792819175` passes (251 backend tests locally, 15 client checks, thirteen browser scenarios/build; two local Windows privilege skips).
- Remote `feature/listener`: two commits for consent-based typed/microphone discussion, currently diverged from main; not merged or claimed part of main. Initial docs review says paid transcription is disabled by default, with a separate allowance/configuration and schema-related changes. Review code, privacy/cost defaults and saved-room migration before any integration. This work does not justify paid calls or disrupt the avatar critical path.

## Reporting and controls

Four-hour progress updates are configured in this chat. Report actual completed work, current test/CI state, the next milestone and risks to November 10. Do not imply unattended work between scheduled runs. Preserve the approved look/voice/pace; new casting approval is not a blocker. Material spending, public deployment or a scope tradeoff affecting the agreed deadline must be surfaced before execution.

## October 28 rig checkpoint

Weighted source proof now passes (64 bones); separate face study has actual jaw and two blink morphs with exact neutral preservation. Canonical bust remains static; the face-study export has no skeleton and no speech connection. Full expressions/visemes, production materials/groom, bust/accessory binding and real Lewis alignment remain on the critical path. This proof does not satisfy the November 4 animated-character readiness gate.

October 28 binding checkpoint: separate bust now exports actual skin weights and 64 joints with three facial morphs, restrained head control and combined-pose/rest checks. This advances the rig proof but does not satisfy full speech/quality readiness.

October 28 expression checkpoint: five real brow controls added to the weighted bust (eight total); upper-face localization, unchanged jaw/blinks and restrained lab controls verified. Mouth/lip shaping, full expression/viseme quality and real voice alignment remain incomplete.

October 29 mouth checkpoint: real rounding/compression/slight-smile units bring the weighted study to eleven controls. Existing eight deformations unchanged. This does not establish phoneme mapping, a finished mouth interior or actual voice synchronization; these remain on the critical path.

October29 reliability/timing checkpoint: fixed continuous static-lab drawing after CI rig test timed out; all15 local browser scenarios now pass with original90s budget. Approved model exposes phoneme durations; same-inference fixed-line proof captures73 spans with unchanged audio. Runtime cue integration, perceived alignment and finished face quality remain pending. No outside paid alignment dependency is currently necessary for the next experiment.

October29 speaking-study checkpoint: fixed localLewis audio now drives actual rig morphs in the opt-in lab using its own model cues; optional bounded worker/API timing is implemented. Full visual/perceptual quality, mouth interior and long-dialogue evaluation remain incomplete, so this is not production avatar readiness. Existing portrait/live Lewis stays the stable baseline.

October29 oral/long-dialogue checkpoint: weighted rig now shades its existing cavity with an anatomical lining material; detailed dentition/tongue and production appearance remain incomplete. A real59-word public narration passed timing validation (25.06s/391 cues), but took21.10s to prepare locally. Add generation latency/caching evaluation to the critical path before live3D use; do not infer all1500-character inputs fit the40s worker budget. Portrait/live Lewis remains protected.

October29 replay/perceived-quality checkpoint: bounded public clip cache reduces observed immediate repeat preparation from12.107s to0.005724s for one local case sample, with unchanged audio/cues and one worker. New/expired/evicted text remains cold. SCHOLAR_QUALITY_REVIEW.md identifies missing runtime skin maps plus major groom/likeness/tailoring gaps; these remain P0 before custom-avatar activation. No paid art path or new casting decision was authorized/needed for this increment.

October29 material delivery checkpoint: three1K skin maps now bake reproducibly and bind to actual exported/runtime material; genuine normal detail verified against bump-disabled baseline. Browser/GLB delivery gap is resolved for existing grain, not complete skin artistry. Groom, likeness, tailoring, detailed oral shapes and perceived speech quality remain critical before the November4 gate.

October29 facial-groom checkpoint: denser beard/moustache now fitted to the actual head and tested in local Lewis playback; original head/skin/skeleton and live game preserved. Crown-card experiment rejected, scalp/crown unchanged. The groom still reads coarse and uneven; crown/hairline shape, face likeness and final hair/material/oral quality remain before the November4 readiness gate.

October29 crown checkpoint: visible scalp holes repaired in the isolated rig; unchanged cap topology/material and original head, with anatomical cap weights. Raw triangle sign disagreements near ears remain explicitly reported despite positive smooth-normal clearance. Face close-up/full-bust controls improve consistent likeness review on desktop/phone. Final hairstyle, portrait-matched face/eyes/tailoring and perceived speech quality still threaten custom-avatar readiness; preserve November4 gate and portrait/Lewis demonstration baseline.
