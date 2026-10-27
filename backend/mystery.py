"""Canonical mystery facts. Never send unrevealed descriptions or solution to clients."""
TITLE = "The Last Toast at Blackwood Manor"
SUSPECTS = [
    {"id": "ada", "name": "Ada Blackwood", "description": "The heir with an inconvenient inheritance."},
    {"id": "felix", "name": "Felix Finch", "description": "A pianist whose debts strike a sour note."},
    {"id": "margot", "name": "Dr. Margot Vale", "description": "The family physician with immaculate gloves."},
]
EVIDENCE = [
    {"id": "glass", "title": "The untouched port", "description": "Lord Blackwood's port contains no poison. His teacup carries a bitter almond residue.", "act": 1},
    {"id": "clock", "title": "The stopped clock", "description": "The library clock stopped at 9:10. A photograph shows Blackwood alive at 9:20; the clock is a distraction.", "act": 1},
    {"id": "ledger", "title": "A physician's ledger", "description": "Dr. Vale purchased a cyanide compound on Tuesday. Her ledger records no medical use for it.", "act": 2},
    {"id": "alibi", "title": "The music-room recording", "description": "Ada and Felix can both be heard arguing in the music room from 9:15 to 9:30, when the tea was delivered.", "act": 2},
    {"id": "note", "title": "The dismissal letter", "description": "Blackwood planned to expose Vale's forged medical invoices the next morning. Her initials appear on the tea tray receipt at 9:22.", "act": 3},
]
SOLUTION = "Dr. Margot Vale poisoned Blackwood's tea to conceal her forged invoices. The ledger establishes access to poison, the recording clears Ada and Felix, and the tray receipt places Vale at the delivery. The port and stopped clock were distractions."
