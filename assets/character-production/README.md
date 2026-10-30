# Scholar anatomical development blockout

This is an editable **first 3D blockout**, not an approved likeness, finished groom, production rig, or replacement for the working TV avatar. The approved Scholar portrait remains the visual target. The current meshes have **zero joints and zero facial morphs**; no dummy bones, expressions or visemes were inserted to pass a compatibility check.

## Files and authority

- `scholar.json`: authoritative reproducible macro/target/accessory settings, including the approximate 67-year-old male intent.
- `scholar-blockout.blend`: editable compressed Blender scene. `EDITABLE_MAKEHUMAN_SOURCE_CC0` retains the hidden parametric anatomical source and its target keys; the visible review bust/accessories are mesh-editable.
- `scholar-blockout-inventory.json`: build inventory and provenance.
- `../../scripts/build-scholar.py`: deterministic character builder.
- `../../frontend/public/character-lab/scholar-blockout.glb`: review export, 15 static mesh objects, +Z forward in glTF.
- `../../docs/assets/scholar-blockout-front.png` and `scholar-blockout-profile.png`: actual neutral Blender renders.

The anatomical head/neck begins with MPFB's MakeHuman basemesh, not a face assembled from spheres. Small anatomical eyeballs, wire spectacles, short grey hair guides, jacket/waistcoat/shirt/tie blocking and an embedded project-authored tweed tile are additional meshes. Clothing now covers the underlying shoulders/chest; the first export's visible body intersections were corrected before acceptance as a development artifact.

## Source and license provenance

- MPFB source: [makehumancommunity/mpfb2](https://github.com/makehumancommunity/mpfb2), pinned commit **6ff1eb358f6c1959ced77e79e6dd2406d9a71f49**, extension manifest version 2.0.18, Blender minimum 4.2.0.
- MPFB program code: **GPL-3.0-or-later**, kept in the ignored local authoring-tools checkout. It is not bundled into the game runtime.
- Bundled basemesh, targets and related asset data: **CC0-1.0**, as described by the project's [license](https://github.com/makehumancommunity/mpfb2/blob/6ff1eb358f6c1959ced77e79e6dd2406d9a71f49/LICENSE.md) and [asset declaration](https://github.com/makehumancommunity/mpfb2/blob/6ff1eb358f6c1959ced77e79e6dd2406d9a71f49/LICENSE.ASSETS.md). The upstream license separately discusses exported meshes, saved models and renderings.
- Pinned `src/mpfb/data/3dobjs/base.obj` SHA-256: `bea00279464133e86b634220cd2774ebf3b470de280d11222a6b2269e4a8d950`.
- Portable Blender: official **4.5.15 LTS** archive, prepared and SHA-256 checked by `scripts/prepare-character-tools.py`.
- Accessories and weave tile: project-authored procedural meshes/pixels. No downloaded wardrobe, paid asset, proprietary character service or photo-derived face texture was used.
- Visual targets: `frontend/public/casting/vale.png` and `docs/assets/scholar-construction-reference.png`; reference artwork provenance is recorded separately in the repository.

The GLB has no external resource URIs: its small tweed texture is embedded. It does not read the MPFB checkout or need Blender to display in the isolated character lab.

## Reproduce on Windows

From the repository root, with Git and Python available:

```powershell
python scripts/prepare-character-tools.py --download
git clone https://github.com/makehumancommunity/mpfb2.git data/character-tools/mpfb
git -C data/character-tools/mpfb checkout 6ff1eb358f6c1959ced77e79e6dd2406d9a71f49
$env:BLENDER_USER_RESOURCES = Join-Path (Get-Location) 'data\character-tools\blender-user'
& '.\data\character-tools\blender-4.5.15-windows-x64\blender.exe' --background --factory-startup --python-exit-code 1 --python scripts/build-scholar.py
```

If the checkout already exists, inspect it and check out the pinned commit rather than cloning over it. The build validates both source commit and basemesh checksum. It enables MPFB through a temporary local Blender extension repository (`bl_ext.scholar_mpfb.mpfb`) and does not alter the downloaded addon's code or save global user preferences. Generated authoring-tool caches stay under ignored `data/character-tools` when the environment variable above is set. `-- --skip-renders` builds the mesh and editable scene without regenerating PNGs.

Inspect the result with `python scripts/inspect-character.py frontend/public/character-lab/scholar-blockout.glb`, rebuild the frontend, and use the character lab. Do not activate it on TV as a TalkingHead replacement.

## Remaining art/technical work

The hair is a rough scalp/strand proxy with visible gaps, the beard is sparse, eyelids have been opened in a first refinement but still need likeness review, and wardrobe materials/proportions are only blocking. Head likeness, facial anatomy refinement, production hair cards, skin/PBR textures, retopology, UV review, real rigging/weights, expression shapes, visemes and deformation tests remain future gates. The source supports the next iteration; it does not claim those gates are complete.

## First facial refinement — October 28, 2026

Opened the eyes with symmetric MPFB eye-height2 and eyefold-up targets, reduced additional eye-bag shaping, and added subtle cheekbone shaping. Beard candidates increased from 400 to 750. Real front/profile renders were compared with the previous version and approved portrait; the eyes appear more alert without moving the eye centers. This remains a sparse procedural beard and rough hair proxy, not finished character grooming. Source, config, GLB and renders were rebuilt together; original comparison artifacts stay in ignored work.

## Separate deformation experiments

The zero-rig description above applies to scholar-blockout.glb. skeleton-proof.json/.md record the actual 64-bone weighted full-source experiment (diagnostic scene in ignored data/). face-study.blend is editable source for scholar-face-study.glb, a separate 15-mesh export with jawOpen and two blink morphs, zero exported joints and no speech connection. face-study-validation.json records mapping/neutral error; face-study-glb-validation.json measures binary target displacement. Close-up rest/jaw/blink renders are in docs/assets/. These are development proofs, not final likeness or lip-sync approval.

After preparing pinned Blender/MPFB as documented, run portable Blender in background with --factory-startup --python-exit-code 1 --python scripts/probe-scholar-skeleton.py, then with --python scripts/build-scholar-face-controls.py. The latter checks the canonical source hash against the skeleton report. Inspect the export with .venv/Scripts/python.exe scripts/inspect-character.py frontend/public/character-lab/scholar-face-study.glb --measure-morphs. Open ?view=character-lab and select Face study to try restrained manual controls.

## Weighted bust experiment

rig-study.blend and scholar-rig-study.glb bind the separate face study to the real 64-bone skeleton. Run scripts/build-scholar-bound-study.py with the same portable Blender command after building face controls. Canonical files are not modified. The script normalizes strongest-four anatomical weights, rigidly attaches head accessories/torso wardrobe, checks neutral preservation and positive/negative head turns plus combined jaw/blinks, then restores rest before export. rig-study-validation.json records measurements, rig-study-glb-validation.json records actual inventory, docs/assets/rig-study-head-turn.png is the actual render. Full expressions/visemes, eye gaze, shoulder/cloth quality and live speech are unfinished.

The weighted rig now has eight actual morphs: the original three plus five brows from pinned targets/expression/units/caucasian. Build source records target hashes, upper-face affected height and actual transferred deltas. The face-only GLB remains three controls. See docs/assets/rig-study-brow-lift.png for the real restrained preview; production expressions/visemes and speech alignment remain unfinished.

October 29: weighted study now has eleven controls, adding three real mouth units (pursing, compression and corner-puller) from the same pinned raw expression assets. Rounding/compression caps0.25, slight-smile cap0.20. Source hashes and limits are recorded; original eight displacement inventories are unchanged. No full phoneme/viseme mapping or speech connection is claimed.

## Same-inference Lewis timing proof

Run `.\data\casting-runtime\Scripts\python.exe scripts/probe-scholar-timing.py` with the already prepared optional runtime/models. It verifies pinned assets without downloads, captures the existing create() call's internal create_timed() output, validates model-derived phoneme spans and writes WAVs only under ignored data/scholar-timing-proof. lewis-timing-proof.json is the small checked-in evidence record. Current fixed line:73 spans/5.502s, same waveform object/PCM, Lewis0.92 synthesis and approved1.05 playback. This is a diagnostic, not a worker/API change.

The existing model reports duration output; another paid alignment service is not needed to investigate these cues. Keep metadata and audio from the same inference because repeated neural renders vary. Cue time is original WAV seconds; audio.currentTime follows the source clock at approved playback rate. Model-predicted spans are not hand-verified alignment and still require long-line, bounds and actual facial-playback testing.

October29 timed preview: prepare-scholar-timing-study.py packages the verified proof waveform and cue record into frontend/public/character-lab/lewis-study.wav/.json. It requires the matching ignored proof WAV and checks its hash, frames, voice and pace. Browser playback is an explicit fixed lab study; live worker now separately emits optional validated model cues without changing approved synthesis parameters. Approximate mouth mapping is not complete viseme/perceptual approval.

The bound-study builder now identifies existing cavity faces with pinned data/textures/mpfb_inside-mouth.jpg and assigns a rough oral lining. rig-study-validation.json records its hash,398-face/418-vertex coverage and anatomical bounds. No new geometry; the15-mesh GLB has one additional head material primitive, with deformation counts/magnitudes preserved. The mask is used for authoring, not redistributed as a runtime texture.

Run .venv/Scripts/python.exe scripts/probe-scholar-long-timing.py after optional voice preparation to validate the public59-word narration sample through the actual worker. The report lewis-long-timing-proof.json is checked in; WAV/sidecar remain ignored. Observed25.06s/391cues and21.10s generation are evidence for one local run, not a latency or max-length guarantee.

Run .venv/Scripts/python.exe scripts/probe-scholar-cache.py after optional local voice preparation to measure a real isolated renderer cache miss and immediate hit for the same canonical public narration. lewis-cache-proof.json records waveform/timing identity, actual worker count, observed times, payload budget and cleanup; it does not preserve the waveform or change live rooms. One local run is not a cross-device or first-generation performance guarantee.

Skin-material delivery: scripts/bake-scholar-skin.py is called by the bound-study builder and creates three1K PNG source maps in skin-materials/, packed into rig-study.blend and GLB. It uses8Cycles CPU bake samples/8px margins, color-only base bake, a bump-disabled normal baseline and emission coverage measurement; restores prior render samples afterward. See skin-material-validation.json. All maps are project-generated from existing local nodes/UVs; no new scan/photo/paid texture. Subsurface response is not baked. Geometry and11 real morphs remain unchanged.

Fitted facial groom: scripts/refine-scholar-groom.py is a bound-study helper, not a separate model implementation. Deterministic2200beard/800moustache clumps add18kvertices/12ktriangles; actual head-triangle correspondence drives normalized skin weights and four nonzero mouth targets. It records groom-validation.json and actual front/profile renders. Crown/scalp remain unchanged after a rejected preview experiment. Skin textures and original head geometry remain intact. Full hair/likeness and complex intersection/perceptual quality remain unfinished.

## Cap coverage development repair

The bound-study builder calls `scripts/refine-scholar-crown.py` for a conservative cap-only projection/weight transfer. Same topology/material, no new hair geometry; actual head and facial targets remain unchanged. `crown-validation.json` retains positive smooth-normal fit and unresolved sharp ear-edge raw triangle disagreements. This repairs visible crown holes, not the unfinished helmet hairline or final silver hair design. Review tracked `docs/assets/crown-before/after-front/profile.png` and the lab Face close-up at multiple angles.

## Restrained iris material study

The bound builder calls `scripts/refine-scholar-eyes.py`: project-authored512px slate-grey iris albedo on newUV1, preservingUV0 and actual eye/pupil/sclera anatomy. SourcePNG is under eye-materials/; exact hash, bounds and limitations are in eye-material-validation.json. Five images now embed in the GLB (coat,three skin,one iris). This is supported material detail, not finished eyes, gaze/cornea or portrait likeness.

## Core source asset reuse

Included verifiedCC0 core source files:source-assets/makehuman-system/SOURCE.json. Fit hair with fit-scholar-hair-asset.py; refine skin color with refine-scholar-skin-color.py. Both are builder stages after iris/before pose checks. Canonical static/face-only models remain unchanged. Derivedhair RGBA/normal and refinedskincolor export as real images (seven total). Original cap is retained only in editable source; source overlap is measured and not certified intersection-free. Fullreview/recipe:docs/reviews/SCHOLAR_CORE_ASSETS_REVIEW.md.

## Derived eyelid neutral refinement

refine-scholar-eyelids.py runs after binding identity and before skin bake/crown/groom. It is an explicit419-vertex eye-local neutral correction, not a change to canonicalstatic/face-only source. eyelid-validation.json and eyelid-neutral-offsets.json bind exact reviewed input/target hashes, unchanged11morphdeltas/UV/weights/rig and declared before/after positions. Manifest hash normalizes UTF-8 line endings toLF. Tests preserve the original head multiset outside that support. Do not doubleapply; rebuild from face-study.blend. Existing original fullsource remains editable. Rebuilt skin normal/refinedcolor maps follow the modified surface; all modes/voice remain intact.
