# Scholar hair experiment review — October 30, 2026

**Decision: rejected for public integration.** The active rig GLB, canonical Blender sources, approved portrait and Lewis voice are unchanged.

## Observed result

Two rounded/tapered tube-clump passes were rendered against the existing fitted cap. The second introduced an asymmetric up/back sweep and24mm front lift, but front/profile review still showed a helmet-like hairline, combed mass and exposed side/back wire loops. It did not match the approved Scholar's loose swept/wavy hair. The final experiment had1,500clumps/126,000vertices/117,000quads, heavier than warranted by the visual result.

Normalized existing Head weights, root-triangle correspondence and neutral/±10degree attachment checks passed. That is technical attachment evidence, not an appearance pass. Original face, eyes, fitted facial groom and cap geometry were preserved in the experiment; cap color and legacy crown-guide retirement were experiment-only changes. Neither a public asset nor builder hook was installed.

Tracked evidence: `hair-prototype-rejected-2026-10-30.json` and `../assets/rejected-hair-wave-front.png` / `rejected-hair-wave-profile.png`. The JSON records the active publicGLB hash and byte-identical comparison with the preceding commit. Experimental source, render caller and other views remain in ignored local `data/character-tools/hair-experiment/`; they are not a distributed or activated hairstyle.

## Next approach

Evaluate an existing hair mesh/material with an appropriate swept silhouette, then fit/recolor/bind it to the actual Scholar and inspect its real exportedGLB before reuse. The official [hair01 inventory](https://static.makehumancommunity.org/assets/assetpacks/hair01.html) lists Cortu short-messy hair asCC0 and describes the pack as mainly low-poly/stylized. The [system-asset inventory](https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html) lists furtherCC0 hair assets. These are source leads, not a selection or a premium-quality claim. No asset pack or individual hair asset was downloaded this run. Inspect individual-file license/source hashes and actual appearance before choosing one. No purchase/provider is needed to assess these candidates.

## Comparison tooling delivered

Face close-up now shows a display-only crop of the same approved portrait beside the development model. The SVG viewBox230−45 570680 encloses the source image's full hair, ears, beard/chin and a little collar; meet letterboxing keeps that region visible on phones. Full bust, camera Reset and model changes restore the original portrait. No new portrait image/candidate, photo editing or identity replacement. Actual desktop/mobile screenshots reviewed; the browser test waits for a post-resize GPU draw before capturing the model.

## Deadline

This experiment does not advance final-groom readiness. Hair, facial proportions, eyelids, tailoring/oral detail and perceived speech quality remain before the November4 readiness gate. A finished custom avatar remains at risk for November10; keep the playable approved portrait/liveLewis baseline. Do not count geometry or passed attachment checks as finished likeness.
