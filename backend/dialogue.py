"""Providers phrase public facts, never mutate the case or import hidden canon."""
from typing import Protocol


class DialogueProvider(Protocol):
    def respond(self, text: str, state: dict) -> str: ...


# Topic aliases contain no hidden facts. Matching operates only on released IDs.
CLUE_TOPICS = {
    "glass": ("glass", "port", "cup", "tea", "poison", "collapse", "death window"),
    "clock": ("clock", "photograph", "photo", "time of death", "9:10", "9:20"),
    "ledger": ("ledger", "dispensary", "key", "compound", "cyanide"),
    "alibi": ("recording", "alibi", "music", "pianist", "ada", "felix"),
    "note": ("letter", "dismissal", "invoice", "motive", "tray", "receipt", "9:22"),
}
SUSPECT_TOPICS = {
    "ada": ("ada", "heir"),
    "felix": ("felix", "finch", "pianist"),
    "margot": ("margot", "vale", "physician", "doctor"),
}


class MockDialogueProvider:
    """Dry, helpful Wobblebottom, constrained to the supplied public snapshot."""

    def respond(self, text: str, state: dict) -> str:
        if state["act"] == 4 and state.get("solution"):
            return state["solution"] + " Case closed. We may now return to the rather less mysterious dessert."
        lower = text.casefold().replace("spoiler-free", "")
        evidence = state.get("evidence", [])
        if any(phrase in lower for phrase in (
            "ignore", "system prompt", "hidden", "unrevealed", "spoiler",
            "killer", "murderer", "who did", "culprit", "solution",
        )):
            return "An admirably direct question. I shall reserve the culprit until the reconstruction; even a good theory must survive the evidence. Ask for a recap or examine a released clue."
        if not evidence:
            return "At present our evidence consists chiefly of excellent posture. Ask the host to begin the case and reveal a clue; I shall then have something sturdier to discuss."
        if any(word in lower for word in ("recap", "summary", "summarise", "summarize", "what do we know", "so far")):
            facts = " ".join(f"{clue['title']}: {clue.get('summary', clue['title'])}" for clue in evidence)
            return f"The record so far. {facts} Full descriptions remain in your notebook."
        if "hint" in lower or "help" in lower:
            ids = {clue["id"] for clue in evidence}
            if "note" in ids:
                return "Build one chain from the released clues: the vessel, access, the delivery window, and a reason to act. Explain the two distractions before you accuse. Certainty is more becoming than volume."
            if "alibi" in ids:
                return "Compare the released evidence for access with the released alibi. Means and opportunity deserve separate columns; an unfortunate personality is not a third column."
            if "ledger" in ids:
                return "Access is one question; opportunity is another. List what this ledger proves, and what it does not. I recommend keeping both eyebrows available."
            if "clock" in ids:
                return "Separate the drink offered from the drink consumed. Then compare the clock with the photograph; a clock that cannot keep time is a rather poor witness."
            return "Follow the vessel the victim actually drank from. A dramatic-looking glass need not be the important one. Appearance is a famously unreliable investigator."
        explicit_clue = next((clue for clue in evidence if clue["title"].casefold() in lower), None)
        if explicit_clue:
            return f"Consider {explicit_clue['title'].lower()}: {explicit_clue['description']} A useful fact, mercifully, among the opinions."
        suspect = next((s for s in state.get("suspects", [])
                        if any(topic in lower for topic in SUSPECT_TOPICS.get(s["id"], ()))), None)
        if suspect:
            relevant = [clue for clue in evidence if
                        any(topic in clue["description"].casefold() for topic in SUSPECT_TOPICS.get(suspect["id"], ()))]
            facts = " ".join(f"{clue['title']}: {clue['description']}" for clue in relevant)
            return (f"{suspect['name']}. {suspect['description']} "
                    + (facts if facts else "No released clue yet establishes this guest's part in the delivery.")
                    + " Let us distinguish evidence from a well-tailored suspicion.")
        mentioned = next((clue for clue in reversed(evidence)
                          if any(topic in lower for topic in CLUE_TOPICS.get(clue["id"], ()))), None)
        if mentioned:
            return f"Consider {mentioned['title'].lower()}: {mentioned['description']} A useful fact, mercifully, among the opinions."
        if any(topic in lower for topics in CLUE_TOPICS.values() for topic in topics):
            return "That detail is not established in the released record. Ask the host to reveal the next clue, or ask me to recap what is on the table. Guesswork is plentiful; evidence is worth waiting for."
        return "I can review a released clue, discuss a suspect's public profile, offer a hint, or recap the evidence. Kindly give me a topic; interpreting meaningful glances remains outside my fee."
