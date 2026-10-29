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

The lab now also offers Weighted rig study. This separate GLB has 64 joints, real skin weights and eleven morphs; manual head turn is limited to ten degrees each way. The original static blockout and face-only experiment remain separate. No speech, production activation or full facial compatibility is implied. Build after the face study with portable Blender --background --factory-startup --python-exit-code 1 --python scripts/build-scholar-bound-study.py. See rig-study-validation.json for measured deformation and rig-study-glb-validation.json for actual export inventory.

Brow geometry comes from pinned raw targets/expression/units, not the empty packaged data/expressions directory. Five new controls use actual sparse anatomical deltas and affect the skin plus nearby brow guides. Lifts cap at0.35, lowering at0.25; no speech mapping or final expression-quality approval is implied.

Three manual mouth units now complement the brows, jaw and blinks: rounding 0.25, compression 0.25, slight smile 0.20. Renders in docs/assets/rig-study-mouthPucker.png, rig-study-lipPress.png and rig-study-mouthSmile.png show actual geometry at those limits. These are not a complete viseme set; mouth interior and speech synchronization remain unfinished.

The static lab now draws on change and skips idle GPU work; orbit damping and manual shape/pose changes still update actual geometry. This optimization does not change time-driven TV animation. See the separate Lewis timing probe in assets/character-production/README.md; no speech connection has been activated.

## Try the fixed timed speech study

Open `?view=character-lab`, choose **Rig study**, and select **Play Lewis timing study**. The bundled clip plays at approved1.05 pace without any runtime/model installation, paid account or microphone. Stop cancels/reset; changing model, hiding the page or losing graphics also stops it. Localhost or HTTPS is required for the waveform integrity check.

The preview uses model-predicted phoneme spans and a deliberately simplified small mouth mapping, not a finished full-viseme TalkingHead performance. Audio SHA256, PCM format and duration are checked before playback. Source-clock cues follow audio.currentTime and are not accelerated twice. The game remains approved portrait/live Lewis.

To reproduce the sample, first run the same-inference timing probe with the optional runtime, then `.\.venv\Scripts\python.exe scripts/prepare-scholar-timing-study.py`. Packaging validates that the local WAV matches the recorded proof before copying it into the lab. No synthesis/download occurs during packaging or browser playback.

October29 oral refinement: the weighted study uses the existing anatomical UV mouth mask to assign lining to398 cavity faces. Vertex/triangle counts and neutral shape are unchanged; skin now has a second material primitive. See docs/assets/rig-study-mouth-lining.png for the actual restrained open-jaw render. No teeth/tongue or new cavity geometry was created. Full interior and face quality remain under development.

## Baked skin maps

The bound-study builder calls scripts/bake-scholar-skin.py as a Blender helper. It bakes1K color-only albedo, roughness and tangent normals from the existing skin nodes, verifies normal detail against a bump-disabled baseline using a UV coverage bake, saves PNGs under assets/character-production/skin-materials and packs them into the editable scene/GLB. Run the normal bound-study Blender command; the helper is not a standalone model-generation command.

skin-material-validation.json records samples, margin, color spaces, hashes and measured detail. The inspector's material_inventory records actual runtime references, embedded image hashes and dimensions. Character lab displays the actual loaded1K map count; static/face-only studies remain at zero, weighted rig at three. Subsurface response and final artistic skin/groom/likeness are unfinished.

## Fitted facial groom

The bound-study builder calls scripts/refine-scholar-groom.py after skin baking/binding. It adds deterministic beard/moustache ribbon clumps matched to actual head triangles, transferring real weights and nonzero jaw/rounding/compression/smile deltas. See groom-validation.json for counts, fit/orientation/lip-proxy guards and pose checks. docs/assets/groom-study-front.png and groom-study-profile.png are actual comparison renders. Original crown/scalp are deliberately unchanged. This is not production hair cards, anisotropic grooming or final likeness approval.

The inspector now reports mesh_inventory with node/material labels, component geometry and actual nonzero deformation measurements. Original-head position/deformation tests remain separate from intentional added groom topology.
