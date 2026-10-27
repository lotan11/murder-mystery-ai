# The Last Toast at Blackthorn Manor

**Organizer/design source — contains the complete solution. Do not share this document with players before the finale.** The browser receives only gated public snapshots; this repository is an authoring workspace, not a spoiler-free player handout.

## Playable milestone

`backend/mystery.py` is the authoritative case: `last-toast-blackthorn`, version 1. The intended first rehearsal takes 20–30 minutes with a host and 2–6 guests, expandable to the prototype's room limit. M2 adds private role cards in `backend/characters.py`: the first three guest identities receive Ada, Felix and Margot in join order; additional guests become visiting investigators. Named roles are exclusive, while investigators are deliberately non-exclusive. The host may reassign roles only in the unpaused lobby. With fewer than three guests, unassigned suspects still exist in the authored case; every role need not have a performer.

The host opens acts and releases clues. Wobblebottom explains already released facts, provides progressively useful hints, and performs the final reconstruction. The host's role is facilitation rather than improvising missing facts. A guest may accuse during act three, replace their vote, and compare their deduction with the fixed outcome. Votes never alter the culprit.

## Premise and tone

Lord Blackthorn collapses during a dinner at his manor. His untouched port invites an obvious theory; his tea provides the less convenient truth. Ada Blackthorn has fought with her father over the estate. Felix Finch owes him money. Dr. Margot Vale has been trusted with the family's medical supplies for years.

Detective Reginald P. Wobblebottom is competent, observant and quietly theatrical. His name supplies enough absurdity; he does not need constant food jokes or slapstick. His sarcasm punctures weak reasoning without humiliating a guest. He never invents testimony, announces a culprit early, or treats the loudest accusation as proof. Example: “Means and opportunity deserve separate columns; an unfortunate personality is not a third column.”

## Fair-play contract

- All evidence is authentic and accurately transcribed. No unseen accomplice, secret twin or unannounced supernatural rule changes the answer.
- The case asks which of the three named suspects carried out the poisoning during the observed tea-delivery window.
- A reasonable deduction combines means/access, opportunity, motive and the other suspects' alibi. A disliked victim and a suspicious manner are insufficient.
- The host must release every clue in an act before advancing. All five clues must be released before the final reconstruction.
- Public clue descriptions and the final reconstruction are released only by the deterministic engine. Dialogue receives public facts, never the full case module or private role cards.
- Margot's performer privately knows the culprit from the outset. Their task is dramatic participation, not a fair guessing contest; investigators and the other performers still deduce from released evidence. No private card creates a new admissible clue.
- Players may decline questions. Nobody must fabricate testimony, override a released clue or invent an accomplice to protect a role.

## Canonical timeline — spoilers

| Time | Established event | Source |
| --- | --- | --- |
| Tuesday | Vale signs for a cyanide compound and holds the dispensary's only key; no legitimate use explains the missing compound | Physician's ledger, act two |
| Afternoon | Vale acknowledges Blackthorn's letter threatening to expose her forged invoices the next morning | Dismissal letter, act three |
| 9:10 shown on clock | Clock's hands are stopped; its spring had broken that morning | Stopped clock, act one |
| 9:15–9:30 | Ada and Felix speak continuously in the music room, establishing their presence there | Music-room recording, act two |
| 9:20 | Timestamped photograph shows Blackthorn alive | Stopped clock, act one |
| 9:21 | Steward watches fresh tea being poured | Dismissal letter/tray record, act three |
| 9:22 | Vale signs for the tray and alone carries it to Blackthorn | Dismissal letter/tray record, act three |
| 9:23 | Steward sees Blackthorn drink the delivered tea | Untouched port, act one |
| 9:27 | Blackthorn collapses | Untouched port, act one |

The laboratory report identifies poison in the teacup and none in the port. The report is accepted as completed case evidence; this is a compressed theatrical investigation rather than a real-time forensic simulation.

## Act plan and host cues

| Phase | Suggested time | Host action | Discussion objective |
| --- | --- | --- | --- |
| Gathering | 3–4 minutes | Create room, open TV, have guests join and privately read cards; optionally share introductions | Explain that clues are reliable, votes are revisable, speech is optional and one actor knows their guilt |
| Act one: the discovery | 5–6 minutes | Start; reveal the port; allow discussion; reveal the clock | Distinguish the consumed drink from the offered port and reject the clock as a death timestamp |
| Act two: the contradictions | 6–8 minutes | Reveal the ledger, then the recording | Separate access from opportunity and compare both with the other suspects' alibi |
| Act three: the accusation | 5–7 minutes | Reveal the letter/tray record; invite each guest's reasoned vote | Complete motive and opportunity; ask guests to explain both red herrings |
| Reconstruction | 2–3 minutes | Resolve the case after all clues | Reveal Vale, compare reasoning, and collect feedback |

These are facilitation suggestions, not a countdown. Pause freezes progression, dialogue and voting so a meal or discussion can take priority. If the group stalls, ask Wobblebottom for a spoiler-free hint or recap rather than revealing a fact out of order.

## Solution and red herrings — spoilers

**Dr. Margot Vale poisoned the tea to prevent exposure of forged invoices.** The teacup identifies the means. The ledger establishes her access to the missing compound. Ada and Felix's continuous recording clears them during delivery. The acknowledged letter establishes an immediate motive; sole custody of the freshly poured tea at 9:22 establishes opportunity before it is drunk at 9:23.

The port is a wrong-vessel distraction, not a second poisoning. The stopped clock is a broken object, not a secret time-of-death signal or a fabricated earlier murder. Both can be dismissed using act-one evidence, without an explanation invented during the finale.

## Dialogue and integration rules

The current provider is deterministic. A referenced released clue can be revisited even after later clues appear. Suspect questions return public profiles and relevant released facts; recap uses each released clue's canon-authored `summary`, with full descriptions kept in the guest notebook. The complete recap stays within 650 characters and the reconstruction within 700 for TV captions. Hints use the released clue IDs rather than act number alone, avoiding an act-opening spoiler. Requests to ignore rules or reveal the culprit get a courteous refusal until act four.

An optional future AI provider may change phrasing, not facts or state. It must accept only the public snapshot, return validated dialogue/performance data, time out safely, and fall back to this provider. Microphone capture, speaker identification, custom TTS and viseme lip sync remain separate integrations; none is implied by idle avatar movement or browser speech.

## Rehearsal acceptance and feedback

The first complete rehearsal succeeds when every guest can join, read prior evidence, ask a relevant question, vote, recover after reload, and explain the final chain without the host inventing facts. Record completion time, which clue caused confusion, whether the red herrings felt fair, TV readability, phone friction, and whether the detective's tone helped discussion. Do not describe the story as playtested until a human group has completed that rehearsal.

Next design increments: richer individual questioning, host-only facilitator notes in the application, optional evidence artwork, and a second case after this one passes rehearsal. Human four-player rehearsal remains pending; automated privacy checks do not establish that the dinner pacing works.


## M2 character participation and privacy — spoilers

`backend/characters.py` is the authoritative role-card source. The card is an acting aid, not a second mystery engine. Each has one safe public introduction suggestion, a private brief, three objectives and short performance guidance. These objectives are conversation prompts; the game does not claim to score or verify their completion.

| Role | Private dramatic purpose | Place in the investigation |
| --- | --- | --- |
| Ada Blackthorn | Be seen as a person beyond the inheritance; acknowledge family hurt | Innocent performer who reasons from the released record |
| Felix Finch | Admit financial pressure without treating embarrassment as guilt | Innocent performer who reasons from the released record |
| Dr. Margot Vale | Maintain composure while helping an earned reconstruction | Knows privately that they poisoned the tea to conceal forged invoices; actor rather than an unspoiled solver |
| Visiting investigator | Bring quieter guests into the conversation and examine proof | Non-suspect, no advance knowledge or hidden evidence; multiple players may hold this role |

The culprit card explicitly names guilt, method and motive for its authenticated recipient. This is intentional private information, not a premature public reveal. Ada and Felix's added personal stakes do not establish an unreleased alibi, time or witness. Private cards must never enter the public room snapshot, the detective's dialogue context, the host view, the TV, or another guest's connection. Role identity and whether a guest has introduced themselves may be public; private briefs and objectives may not.

### Optional introduction round

In the gathering or act one, allow roughly 20–30 seconds per guest to introduce their character. The provided public introduction is safe to read aloud. A guest can edit it, submit an intentional public introduction of up to 240 characters, or simply pass. The submitted text is voluntary public speech: the UI should warn players not to paste the private brief. The application does not automatically publish private cards or treat an introduction as verified case evidence. Replacing one's introduction updates that guest's entry rather than inventing a second speaker. Introductions never block the host's act controls.

Late joiners receive whichever named roles remain; after the case starts, the host cannot reassign characters. Reload and server restart retain the assignment and private delivery. Reset retains party identities and assignments, while clearing introductions and votes so the group can replay deliberately.

### Accusations and finale

During act three, guests may submit a suspect and an optional rationale of up to 300 characters. A replacement accusation replaces their own previous choice and reasoning. Before resolution, the player's reasoning belongs only to that player; the public view shows aggregate votes. At the finale, the application may publish all submitted accusations and rationales so the table can compare reasoning with the fixed reconstruction. Role objectives never change the culprit, clue order or the reliability of the evidence.

The host should invite Margot's performer to acknowledge the established chain after the reconstruction, without requiring a theatrical confession. For a four-player rehearsal, use three suspect performers and one visiting investigator; record whether the guilty actor still enjoyed participation and whether other players understood the distinction between roleplay and evidence.
