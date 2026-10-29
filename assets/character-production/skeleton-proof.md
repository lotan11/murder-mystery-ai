# Scholar source skeleton proof

This isolated experiment binds the preserved editable MakeHuman source to the pinned MPFB `mixamo_unity` skeleton and proves that imported skin weights deform geometry. It does not change the canonical review bust, public GLB, game avatar or voice.

## Reproduce on Windows

From the repository root, after the documented portable Blender/MPFB authoring setup:

```powershell
$env:BLENDER_USER_RESOURCES = Join-Path (Get-Location) 'data/character-tools/blender-user'
& '.\data\character-tools\blender-4.5.15-windows-x64\blender.exe' --background --factory-startup --python-exit-code 1 --python scripts/probe-scholar-skeleton.py
```

The script copies the canonical `.blend` into ignored `data/character-tools/skeleton-proof/` before loading it. It enables the pinned MPFB extension, finds the preserved source collection, calls `HumanService.add_builtin_rig(source, 'mixamo_unity', import_weights=True)`, and verifies the resulting armature modifier targets the imported rig. It reads no network resources. The diagnostic full-body `.blend` remains in the ignored folder and is not exposed by the application.

## Measured result

The generated `skeleton-proof.json` records the input blend, rig and weight SHA-256 digests and complete raw bone names. The tested input produced 64 bones with the upstream `mixamorig:` prefix and imported weights on 19,158 source vertices. Rotating `mixamorig:Head` by 12 degrees around its local Y axis displaced 4,977 strongly head-weighted vertices by up to 0.02770 metres (mean 0.01827 metres). All 7,077 tested vertices below one metre stayed stationary. Restoring the pose returned all evaluated vertices with zero measured error. The script fails if meaningful head displacement, stationary lower body, or rest-pose restoration checks fail.

The upstream skeleton includes eye, jaw and orbicularis bones. Their presence is inventoried; their movement and deformation have not been tested. Names retain their prefix, so this is not a claim of immediate TalkingHead compatibility.

## Scope and provenance

MPFB commit `6ff1eb358f6c1959ced77e79e6dd2406d9a71f49`, source code GPL-3.0-or-later; bundled rig/base assets CC0. Actual upstream rig and weights are `src/mpfb/data/rigs/standard/rig.mixamo_unity.json` and `weights.mixamo_unity.json`. The script uses the upstream service rather than creating nominal label-only bones. See the folder README for complete source/tool provenance.

Only the hidden anatomical source is bound. Cropped public skin, garments, spectacles, eyeballs and procedural hair/beard are not bound by this experiment. No facial morphs, expression controls, visemes, lip sync, animation quality or production readiness are claimed. The public review GLB remains an unrigged development blockout.
