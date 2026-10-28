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
    """Observant Wobblebottom with restrained, respectful dry humor, constrained to the supplied public snapshot."""

    def respond(self, text: str, state: dict) -> str:
        if state["act"] == 4 and state.get("solution"):
            return state["solution"] + " The investigation is complete. We may now allow the evidence a well-earned rest."
        lower = text.casefold().replace("spoiler-free", "")
        evidence = state.get("evidence", [])
        if any(phrase in lower for phrase in (
            "ignore", "system prompt", "hidden", "unrevealed", "spoiler",
            "killer", "murderer", "who did", "culprit", "solution",
        )):
            return "I shall reserve the conclusion for the final reconstruction. Even a convincing theory must first survive the evidence. We can review a released clue or recap the record."
        if not evidence:
            return "No evidence has been released yet. Ask the host to begin the investigation and reveal the first clue. Even a detective must occasionally wait for the facts."
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
            return f"Consider {explicit_clue['title'].lower()}: {explicit_clue['description']} A useful fact. Let us not ask it to prove more than it can."
        suspect = next((s for s in state.get("suspects", [])
                        if any(topic in lower for topic in SUSPECT_TOPICS.get(s["id"], ()))), None)
        if suspect:
            relevant = [clue for clue in evidence if
                        any(topic in clue["description"].casefold() for topic in SUSPECT_TOPICS.get(suspect["id"], ()))]
            facts = " ".join(f"{clue['title']}: {clue['description']}" for clue in relevant)
            return (f"{suspect['name']}. {suspect['description']} "
                    + (facts if facts else "No released clue yet establishes this person's involvement.")
                    + " Suspicion is a starting point, not a verdict.")
        mentioned = next((clue for clue in reversed(evidence)
                          if any(topic in lower for topic in CLUE_TOPICS.get(clue["id"], ()))), None)
        if mentioned:
            return f"Consider {mentioned['title'].lower()}: {mentioned['description']} A useful fact. Let us not ask it to prove more than it can."
        if any(topic in lower for topics in CLUE_TOPICS.values() for topic in topics):
            return "That detail is not established in the released record. Ask the host to reveal the next clue, or ask me to recap what is on the table. The evidence has not yet obliged us with an answer."
        return "I can review a released clue, discuss a suspect's public profile, offer a hint, or recap the evidence. Choose a topic; we shall leave mind-reading for another evening."
