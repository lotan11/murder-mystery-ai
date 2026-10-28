# Local TalkingHead on the game TV

This optional milestone connects the approved restrained TalkingHead animation to actual public detective dialogue. The original evidence stage remains available. No microphone or paid speech provider is involved.

## Windows setup and rehearsal

Start the repository with Windows PowerShell:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\start.ps1 -Port 8018
```

The server computer needs Windows PowerShell 5 and installed Microsoft David Desktop or Zira Desktop English voices. This game mode generates speech as needed; the separate audition's preparation command is not a prerequisite. Speech is synthesized on the server machine, then the TV browser plays the WAV with timed facial shapes after an explicit playback gesture. Other supported browsers/devices can display the TV while the backend runs on Windows.

Create an evening, open the organizer's TV link, and choose the animated detective option. Enable local voice, then begin the case or submit a question. Keep the organizer open in a second tab to pause, release clues and move between acts. Captions remain visible. Use mute/stop before switching devices to avoid two TVs speaking at once. Each TV has its own playback preference.

The TV link carries a read-only speech capability in its fragment. Share it only with the intended display. It cannot advance the case or retrieve private cards. A manually typed room-only TV URL can still show public captions and evidence; use the organizer's generated TV link for speech access.

## Limits and recovery

- The face is a licensed sample, not final Wobblebottom. David/Zira are US English demonstration voices, not the planned British character voice.
- Word starts are reported by Windows speech; durations and English mouth shapes are estimated. Reduced lip strength and upper-face expression are retained from the approved audition.
- The backend speaks its current public dialogue only. The browser cannot submit arbitrary text for synthesis. Generation is bounded and runs outside the room lock.
- Pause, disconnected state and changed dialogue/state cancel playback and suppress stale results. Muting cancels audio. Captions remain the authoritative current line.
- Missing Windows speech support, an unavailable installed voice or a rendering error leaves the game playable with captions. No external provider is used as a silent fallback.
- The feature does not add live listening, custom voice, final detective assets, premium TTS or autonomous conversation. Existing optional AI planning remains separately configured and disabled by default.

Automated browser fixtures contain synthetic tones, not real speech. Backend tests inject renderers. A real Windows generation/playback check is recorded separately in PROGRESS.md and VALIDATION.md; neither offline fixtures nor mouth movement alone establish premium voice realism.
