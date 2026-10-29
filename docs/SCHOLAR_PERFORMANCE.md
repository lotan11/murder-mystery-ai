# Approved Scholar and Lewis in the playable TV

The user approved **The Scholar + Lewis with the slightly faster pace** on October 28, 2026. The TV now uses the approved Scholar concept portrait with live Lewis neural narration as an incremental presentation milestone. This portrait is not a finished 3D avatar; the working animated sample and original procedural stage remain separate selectable modes.

## How to rehearse

Start the application normally, create an evening and open the organizer-generated TV link. The selected TV presentation is Scholar. Press **Enable Lewis voice** once to permit browser audio, then advance the case or ask the detective a question from the host/guest views. Only current public detective dialogue is spoken. Pause, mute, stop and replay remain available; captions/evidence remain visible even when audio fails.

**TV presentation** lets you switch to the existing animated sample with Windows voices, or the original procedural stage. Switching stops the previous mode so there is no overlapping narration. Scholar voice starts muted on reload/reconnect and does not silently switch to another voice when unavailable.

## Exact approved pace

The approved casting source uses Kokoro `bm_lewis`, British English, synthesis speed 0.92. Live dialogue uses that same generation setting and browser playback at **1.05x with pitch preservation requested**, matching the approved audition mechanism. It is not silently replaced with a different synthesis speed or another voice. Browser pitch-preservation behavior may vary. The portrait is static; there is no claim of facial speech alignment or measured word timing.

## Optional local neural runtime

The optional casting runtime and verified model files must exist on the server computer. They were already prepared on the current development machine. To reproduce with Python 3.12:

```powershell
py -3.12 -m venv data/casting-runtime
data/casting-runtime/Scripts/python.exe -m pip install -r requirements-casting.txt
data/casting-runtime/Scripts/python.exe scripts/prepare-casting.py --download
```

Restart the game server after setup. Core application requirements and Windows SAPI remain independent. No paid provider, API key or microphone is required. The live renderer never automatically downloads models or executes client-supplied text. Pinned cached models are verified before local inference; generated files remain temporary/ignored.

## Runtime boundary

The authenticated Scholar speech endpoint accepts an empty request only, using the existing host/read-only TV speech capability. The server selects current public dialogue under the room lock, runs bounded local synthesis outside the lock, then checks room state before returning validated inline WAV audio. There is a single bounded neural generation slot, fixed voice, output/text/time limits and child cleanup. Pause or a state change rejects old results. Client cancellation and generation guards prevent delayed audio from playing after pause, mute, navigation, reset or a new line.

## Remaining character production

The Scholar concept and Lewis pace are selected/approved. The portrait presentation and live voice are real; a likeness-matched rig, realistic materials and tested facial deformation are still production work. See SCHOLAR_RIG_BRIEF.md. Do not label the existing unrelated animated sample as the finished Scholar or animate the portrait with a fake mouth. Existing subtle expression and restrained viseme settings remain the reference for the future rig.

## Optional model timing metadata

The existing authenticated public-speech endpoint may now include phoneme_timing with source kokoro-model-duration, clock audio-seconds and bounded phoneme/start/end spans. These belong to the same inference waveform. Missing timing remains compatible with older outputs; malformed present sidecars fail safely. The portrait player continues approved audio playback and ignores these optional cues. No private input, room mutation, user text synthesis endpoint or automatic 3D activation is added. A separate fixed speaking study is available in the character lab; its simplified mouth mapping is not final viseme quality.

## Repeated public speech

The server can reuse successful exact-public-text Lewis clips and their matching model cues in process memory. Default cache: four entries,32MiB serialized payload,15-minute fixed reuse lifetime; expired entries are removed on cache activity and process exit clears everything. Hits do not extend lifetime. This does not write a persistent voice library or change HTTP no-store. Authorization/pause/revision checks still run, and metadata is copied before return.

A local59-word probe observed about12.1s for the first renderer-cache miss and6ms for immediate reuse with one worker total. This does not predict another machine or speed up new/expired/evicted lines. Voice, pace and40s worker timeout remain unchanged. Restart the server after pulling backend changes to use the new process-local renderer; existing saved rooms retain their schema.
