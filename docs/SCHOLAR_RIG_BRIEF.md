# The Scholar: production character and rig brief

Updated October 28, 2026. **Approved visual direction; custom 3D asset not yet created.**

## Approved identity and present delivery

The user selected **The Scholar** portrait, **Lewis** as the voice, and a pace **5% faster than the approved baseline**. These choices are settled; asset development should not restart casting or seek approval for the same look and voice again.

The visual authority is [the approved portrait](../frontend/public/casting/vale.png), SHA-256 `9850b73dae23db093180bbadd6a02d0d8b78e97a88cab4473c8cf8490f9f90e7`. Its generation provenance and original concept prompt are in [casting provenance](../frontend/public/casting/PROVENANCE.md) and [the image prompts](CASTING_IMAGE_PROMPTS.md). The filename `vale.png` is a casting asset key: the character remains **Detective Reginald P. Wobblebottom**, not the case's suspect Dr. Margot Vale.

The current integration target is the approved **static portrait with live Lewis speech**, preserving the existing TalkingHead sample for an animated comparison. A speaking portrait remains a still image. The clothed CC0 MPFB sample remains a different human model. Neither is a custom Scholar mesh, likeness rig, or final animated detective. Actual voice/playback verification belongs in the milestone progress and validation reports, not an inference from this brief.

## Visual requirements

- Mature man, approximately 67, with a weathered but natural face, intelligent blue-grey eyes and thoughtful warmth. Preserve the portrait's face proportions and asymmetry rather than making a generic older gentleman.
- Wavy silver hair with a soft side part; neatly trimmed silver moustache and short beard. Facial hair must frame the lips without concealing their movement.
- Understated round, thin dark-bronze spectacles. Clear lenses leave the eyes readable; reflections must not become opaque discs under the manor lighting.
- Dark brown herringbone tweed jacket, deep green waistcoat, ivory shirt, muted patterned tie, pocket detail and restrained watch chain. Match the portrait's tailoring and silhouette. Cloth texture should remain stable at TV distance, without distracting moire.
- Premium stylized realism: believable human anatomy with a little artistic simplification. No oversized mouth, rubber face, cartoon eyebrows, theatrical grin, monocle, pipe or added hat.
- Performance is observant and gently dry. A small brow lift or quiet change of gaze should carry wit; constant nodding, broad smiles and exaggerated lip shapes should not.

The portrait supplies one angle, not a complete 3D specification. A front, three-quarter and profile construction sheet should resolve its unseen proportions consistently. This is a realization of the selected design, not a new round of alternative characters.

## Actual runtime contract

Target the repository's **TalkingHead 1.8.2** integration. Requirements below were checked against the installed `modules/talkinghead.mjs`, the local `frontend/src/talkinghead.d.ts`, and the upstream compatibility material already recorded in [AVATAR_ASSETS.md](AVATAR_ASSETS.md). They are acceptance requirements for a future asset, not a claim that one exists.

| Area | Required delivery and check |
| --- | --- |
| Container | Browser-loadable glTF 2 binary `.glb`, with textures embedded or explicitly bundled locally. No undocumented CDN or credential dependency. |
| Skeleton | Mixamo-compatible body skeleton and bone axes/rolls. Prefer a root named `Armature`, matching the library default. A head-only mesh with missing required body/hand bones is not sufficient for the current loader. |
| Naming | Bone names below must resolve after TalkingHead strips the optional `mixamorig` prefix. Preserve expected hierarchy and usable local transforms, not just matching labels. |
| Eyes | Separate controllable `LeftEye` and `RightEye` objects in addition to the pose bones; the loader queries their transforms and derives eye level. Eyes must rotate and blink without separating from lids or spectacles. |
| Facial control | ARKit-style expression targets and Oculus viseme targets with the exact names below, exposed through glTF morph target names. Compatible names alone do not establish good deformation. |
| Mouth interior | Teeth and tongue need appropriate geometry and deformation. Closed lips, teeth contact and tongue poses must remain believable at close camera distance. |
| Hair and accessories | Beard/moustache follow facial deformation; scalp hair and spectacles remain attached during head motion. No noisy hair simulation is required. |
| Application fit | Load through `showAvatar`, support English `speakAudio` with audio/words/start times/durations, and stop cleanly through `stopSpeaking`/`dispose`. No new voice service is needed to prove the rig. |

### Bone inventory

The installed loader derives `posePropNames` from its poses and rejects models missing those named objects. Its current pose setup references these **52 bones**:

- Core: `Hips`, `Spine`, `Spine1`, `Spine2`, `Neck`, `Head`.
- On **each** side (`Left` and `Right`): `Shoulder`, `Arm`, `ForeArm`, `Hand`, `UpLeg`, `Leg`, `Foot`, `ToeBase`.
- On **each** hand: `HandThumb1`–`HandThumb3`, `HandIndex1`–`HandIndex3`, `HandMiddle1`–`HandMiddle3`, `HandRing1`–`HandRing3`, `HandPinky1`–`HandPinky3`, all with their `Left`/`Right` prefixes.

`LeftEye` and `RightEye` are additionally used directly by the loader. Extra hair/jaw/accessory bones are permitted; this brief does not require a particular total bone count or copy the sample's 67-joint count as a rule.

### Facial inventory

Author these 52 named ARKit-style controls, retaining good left/right independence:

```text
eyeBlinkLeft eyeBlinkRight eyeLookDownLeft eyeLookDownRight
eyeLookInLeft eyeLookInRight eyeLookOutLeft eyeLookOutRight
eyeLookUpLeft eyeLookUpRight eyeSquintLeft eyeSquintRight
eyeWideLeft eyeWideRight jawForward jawLeft jawRight jawOpen
mouthClose mouthFunnel mouthPucker mouthLeft mouthRight
mouthSmileLeft mouthSmileRight mouthFrownLeft mouthFrownRight
mouthDimpleLeft mouthDimpleRight mouthStretchLeft mouthStretchRight
mouthRollLower mouthRollUpper mouthShrugLower mouthShrugUpper
mouthPressLeft mouthPressRight mouthLowerDownLeft mouthLowerDownRight
mouthUpperUpLeft mouthUpperUpRight browDownLeft browDownRight
browInnerUp browOuterUpLeft browOuterUpRight cheekPuff
cheekSquintLeft cheekSquintRight noseSneerLeft noseSneerRight tongueOut
```

Target the documented 15 Oculus viseme names:

```text
viseme_sil viseme_PP viseme_FF viseme_TH viseme_DD
viseme_kk viseme_CH viseme_SS viseme_nn viseme_RR
viseme_aa viseme_E viseme_I viseme_O viseme_U
```

The existing CC0 sample has 14 non-silence targets and uses a zeroed neutral expression for silence; its successful use does not mean every future model may omit any target without testing. The production export should provide `viseme_sil` as a neutral control or explicitly demonstrate that zeroing its non-silence targets produces the approved neutral pose in this integration. Additional convenience controls such as `mouthOpen` and `eyesClosed` can be derived by TalkingHead; they are not substitutes for missing authored facial deformation.

## Restrained performance baseline

Keep the user's accepted motion revision as the starting point: application viseme output is **45% of library strength, capped at 0.38**, with modest speech-weighted upper-face expression and head motion. These values are present in the current audition/live renderer; they are application tuning, not a guarantee that the new mesh will look right at those values.

Lewis should retain the approved voice identity with the requested **1.05 pace factor**. Faster audio requires matching regenerated or transformed timing data; do not speed only the sound while leaving old word timing behind. Word-start timing and estimated durations are not a claim of measured phoneme alignment. Keep voice/provider configuration and credentials in the existing speech path, outside the character asset.

## Acceptance gates

| Gate | Evidence required before marking it complete |
| --- | --- |
| Likeness | User reviews the first 3D neutral front, three-quarter and profile renders against the already selected portrait. Match face, spectacles, hair, facial hair and tailoring; approval concerns the 3D realization, not reconsidering the settled concept. |
| Topology | Inspect neutral and isolated blink, smile, jaw, lip-seal and tongue shapes. No lip/teeth intersections, inverted surfaces, floating beard, broken eyelids or spectacles entering the face. Deformation loops must support the observed motion rather than relying on a texture of a face. |
| Rig/load | Automated inventory plus a real `showAvatar` load in the existing app, with no missing-bone/blend-shape errors. Confirm eye direction, camera framing and normal standing/head poses. |
| Speech | Play short and long existing public detective lines using Lewis at the selected pace. Confirm actual audio and actual facial influences, rather than animation of a still portrait or synthetic CI tones. Inspect closed-lip consonants, open vowels, pauses and the end of a line. |
| Restraint | Evaluate the current 0.38 cap and gentle brow/head behavior on this mesh. User confirms it conveys dry wit without exaggerated lips, constant nodding or distracting facial hair movement. Tune down before increasing amplitude. |
| Recovery | Pause, Stop, voice change, new dialogue, disconnect and leaving the page stop old speech and return speech visemes to rest. Model/audio failure preserves readable case captions and evidence. |
| Browser budget | Measure load time, transfer size, frame rate and memory on the actual TV computer. The existing renderer targets 30 FPS; record observed behavior rather than claiming a device-independent performance guarantee. Optimize textures/geometry without silently destroying likeness or facial shapes. |
| Provenance | Supply editable source, exported GLB, texture sources, asset/license inventory, checksum and export settings. Every included mesh, hair, clothing and texture must permit delivery as a downloadable web asset. |

Automated inventory and browser regressions establish compatibility; they cannot approve likeness or acting quality. No gate above is presently passed for a custom Scholar rig because no such rig has been supplied.

## Available tools, remaining blocker and next asset step

The environment currently has a raster image-generation tool, Three.js/GLTFLoader, TalkingHead and Python inspection utilities. These can produce reference images, render an existing GLB, inspect its structure and verify runtime behavior. They do **not** provide an already available, production-ready portrait-to-rig conversion. A `blender` executable was not found on PATH or in the checked standard `C:\Program Files\Blender Foundation` installation location; this is a limited environment check, not proof that no installation exists elsewhere.

The precise missing deliverable is a **likeness-matched, clothed 3D mesh with deformable facial topology, the required skeleton and facial targets**, together with its editable source and web-distribution provenance. Another generated portrait or a mesh lacking blend shapes does not close that gap. No asset purchase, paid add-on, 3D service call or custom rig creation has been performed by this brief.

The next actionable asset-creation step is to prepare the approved Scholar's front/three-quarter/profile construction references and establish a Blender + MPFB-compatible authoring workspace, following the creation route already documented by TalkingHead. Build a neutral head-and-costume blockout from a reusable, appropriately licensed base, then compare likeness **before** investing in final textures and facial shapes. A character artist can use this same brief if that route is later selected; no commission has been initiated. Retopology, expression authoring, rigging and export validation remain real work after any initial reconstruction or blockout.

Continue using the approved portrait/live-voice milestone and existing animated sample while that asset is created. Do not relabel the sample as the Scholar or claim the portrait has acquired a 3D rig.

## Construction reference prepared

A front/profile/three-quarter [construction reference sheet](assets/scholar-construction-reference.png) was generated from the approved portrait with the built-in image tool and inspected. It preserves the selected glasses, silver hair/beard, tailoring and mature proportions. It is 2D guidance only, not a mesh, measured scan or animation rig. The approved original portrait remains the likeness authority if the generated unseen view differs. Exact generation prompt is in SCHOLAR_REFERENCE_PROMPT.md.

## Authoring foundation update

Portable Blender 4.5.15 and a pinned MPFB source checkout are now available locally under ignored data/character-tools. The earlier environment limitation above is historical. An actual anatomical development bust, editable Blender source, build settings and separate browser workbench now establish the modeling/export path. This is a blockout, not a completed likeness or facial rig. See CHARACTER_AUTHORING.md for reproduction and current gates; keep the approved portrait/live Lewis in the game.
