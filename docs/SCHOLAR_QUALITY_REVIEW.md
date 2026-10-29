# Scholar character quality review — October 29, 2026

**Status: functional development rig, substantially short of the approved premium stylized-realistic likeness.** Keep the approved Scholar portrait and Lewis at +5% playback as the live game presentation. This review concerns the 3D realization of the settled selection; it does not reopen casting.

## Evidence inspected

- Approved identity: [vale.png](../frontend/public/casting/vale.png).
- Current close-up: [rig-study-mouth-lining.png](assets/rig-study-mouth-lining.png), an actual open-jaw Blender render.
- Authoring: [scholar.json](../assets/character-production/scholar.json), [build-scholar.py](../scripts/build-scholar.py), [bound-study builder](../scripts/build-scholar-bound-study.py), and [rig brief](SCHOLAR_RIG_BRIEF.md).
- Export: JSON/material inventory inside `frontend/public/character-lab/scholar-rig-study.glb`.

The recent `frontend/test-results/scholar-timed-study.png` was absent at review time. No live playback or listening was performed in this review; a still image and inventory cannot establish natural lip-sync. Portrait lighting, head angle and camera differ from the studio render, so exact proportion changes need matched-camera comparisons.

## Highest-impact next edits

| Priority | Observed gap against the approved portrait | Practical source work and acceptance evidence |
| --- | --- | --- |
| P0 | Silver swept hair and a dense, shaped moustache/beard are major identity cues in the portrait. The model has a dark cap, separated bright wire-like hair guides, sparse curled beard strands and visible skin gaps. | Replace the visible guide aesthetic with layered, directionally groomed clumps/cards and a lighter continuous underlying hair mass. Shape the moustache, cheek transition and chin beard as coherent silhouettes; taper tips and vary width rather than merely adding more identical tubes. Use `build-scholar.py` groom sections; retain reproducible settings/weights. Compare front, three-quarter and profile at TV framing and close range. No scalp gaps, floating beard or beard crossing the lips during jaw/rounding/compression. |
| P0 | The model's smooth face, uniform blue eyes and heavy lid contour read as a generic aged mannequin. The portrait has more angular nose/cheek definition, clearer eyelid structure and a composed, attentive expression. | First match camera/head orientation. Then adjust eyelid contour, iris visibility, nose bridge/tip/alar width and cheek planes in small reversible steps through `scholar.json`/anatomical targets. Available local nose width/volume targets support experimentation; do not infer a precise weight from the portrait alone. Preserve neutral topology and rebuild derived facial studies. Gate on side-by-side neutral views and blink/lip-seal checks, not a higher morph count. |
| P1 | Skin lacks the portrait's subtle color variation, wrinkles and surface response; eyes lack convincing iris/corneal detail. | Bake/export UV-based skin base-color, tangent normal and roughness detail, with restrained age variation and no painted lighting. Improve iris detail and corneal highlights without enlarging/cartooning the eyes. Inspect the actual GLB and browser, not only Cycles. Keep the existing skin tone/identity target rather than adding indiscriminate noise. |
| P1 | Tailoring is still flat polygon blocking: broad shell shoulders, planar lapels/collar, plain tie and waistcoat. The portrait's fitted layered tweed, patterned tie, fabric thickness and small accessories carry much of its premium quality. | Refine collar/lapel thickness, overlap and shoulder silhouette before adding accessories. Give waistcoat/tie distinct cloth texture and a controlled weave scale; add restrained seams/buttons/pocket detail after silhouette approval. Current wardrobe is rigid to Spine2: inspect head-turn collar clearance and make no cloth/shoulder-deformation claim. |
| P1 | Oral lining now distinguishes the existing cavity, but the open mouth remains a dark opening without finished dentition/tongue detail. Eleven controls and the fixed timing study are not a full phonetic face. | Add and fit actual interior detail only where visible at restrained speech weights, then validate jaw, lip seal, rounding and compression in frontal/profile views. Extend genuine mouth shapes after anatomical inspection; do not add empty viseme names. Review short/long real Lewis playback at the approved pace for intersections, floating facial hair and exaggerated motion. |

## Export detail is a real blocker

`build-scholar.py` connects a procedural Noise node through Bump to skin Normal and sets Principled subsurface weight. At the initial inspection before the skin-bake increment, **Neutral aged skin blockout** had only constant base color, metallic factor and roughness: no base-color texture, normal texture, roughness texture or equivalent subsurface extension. That initial export did not deliver those Blender node effects as equivalent runtime skin detail. That initial export had one image/texture, used by **Brown tweed blocking**; the waistcoat, tie, hair and eyes remain constant-color materials. Thus a nicer Cycles render alone cannot close the browser quality gap. Bake supported PBR maps and verify their actual GLB bindings and browser appearance. Keep neutral studio comparison first; a warm key/cool rim presentation pass should follow, not conceal, the material/likeness work.

## Readiness and November 10 risk

The selected identity is recognizable through glasses, age, hair color and dress, but the groom, face/material finish and tailoring are not yet close enough for final character approval. A working skeleton, real morphs, model timing and passing tests are technical progress, not art completion. The November 4 readiness gate in [INTEGRATION_PLAN.md](INTEGRATION_PLAN.md) must include matched-view likeness and actual perceived speech review. Final live activation still requires those quality gates and a dinner/device rehearsal; retain portrait/live Lewis if the custom avatar is not ready. No purchase, paid conversion, public deployment or new casting decision is recommended by this review.

## Follow-up: portable skin grain delivered

The subsequent skin-bake increment now embeds three1K supported maps and browser verification confirms decoded color/normal/roughness on the loaded material. Genuine normal variation is measured against a bump-disabled bake; source normal/base-color hashes match GLB images. This resolves delivery of the existing subtle grain. It does not add authored wrinkles, scan detail, subsurface response or close the groom/face/wardrobe likeness gaps above. Keep those P0 visual gates; the character is still a development rig.
