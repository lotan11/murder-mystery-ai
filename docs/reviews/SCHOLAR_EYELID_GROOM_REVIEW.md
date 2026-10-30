# October 30 eyelid and facial-groom experiments

These are isolated development experiments, not changes to the public rig or the approved game portrait/Lewis presentation. Root inspected actual front/profile renders, the closed blink and the groom in Three.js. No paid assets/providers were used.

## Eyelid preview: retain for guarded integration

A localized +0.20 contribution from the existing pinned MPFB eye-height targets makes the heavy eyelids slightly more alert. Reducing the existing target would close the eyes further. The preview changes 419 head vertices, at most 0.560 mm; its eye-local mask protects the central/lower nose and lips. Source/head correspondence error is at most 0.128 micrometres. The same offset is added to Basis and all eleven shapes: deformation deltas, UVs, weights, eyes and skeleton remain unchanged. Reported minimum face-normal dot is 0.9943; no flipped/degenerate faces. Root visually confirmed the blink still closes. These checks do not certify physical eye contact or final likeness.

[Before](../assets/eyelid-preview-before-front.png), [preview](../assets/eyelid-preview-after-front.png), [closed blink](../assets/eyelid-preview-closedblink.png).

Disposition: modest visual improvement, accepted as a preview only. It is not in the public GLB or builder. Next integration must run before facial-groom fitting and explicitly account for the localized neutral offsets in the original-head preservation test, retaining all other geometry/deformation guards. Local reproducible evidence: data/character-tools/eyelid-preview; ignored authoring dependencies are required.

## Facial groom: reject

Wider, slightly raised cards with a project-authored strand-alpha atlas retained the same 2,200 beard and 800 moustache clumps. Anatomical weights, four genuinely nonzero mouth targets, outward attachment across five poses and a 1.66 mm lip-proxy clearance passed. In the browser, alpha cutoff 0.5 removed fine detail under minification; 0.25 restored coverage but produced grey sticker-like patches around the moustache and chin. Root agrees with the visual rejection. No helper, atlas, model or source change is activated.

[Existing groom](../assets/groom-card-before-front.png), [rejected cards in browser](../assets/groom-card-rejected-front.png).

Selected community beard candidates were also excluded: individual OBJ/MHCLO headers contained AGPL3 or conflicting/missing material provenance despite CC0 catalog labels. They remain ignored and were not imported or redistributed. Next groom work should improve natural silhouette, strand grouping and material appearance rather than merely adding density.

## Schedule

The existing game, real local Lewis voice at 1.05 playback pace and approved portrait remain the stable demonstration. Finished likeness, natural facial groom, tailoring, oral detail and perceived speech quality remain open. November 4 is the animated-character readiness gate; November 10 integration still depends on preserving the playable fallback.

## Subsequent guarded integration

The accepted eyelid preview is now integrated into the separate weighted study. Reproducible helper and explicit neutraloffset/protected-data evidence accompany the strict headmultiset guard; canonicalstatic/face-onlystudies stay unchanged. Actualbrowser [neutral](../assets/eyelid-runtime-neutral.png) and [closedblink](../assets/eyelid-runtime-blink.png) reviewed. LocalLewis1.05pitchpreserved/Stopneutral and all16assetchecks pass. Face/groom/wardrobe remain unfinished. The widercardgroom is still rejected.
