# Scholar core hair and skin integration — October 30, 2026

## Selection and exclusions

Accepted as a **development-rig refinement**, after matched Cycles and actual Three.js GLB review: MakeHuman core **short02** hair fitted through the actual retained MPFB source/MHCLO mapping, plus a restrained45% blend of the authored old_caucasian_male diffuse into the original skin color. The [official system inventory](https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html) lists these core assets asCC0; each included OBJ/MHCLO/MHMAT explicitly states its September2020CC0 release. Original headers and exact selected-fileSHA256 are retained in source-assets/makehuman-system/SOURCE.json. Source bytes are excluded from Git line-ending conversion so hashes remain portable.

Excluded from public reuse: culturalibre_hair_01 hasAGPL3 in its fitting header despite the [hair01 inventory'sCC0 listing](https://static.makehumancommunity.org/assets/assetpacks/hair01.html); Cortu has authorCC0 declarations in fitting/material files but anAGPL3 OBJ header, plus an unsuitable eye-crossing fringe. No assertion that the conflict is resolved. Core short03 has consistent headers but covers an eye/intersects spectacles. Their previews remain ignored; only selected core short02/skin files are redistributed.

Retrieval used HTTPS range requests for ZIP entries with CRC checks and stable archive ETag, not a completed archive download. The slow partial full-pack download was stopped and removed. Per-file hashes are authoritative; no full-archiveSHA claim. No purchase/provider call/public deployment.

## Delivered hair

`fit-scholar-hair-asset.py` fits actual short02 to the retained full anatomical source. All1,755imported vertices receive normalized weights on the existing Head bone; no new bones/morphs. Derived RGBA silver albedo retains original alpha exactly. Actual glTF uses2048color/alpha plus supplied2048normal, BLEND/double-sided, normal strength0.4, roughness0.8, specularFactor0.3. The source material disables normal, so this tangent interpretation is explicitly a tested project adjustment, not claimed source intent. Actual browser views, not only Cycles, guided silver brightness and highlights.

The original cap stays in editable source and exits active export. Only crown polygons retire from legacy guide objects; original vertex/morph/weight arrays, brows, facial groom, face and eyes are preserved. Existing Head correspondence stays below one micrometre at±10degrees. A nearby-vertex contact proxy records26 inward triangle signs/minimum−2.264mm: authored scalp overlap remains; no zero-intersection/follicle-root quality claim.

The result has a feathered hairline, visible ears and coherent silver mass, but remains denser/smoother than the portrait's loose waves. Final hair design is still open.

## Delivered skin

`refine-scholar-skin-color.py` blends the unchanged2048source diffuse at0.45 with linear tint(0.78,0.82,0.90). A smooth world-position mask suppresses source contribution at the rear/nape to remove printed stubble. A1024COLOR-onlyUV0 bake becomes the supported active base color. Original procedural input is retained separately; normal/roughness/iris, material assignments, geometry/UV/weights/morphs are unchanged. No additional lighting is baked, but the source authored diffuse is not established as a clean/de-lit scan. This adds color/age variation, not sculpted age anatomy or finished skin.

## Preservation and metrics

Canonical original blockout and face-only studies, approved portrait/liveLewis at1.05pace, all eleven genuine controls and64joints remain. Public weightedGLB now13,709,032bytes,66,767exported vertices/88,423triangles and seven embedded images. It replaces the previous119,835vertices/177,239triangles by retiring dense crown guides, rather than accumulating more tubes. Tests validate preserved components and every active vertex's skinning; the obsolete global100k-vertex floor was removed. Geometry counts do not establish appearance quality.

The game default remains portrait/liveLewis; no microphone/AI activation, live-room migration or case change. ListenerPR2's newer playback-state contract atddf2778 is under fresh review and is not covered by earlier0b2e809 approval.

## Evidence and remaining work

Standalone hair/skin validation, retained input/source hashes, actual embedded image bindings and normalized weights are checked. Browser diagnostics derive hair map count/alpha state from actual loaded materials. Final matched views:docs/assets/scholar-assets-front/profile/threequarter.png; skin component comparisons:skin-age-before/after-front/profile.png.

Still open: face/eyelid proportions, dense shaped facial beard/moustache, tailoring/oral detail, loose hair breakup and perceived full dialogue quality. November4 readiness gate and November10 custom-avatar risk remain. The playable portrait/Lewis baseline remains the fallback. This increment is not final-character approval.
