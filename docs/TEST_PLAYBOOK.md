# Playable milestone test guide

Use the Windows instructions in the root README. No AI key or microphone is needed. Keep the host browser open and use its links to connect the TV and phones. For devices on the same Wi-Fi, start with `-Lan` and create the room using the computer's LAN address.

## M1 rehearsal (20–30 minutes)

1. Create a new evening. Open the TV stage and join two guest notebooks with different names.
2. Begin the case. Check that Next act is disabled before the host releases all current clues.
3. Reveal the two act-one clues and discuss the vessel and timeline. Ask the detective about the port, the clock, a recap and a hint. Only released evidence should inform answers.
4. Pause the evening. Guest questioning and host progression should be unavailable. Resume and finish act two.
5. During act three, each guest accuses a suspect. Changing a vote should replace that guest's prior vote.
6. Reload a guest screen; it should remain joined once connected. Reload the TV; it should show the same act and latest clue.
7. Stop the server with Ctrl+C. Restart with `start.ps1 -SkipSetup` and revisit the existing links in the same browsers. Progress, guest identities, votes and host access should recover from the local database.
8. Release the final clue and resolve the case. Check that all screens agree on the reconstruction.
9. Reset only when ready to replay: reset clears case progress/votes while preserving the party and access credentials.

## Feedback to capture

- Device/browser and whether it was a real phone/TV or a test viewport.
- Where players became confused, idle or frustrated; exact clue or screen.
- Whether the final deduction felt earned before the reveal.
- Text readability at dining/TV distance and any audio/echo problems.
- Any unexpected disconnect, lost identity or progress discrepancy.

Report feedback in this chat; the lead should update `PROGRESS.md` and the task board rather than create an unrelated specification elsewhere. Do not post host or guest bearer tokens in public issues.

The automation validates software behavior; only a real dinner rehearsal validates pacing and room readability. The complete solution and timeline are documented in `GAME_DESIGN.md` (spoilers).
