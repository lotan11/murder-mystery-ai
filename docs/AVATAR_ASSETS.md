# Avatar assets and audition provenance

Updated October 28, 2026. This document separates the free model audition from a final detective character or a speech integration.

## Assets in this repository

| Asset | Purpose | Provenance / license |
| --- | --- | --- |
| Existing procedural Three.js detective | Existing game stage | Built from repository geometry; remains the current stylized placeholder |
| `frontend/public/audition/mpfb.glb` | Optional TalkingHead human-model audition | Unmodified CC0 example from TalkingHead commit `166b443a445eeb63a4ea02270aa9e7d6ba8b4d88` |
| `@met4citizen/talkinghead` | Audition rendering, facial blend shapes and animation capability | MIT library, version 1.8.2; package lock records dependency resolution |

The MPFB model is a generic female human in a blue T-shirt and jeans, not the detective. It demonstrates the quality and mechanics of a more human model without claiming to supply Wobblebottom's final age, clothes, hat, moustache or voice. No character asset was purchased and no TTS/audio was generated as part of sourcing it. A visual audition is not proof of synchronized spoken performance.

## Reproducible provenance

- [Exact raw GLB](https://raw.githubusercontent.com/met4citizen/TalkingHead/166b443a445eeb63a4ea02270aa9e7d6ba8b4d88/avatars/mpfb.glb)
- [Exact README license declaration](https://github.com/met4citizen/TalkingHead/blob/166b443a445eeb63a4ea02270aa9e7d6ba8b4d88/README.md#L373)
- [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/)
- [TalkingHead MIT license](https://github.com/met4citizen/TalkingHead/blob/166b443a445eeb63a4ea02270aa9e7d6ba8b4d88/LICENSE)
- [Bundled public asset/license notice](../frontend/public/audition/ASSET_LICENSE.md)

Downloaded only `avatars/mpfb.glb`, at the pinned commit. Its SHA-256 is `63c645a2a863b9972e9a9c2ed576a1de4c390b8475508e1473e69c87a3ee299c`; byte length is **36,815,920**. The asset was not optimized, reskinned, decimated or recompressed. Its approximately 35.1 MiB download should be presented as an optional on-demand audition, rather than silently loading on every phone or game screen.

On Windows, verify the bytes from the repository root:

```powershell
Get-FileHash .\frontend\public\audition\mpfb.glb -Algorithm SHA256
(Get-Item .\frontend\public\audition\mpfb.glb).Length
```

Other upstream examples were not copied: Ready Player Me, Avaturn, AvatarSDK and VRoid example files have different licensing conditions. Upstream demonstration audio, background media and Mixamo clips are also excluded. The library's MIT license does not convert those example assets to MIT.

## Inspection actually performed

The GLB 2 JSON chunk and embedded resources were inspected, then the whole body was rendered locally with Three.js `GLTFLoader` in Chromium. The model is clothed in a T-shirt and jeans, with bare feet; it is not the unclothed MakeHuman base. No external textures or buffers were requested. This render inspection establishes appearance and basic loadability, not a performance benchmark or a final artistic acceptance.

| Property | Observed value |
| --- | --- |
| glTF asset version / generator | 2.0 / Khronos glTF Blender I/O v5.0.21 |
| Meshes / materials / embedded images | 8 / 8 / 7 |
| Clothing mesh | `female_casualsuit01` |
| Skin | One `Armature` with 67 joints |
| Bone naming | `Hips`, `Spine`, `Spine1`, `Spine2`, `Neck`, `Head`, limbs and fingers; Mixamo-style names without the `mixamorig` prefix |
| Body facial targets | 66 named morph targets: 52 ARKit-style expressions and 14 non-silence Oculus visemes |
| Additional morph-bearing meshes | Eyes, eyebrows, eyelashes, teeth and tongue |
| Viseme caveat | `viseme_sil` is not a named target; neutral/silence is the zeroed expression, not a claimed extra target |
| Animation clips | None embedded; library behavior supplies movement |
| Compression extensions / external URIs | None declared; image data and geometry are embedded |
| Measured whole-model height | Approximately 1.783 model units in the rendered default pose |

The facial inventory includes `eyeBlinkLeft`, `eyeBlinkRight`, `jawOpen`, `mouthSmileLeft`, `mouthSmileRight`, and `viseme_PP`, `viseme_FF`, `viseme_TH`, `viseme_DD`, `viseme_kk`, `viseme_CH`, `viseme_SS`, `viseme_nn`, `viseme_RR`, `viseme_aa`, `viseme_E`, `viseme_I`, `viseme_O`, `viseme_U`. Their presence permits an audition of facial control; it does not establish timing or quality of lip sync to a real voice.

## Runtime boundaries

Load the optional audition separately from the existing game stage. Do not couple it to paid TTS defaults or microphone capture. TalkingHead exposes `dispose()` in 1.8.2: the integration should use that lifecycle cleanup when leaving the audition, rather than only stopping the render loop. Its dependency uses Three.js 0.186; keep the audition's own scene under the library rather than mixing objects from separately resolved Three.js versions.

Before selecting a production detective, record the actual character asset's license, visual approval, rig/blend-shape inventory and performance acceptance. No final Wobblebottom model or custom voice is supplied by this source asset.
