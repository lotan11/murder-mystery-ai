# Character and voice approval audition

## Selected direction — October 28, 2026

User selected **C · The Scholar + Lewis (`bm_lewis`)** in chat. The user subsequently approved the slightly faster Lewis pace (1.05x). Proceed with The Scholar + Lewis. A finished Scholar 3D rig is not yet delivered; the approved portrait/live-voice presentation is the next incremental game integration, with existing stages preserved.

Open `/?view=casting` on the running app. Compare a character concept and a voice, choose one of three identical scenes, then press **Play scene**. Nothing plays automatically. **Add to shortlist** saves only a local browser preference; it is not approval and never changes the active game character or voice.

## Lewis pacing revision

User likes Lewis and requested a slight speed increase. Casting now opens on The Scholar + Lewis and defaults to a 1.05x playback preview (about 5% faster). The Lewis pace control can switch back to Original pace. Browser pitch preservation is requested; exact behavior depends on the browser. This changes preview playback, not source recordings or the active game voice. The user approved this 1.05x pace; live integration retains the same generation/playback mechanism. Other voice candidates remain at original playback rate.

## Prepared candidates

| Character | Art direction | Asset |
| --- | --- | --- |
| A · The Classic | Mature silver-haired detective, charcoal three-piece tailoring, quiet precision | `frontend/public/casting/ashford.png` |
| B · The Modern | Mature Black British detective, salt-and-pepper beard, navy tailoring, worldly warmth | `frontend/public/casting/mercer.png` |
| C · The Scholar | Mature detective with round spectacles, silver hair, tweed and waistcoat, intellectual warmth | `frontend/public/casting/vale.png` |

These three AI-generated stylized-realistic **concept portraits are not rigged 3D avatars**. The filename `vale` is an internal art identifier; candidate C is another interpretation of Wobblebottom, not the case's suspect Dr. Vale. See CASTING_IMAGE_PROMPTS.md for the exact shared prompt and candidate directions. All portraits were generated with the built-in image tool and saved in the project. No purchased character or third-party rig is represented as complete.

Three real locally generated British male neural voice candidates are prepared: **George (`bm_george`), Daniel (`bm_daniel`), and Lewis (`bm_lewis`)**. These are Kokoro voice IDs, not claimed performers, age guarantees or endorsements. The approval objective is a mature British detective; perceived maturity, articulation, inflection and suitability must be judged by listening. Any face may pair with any voice: nine pairings, each using the same three scenes. Audio is reused across portraits for a fair comparison; there is no duplicate synthesis disguised as a new performance.

## Identical scenes and performance direction

1. **Arrival:** “Good evening. I am Detective Reginald P. Wobblebottom. A pleasure to meet you. I trust your evening has been less eventful than mine.” Warm opening; small thought pauses; final clause understated.
2. **Evidence:** “An interesting theory. Let us see whether the evidence is prepared to support it.” A slight skeptical lift, then calm evidence-first delivery. Amusement should not dismiss a guest.
3. **Reassurance:** “Take your time. A careful answer is far more useful than a confident guess.” Softer and reassuring, without a broad smile or theatrical flourish.

Recordings use the same authored text and speed setting (0.92) for all voices. Punctuation and the model produce the current phrasing. Performance notes are directions to judge, not a claim of precise emotional control. There are no measured word timings or new lip-sync claims in this portrait-and-audio comparison. The approved existing TalkingHead mouth limit and subtle expression remain unchanged in the playable TV view.

## Preparation on another machine

The game server does not require Kokoro, model weights or the optional runtime. It remains runnable with Windows SAPI and the existing avatar. To regenerate the audition in a separate environment (Python 3.12):

```powershell
py -3.12 -m venv data/casting-runtime
data/casting-runtime/Scripts/python.exe -m pip install -r requirements-casting.txt
data/casting-runtime/Scripts/python.exe scripts/prepare-casting.py --download
```

The explicit `--download` retrieves two public model assets from the pinned upstream GitHub release and verifies byte sizes and SHA-256 hashes before use (about 354 MB total). Inference then runs locally. No API key, paid provider, microphone or guest data is used. Models/runtime live in ignored `data/casting-models/` and `data/casting-runtime/`; the nine WAVs and manifest live in ignored `data/casting/`. A fresh clone without generated recordings shows a clear unavailable state, never a substituted US voice.

## Sources and licensing provenance

- Voice catalog and British voice IDs: [official Kokoro VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md).
- Model: [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M), Apache-2.0 per its model card.
- Core runtime: [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx), MIT. [Pinned official model release](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.1).
- Optional dependencies, including phonemizer/eSpeak, retain their respective licenses, including GPLv3+. The whole optional runtime is not described as MIT. Model weights and dependency binaries are not redistributed in the repository.

The generator and controlled API provenance record source versions, speed, sample rate and SHA-256 hashes. API routes serve only these fixed public authored scenes after validating the manifest and WAV data; no arbitrary text synthesis or room data access is added.

## Approval boundary

Default personality has returned to respectful, playfully sarcastic dry humor under the latest user direction. No slapstick, exaggerated mouth shapes, cartoon animation, new game avatar or new active game voice has been introduced. The Scholar + Lewis pairing is selected; the +5% pace is approved, while production of the finished rig remains pending. After approval, production work can build/license the selected 3D rig and connect the selected voice with properly validated speech alignment; that is a separate activation step.
