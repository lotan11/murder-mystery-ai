# Playable milestone test guide

Use the Windows instructions in the root README. No AI key or microphone is needed. Keep the host browser open and use its links to connect the TV and phones. For devices on the same Wi-Fi, start with `-Lan` and create the room using the computer's LAN address.

## Current character rehearsal (20–30 minutes)

1. Create a new evening. Open the TV stage and join four guest notebooks with different names. The first three receive suspect roles; the fourth receives a visiting investigator card. Each guest may reveal their private brief on their own device. The culprit player has actor knowledge; the remaining guests solve the case.
2. Check that private briefs appear only on their owners' devices. Optionally change roles in the host lobby; free an occupied role by assigning its current owner to investigator first. Invite each guest to submit a short public introduction, then begin. Check that Next act is disabled before all current clues are released.
3. Reveal the two act-one clues and discuss the vessel and timeline. Ask the detective about the port, the clock, a recap and a hint. Only released evidence should inform answers.
4. Pause the evening. Guest questioning and host progression should be unavailable. Resume and finish act two.
5. During act three, each guest accuses a suspect and may add a reason. Changing a vote replaces the prior vote. Reasons should remain private to the submitting guest before the finale.
6. Reload a guest screen; it should restore identity, character and submitted information, with the private brief hidden again. Reload the TV; it should show the same act and latest clue.
7. Stop the server with Ctrl+C. Restart with `start.ps1 -SkipSetup` and revisit the existing links in the same browsers. Progress, guest identities, votes and host access should recover from the local database.
8. Release the final clue and resolve the case. Check that all screens agree on the reconstruction and the shared accusation reasons. Invite the culprit actor to acknowledge how the evidence explains their role.
9. Reset only when ready to replay: reset clears case progress, introductions, votes and reasons while preserving the party, character assignments and access credentials.

For multiple simulated players on one computer, use separate browser profiles or browsers; normal tabs share identity. The automated test uses four independent guest browser contexts.

## Feedback to capture

- Device/browser and whether it was a real phone/TV or a test viewport.
- Where players became confused, idle or frustrated; exact clue or screen.
- Whether the final deduction felt earned before the reveal.
- Text readability at dining/TV distance and any audio/echo problems.
- Any unexpected disconnect, lost identity or progress discrepancy.

Report feedback in this chat; the lead should update `PROGRESS.md` and the task board rather than create an unrelated specification elsewhere. Do not post host or guest bearer tokens in public issues.

The automation validates software behavior; only a real dinner rehearsal validates pacing and room readability. The complete solution and timeline are documented in `GAME_DESIGN.md` (spoilers).
