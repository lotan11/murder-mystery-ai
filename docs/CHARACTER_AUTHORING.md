# Scholar 3D authoring workbench

The separate `?view=character-lab` route compares the approved Scholar portrait with an actual locally exported development GLB. It has front/profile/three-quarter camera presets, orbit/zoom and measured geometry/rig inventory. It cannot activate the model in the dinner game or start voice playback.

## Tool preparation

The optional portable authoring tools live in ignored `data/character-tools/`; they do not change system PATH, replace the game runtime or install a system-wide application.

```powershell
.\.venv\Scripts\python.exe scripts/prepare-character-tools.py --download
```

This command downloads Blender 4.5.15 LTS Windows x64 from the official Blender archive, checks the pinned 398649826-byte size and SHA-256 `52dd02fd74877fa08e74b67d7854cf32468a232c02aaa19b6844c91285574f8d`, validates extraction paths, then extracts into the dedicated local tool folder. Source: [official release archive](https://download.blender.org/release/Blender4.5/) and [checksum file](https://download.blender.org/release/Blender4.5/blender-4.5.15.sha256).

Model construction uses the pinned MakeHuman/MPFB anatomical base and project-authored accessories rather than a textured sphere or an animated still image. Source versions and distinct code/asset licenses are recorded with the build script and model provenance. No paid service, purchased asset or cloud avatar conversion is used.

## Rebuild the model

The canonical editable source is `assets/character-production/scholar-blockout.blend`; settings are in `scholar.json`, and `scripts/build-scholar.py` is the reproducible build recipe. Follow [pinned MPFB setup and exact build commands](../assets/character-production/README.md). No Blender installation is needed merely to view the checked-in GLB. The current export has 15 meshes, an embedded texture, and zero joints or facial morphs. It is a development bust, not a finished speaking character.

## Inspection

```powershell
.\.venv\Scripts\python.exe scripts/inspect-character.py frontend/public/character-lab/scholar-blockout.glb
```

The inspector checks the GLB container, real mesh/accessor inventory, embedded-resource status and the expected TalkingHead bone/expression/viseme names. A complete inventory is a necessary check, not a claim of approved likeness, realistic facial deformation or production readiness. The existing CC0 sample is inspected separately and lacks a named silence target while using neutral reset; that exception is documented, not hidden.

The workbench displays actual mesh, joint, skin and named-morph counts measured from the loaded scene. A static development blockout can load correctly while still having zero rig joints or facial targets. It must not be selected for live TalkingHead speech until those missing deformation/rig requirements and quality gates are satisfied.

## Milestone boundary

The approved portrait + live Lewis presentation remains the playable TV default at the approved pace. The authoring model is a work in progress and has not replaced it. This milestone establishes editable anatomical geometry, reproducible export and inspection; likeness refinement, production hair/cloth materials, facial topology/shape targets, a compatible skeleton and actual speech deformation testing remain real follow-up work. See SCHOLAR_RIG_BRIEF.md for the acceptance gates.

## Separate weighted rig study

The lab now also offers Weighted rig study. This separate GLB has 64 joints, real skin weights and eight morphs; manual head turn is limited to ten degrees each way. The original static blockout and face-only experiment remain separate. No speech, production activation or full facial compatibility is implied. Build after the face study with portable Blender --background --factory-startup --python-exit-code 1 --python scripts/build-scholar-bound-study.py. See rig-study-validation.json for measured deformation and rig-study-glb-validation.json for actual export inventory.

Brow geometry comes from pinned raw targets/expression/units, not the empty packaged data/expressions directory. Five new controls use actual sparse anatomical deltas and affect the skin plus nearby brow guides. Lifts cap at0.35, lowering at0.25; no speech mapping or final expression-quality approval is implied.
