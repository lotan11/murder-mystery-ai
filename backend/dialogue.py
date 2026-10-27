"""Dialogue interface. A future AI adapter may phrase facts, never mutate the engine."""
from typing import Protocol

class DialogueProvider(Protocol):
    def respond(self, text: str, state: dict) -> str: ...

class MockDialogueProvider:
    def respond(self, text: str, state: dict) -> str:
        if state["act"] == 4:
            return state["solution"] + " Case closed. The wallpaper remains innocent, against all expectations."
        if not state["evidence"]:
            return "An intriguing theory. At present our evidence consists chiefly of enthusiasm. Ask the organizer to open the case and reveal a clue."
        if any(word in text.lower() for word in ("killer", "murderer", "who did", "solution", "ignore")):
            return "You want the culprit already? Splendid ambition. Collect the evidence first; even my moustache observes due process."
        clue = state["evidence"][-1]
        return f"Consider {clue['title'].lower()}: {clue['description']} A fact, mercifully, among all these opinions."
