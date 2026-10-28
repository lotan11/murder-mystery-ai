"""Providers phrase public facts, never mutate the case or import hidden canon."""
from typing import Protocol
from .case_package import CASE


class DialogueProvider(Protocol):
    def respond(self, text: str, state: dict) -> str: ...


# Topic matching and authored hints belong to the case, not the detective's personality.
CLUE_TOPICS = {clue['id']: tuple(clue['topics']) for clue in CASE['evidence']}
SUSPECT_TOPICS = {suspect['id']: tuple(suspect['topics']) for suspect in CASE['suspects']}
CLUE_HINTS = {clue['id']: clue['hint'] for clue in CASE['evidence']}


class MockDialogueProvider:
    """Serious, measured Wobblebottom, constrained to the supplied public snapshot."""

    def respond(self, text: str, state: dict) -> str:
        if state["act"] == 4 and state.get("solution"):
            return state["solution"] + " The investigation is complete."
        lower = text.casefold().replace("spoiler-free", "")
        evidence = state.get("evidence", [])
        if any(phrase in lower for phrase in (
            "ignore", "system prompt", "hidden", "unrevealed", "spoiler",
            "killer", "murderer", "who did", "culprit", "solution",
        )):
            return "The conclusion will be presented during the final reconstruction. For now, we can review the released evidence or examine a specific clue."
        if not evidence:
            return "No evidence has been released yet. Ask the host to begin the investigation and reveal the first clue."
        if any(word in lower for word in ("recap", "summary", "summarise", "summarize", "what do we know", "so far")):
            facts = " ".join(f"{clue['title']}: {clue.get('summary', clue['title'])}" for clue in evidence)
            return f"The record so far. {facts} Full descriptions remain in your notebook."
        if "hint" in lower or "help" in lower:
            for clue in reversed(evidence):
                if clue['id'] in CLUE_HINTS:
                    return CLUE_HINTS[clue['id']]
            return "Review the released evidence and distinguish established facts from assumptions."
        explicit_clue = next((clue for clue in evidence if clue["title"].casefold() in lower), None)
        if explicit_clue:
            return f"Consider {explicit_clue['title'].lower()}: {explicit_clue['description']} Consider what this establishes and what remains uncertain."
        suspect = next((s for s in state.get("suspects", [])
                        if any(topic in lower for topic in SUSPECT_TOPICS.get(s["id"], ()))), None)
        if suspect:
            relevant = [clue for clue in evidence if
                        any(topic in clue["description"].casefold() for topic in SUSPECT_TOPICS.get(suspect["id"], ()))]
            facts = " ".join(f"{clue['title']}: {clue['description']}" for clue in relevant)
            return (f"{suspect['name']}. {suspect['description']} "
                    + (facts if facts else "No released clue yet establishes this person's involvement.")
                    + " We should distinguish established evidence from suspicion.")
        mentioned = next((clue for clue in reversed(evidence)
                          if any(topic in lower for topic in CLUE_TOPICS.get(clue["id"], ()))), None)
        if mentioned:
            return f"Consider {mentioned['title'].lower()}: {mentioned['description']} Consider what this establishes and what remains uncertain."
        if any(topic in lower for topics in CLUE_TOPICS.values() for topic in topics):
            return "That detail is not established in the released record. Ask the host to reveal the next clue, or ask me to recap what is on the table. Further conclusions require additional evidence."
        return "I can review a released clue, discuss a suspect's public profile, offer a hint, or recap the evidence. Please choose a topic to examine."
