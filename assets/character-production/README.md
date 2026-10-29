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
