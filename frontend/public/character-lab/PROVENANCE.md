# Scholar development GLB

An anatomical development blockout, not a finished likeness or facial rig. The canonical editable source, configuration, upstream commit/base checksum, distinct GPL software/CC0 base-data provenance and build commands are recorded in `assets/character-production/README.md` and `scholar.json` in the repository. The mesh derives from the pinned MPFB/MakeHuman CC0 anatomical base with project-authored accessories and an embedded weave texture. No downloaded third-party wardrobe or paid asset is included. Current export: 15 static meshes, zero joints, zero facial morphs. Approved portrait + Lewis remains the active game presentation.

The separate scholar-face-study.glb derives from the same CC0 anatomical base and project-authored accessories/groom. Three experimental shape targets are snapshots of actual imported MPFB weighted bone poses, mapped to canonical head vertices and beard guides. No full TalkingHead compatibility, finished likeness or speech animation is claimed. Canonical blockout is preserved.

The separate scholar-rig-study.glb retains the same CC0-derived anatomy and project-authored accessories/morph studies, adding actual imported MPFB mixamo_unity skin weights. Software remains subject to its existing GPL notices; the CC0 anatomical/weight data provenance is unchanged. This is a manual binding study, not a finished speech avatar.

Five brow morphs in the rig study derive from the same pinned MPFB CC0 asset collection, under data/targets/expression/units/caucasian. Exact raw-file hashes are recorded in rig-study-validation.json. These are partial legacy expression units, not a licensed external avatar or complete facial-control package.

Three mouth units derive from the same pinned CC0 raw targets: mouth-pursing, mouth-compression and mouth-corner-puller. Exact hashes are in rig-study-validation.json. They are manual expression studies, not a complete external facial rig or speech-alignment service.

lewis-study.wav is original fixed-line local Kokoro bm_lewis output (generation0.92, approved playback1.05), packaged from the same inference as its73 cues. SHA2564f21d61d4c4344e606667721915189a3597b0545dbef35345773bd3c2d8c8499. Runtime MIT/model Apache2 provenance and pinned model hashes follow the existing approved casting generator; no runtime or model weights are redistributed here. lewis-study.json contains model-predicted source-WAV timing, not manually annotated forced alignment. This fixed preview does not activate the unfinished Scholar in the game.

The weighted rig oral-lining assignment derives from pinned CC0 mpfb_inside-mouth.jpg (SHA256dc3e5b39e677351e3bb4c60653dc4d3516f585690076ec4c749e04402db3bf05). Only existing face material indices change; the mask itself is not shipped in the GLB. No external teeth asset, invented geometry or production-quality approval is implied.
