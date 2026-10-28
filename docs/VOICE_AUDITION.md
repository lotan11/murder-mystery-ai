# TalkingHead voice audition

Open `/?view=audition` on the running application. Choose **Existing voice**, a line, then **Play audition**. Stop or change voice to interrupt playback.

## Windows preparation

From the repository folder, run once:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\prepare-audition.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File .\start.ps1 -Port 8018
```

The preparation script uses installed Microsoft David Desktop and Zira Desktop voices to create six local WAV recordings in ignored `data/audition/`. It requires Windows desktop speech support. Missing voices produce a preparation error; the game remains runnable without the audition recordings. No API key or microphone is required. Samples are prepared locally rather than redistributed in Git.

## What is real

- The MIT TalkingHead library renders the locally bundled CC0 `mpfb.glb` sample with actual facial morph animation.
- WAV recordings contain actual Windows synthesized speech. SAPI provides word-start times; word durations are estimates. TalkingHead derives English mouth shapes from words and timings.
- Stop, voice changes and leaving the page cancel playback. If WebGL fails, recordings remain available in explicitly labeled audio-only mode.

## What is provisional

The clothed female sample is an animation compatibility placeholder, **not Reginald's final appearance**. David and Zira are installed US English demonstration voices, not the proposed premium British detective voice. This separate audition does not replace the game's procedural detective or connect live AI replies to TalkingHead. External voice-reference links do not generate audio or incur charges. No microphone or live premium voice provider is configured.

Asset provenance and redistribution terms are in [AVATAR_ASSETS.md](AVATAR_ASSETS.md). The test preparation script deliberately creates synthetic tones, not speech; browser tests use those isolated files to verify actual mesh movement without paid services or Windows-only voices. Listen to the real Windows recordings for a subjective voice/synchronization review.

## Restrained performance revision

User feedback accepted the TalkingHead approach but found the lips exaggerated. Audition visemes now use 45% of library strength, capped at 0.38, while keeping original word timing and easing. Gentle speech-weighted eyebrow/eye expression fades back at rest; head movement is slightly increased. These are artistic adjustments, not improved phoneme timing or a final character rig.
