# The Last Toast at Blackthorn Manor

**Organizer/design source — contains the complete solution. Do not share this document with players before the finale.** The browser receives only gated public snapshots; this repository is an authoring workspace, not a spoiler-free player handout.

## Playable milestone

`backend/mystery.py` is the authoritative case: `last-toast-blackthorn`, version 1. The intended first rehearsal takes 20–30 minutes with a host and 2–6 guests, expandable to the prototype's room limit. Guests investigate together as dinner attendees; they are not assigned private suspect roles in this milestone. The three suspects are authored characters on the evidence board.

The host opens acts and releases clues. Wobblebottom explains already released facts, provides progressively useful hints, and performs the final reconstruction. The host's role is facilitation rather than improvising missing facts. A guest may accuse during act three, replace their vote, and compare their deduction with the fixed outcome. Votes never alter the culprit.

## Premise and tone

Lord Blackthorn collapses during a dinner at his manor. His untouched port invites an obvious theory; his tea provides the less convenient truth. Ada Blackthorn has fought with her father over the estate. Felix Finch owes him money. Dr. Margot Vale has been trusted with the family's medical supplies for years.

Detective Reginald P. Wobblebottom is competent, observant and quietly theatrical. His name supplies enough absurdity; he does not need constant food jokes or slapstick. His sarcasm punctures weak reasoning without humiliating a guest. He never invents testimony, announces a culprit early, or treats the loudest accusation as proof. Example: “Means and opportunity deserve separate columns; an unfortunate personality is not a third column.”

## Fair-play contract

- All evidence is authentic and accurately transcribed. No unseen accomplice, secret twin or unannounced supernatural rule changes the answer.
- The case asks which of the three named suspects carried out the poisoning during the observed tea-delivery window.
- A reasonable deduction combines means/access, opportunity, motive and the other suspects' alibi. A disliked victim and a suspicious manner are insufficient.
- The host must release every clue in an act before advancing. All five clues must be released before the final reconstruction.
- Clue descriptions and the solution are revealed only by the deterministic engine. Dialogue receives public facts, never the full case module.

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
| Gathering | 2–3 minutes | Create room, open TV, have guests join | Explain that clues are reliable, votes are revisable and speech is optional |
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

Next design increments: private character objectives and host-only facilitator notes in the application, richer individual questioning, optional evidence artwork, and a second case after this one passes rehearsal. Private role secrets require an explicit privacy contract and separate per-player payloads; they must never be added to a public room snapshot.
