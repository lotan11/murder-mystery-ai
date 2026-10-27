"""Authored M2 role cards. Deliver only through a guest's authenticated projection.

Public introductions are suggestions, not automatic public announcements. Private
briefs are dramatic context, never additional admissible evidence or model context.
"""

CHARACTERS = {
    "ada": {
        "id": "ada",
        "name": "Ada Blackthorn",
        "public_intro": "I am Ada Blackthorn, Lord Blackthorn's daughter, and I would appreciate an evening without assumptions about my inheritance.",
        "private_brief": (
            "You did not kill your father. You regret how publicly you argued about the estate, "
            "but you also resent being treated as an inheritance with a pulse. Your private aim "
            "is to let someone see the person behind the family name. Discuss your feelings "
            "freely; do not invent a witness, an alibi or a document. Let the released evidence "
            "establish what happened."
        ),
        "objectives": [
            "Introduce yourself without making your inheritance your whole identity.",
            "Ask another guest to separate family conflict from proof of guilt.",
            "Explain your final deduction using two released clues.",
        ],
        "performance_notes": "Be composed, then allow a little hurt to show. You may pass on personal questions; no acting skill is required.",
    },
    "felix": {
        "id": "felix",
        "name": "Felix Finch",
        "public_intro": "I am Felix Finch, the evening's pianist, and I hope my financial reputation will not be mistaken for evidence.",
        "private_brief": (
            "You did not kill Blackthorn. You owe him money and are embarrassed that everyone "
            "seems to know it. You would like one person to remember your musicianship before "
            "your debts. Acknowledge the financial pressure if asked; embarrassment is not a "
            "confession. Do not invent a payment, a new witness or an alibi. Your final theory "
            "should come from the evidence the host releases."
        ),
        "objectives": [
            "Give the table a glimpse of your life beyond the debts.",
            "Ask which released facts establish opportunity rather than suspicion.",
            "Offer a reasoned accusation without relying on another guest's manner.",
        ],
        "performance_notes": "Use dry charm rather than a comic accent. An awkward pause is optional; fabricated testimony is not.",
    },
    "margot": {
        "id": "margot",
        "name": "Dr. Margot Vale",
        "public_intro": "I am Dr. Margot Vale, the family physician, and I suggest we approach this distressing evening with precision.",
        "private_brief": (
            "You are the culprit: you poisoned Lord Blackthorn's tea to stop him exposing your "
            "forged invoices. This is your actor's knowledge, not a fair guessing contest for "
            "you. Keep that knowledge private until the reconstruction. You may remain guarded "
            "or decline a question; you need not lie. Never invent an accomplice, falsify a "
            "released clue or change the solution. Help the others enjoy an earned deduction."
        ),
        "objectives": [
            "Introduce your professional composure without revealing your private brief.",
            "Invite the table to distinguish proven facts from accusations.",
            "At the finale, acknowledge how the released evidence establishes your guilt.",
        ],
        "performance_notes": "Play controlled concern, not a conspicuous villain. You may decline loaded questions; the game never requires a false statement.",
    },
    "investigator": {
        "id": "investigator",
        "name": "Visiting investigator",
        "public_intro": "I am a visiting investigator, here to listen carefully and ask the question everyone else has politely avoided.",
        "private_brief": (
            "You are an independent investigator, not a fourth suspect. You have no secret "
            "evidence and no advance knowledge of the culprit. Your contribution is careful "
            "listening: invite quieter guests in, ask what a clue actually proves, and keep "
            "a distinction between motive and opportunity. More than one guest may hold this "
            "role, and each may reach an independent conclusion."
        ),
        "objectives": [
            "Invite another guest to share an observation.",
            "Ask Wobblebottom about one released clue or request a hint.",
            "Submit an accusation that connects motive, access and opportunity.",
        ],
        "performance_notes": "Curiosity is sufficient; no costume or performance is required. Help the conversation rather than competing for airtime.",
    },
}
