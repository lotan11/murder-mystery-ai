"""Authoritative authored case. Never publish unrevealed descriptions or solution."""

CASE_ID = "last-toast-blackthorn"
CASE_VERSION = 1
TITLE = "The Last Toast at Blackthorn Manor"
SUSPECTS = [
    {"id": "ada", "name": "Ada Blackthorn", "description": "The heir who argued with her father over the family estate."},
    {"id": "felix", "name": "Felix Finch", "description": "A pianist whose unpaid debts made Blackthorn a difficult patron."},
    {"id": "margot", "name": "Dr. Margot Vale", "description": "The family physician, trusted with the household's medical supplies."},
]
EVIDENCE = [
    {"id": "glass", "summary": "Poison is in the tea, not the port; tea drunk at 9:23, collapse at 9:27.", "title": "The untouched port", "description": "The laboratory report finds no poison in Lord Blackthorn's port, but identifies poison in his teacup. The steward saw him drink newly delivered tea at 9:23 and collapse at 9:27.", "act": 1},
    {"id": "clock", "summary": "Alive in the 9:20 photograph; the broken 9:10 clock cannot date the death.", "title": "The stopped clock", "description": "The library clock reads 9:10, but a timestamped photograph shows Blackthorn alive at 9:20. Its service card records a broken winding spring that morning; the stopped hands do not establish his time of death.", "act": 1},
    {"id": "ledger", "summary": "Vale holds the only dispensary key; the missing compound has no medical use.", "title": "A physician's ledger", "description": "Dr. Vale signed for a cyanide compound on Tuesday. The locked dispensary ledger records her as its sole key holder and lists no legitimate use for the missing compound.", "act": 2},
    {"id": "alibi", "summary": "Ada and Felix remain recorded in the music room throughout 9:15 to 9:30.", "title": "The music-room recording", "description": "A continuous, timestamped music-room recording captures Ada and Felix speaking throughout 9:15 to 9:30. Both remained there while Blackthorn's tea was delivered and drunk.", "act": 2},
    {"id": "note", "summary": "Vale faced exposure for forged invoices and had sole tray custody at 9:22.", "title": "The dismissal letter", "description": "Blackthorn's signed letter says he will expose Vale's forged invoices the next morning; she acknowledged it that afternoon. The steward observed fresh tea poured at 9:21. Vale signed for the tray at 9:22 and alone carried it to Blackthorn before he drank at 9:23.", "act": 3},
]
SOLUTION = (
    "Dr. Margot Vale poisoned Lord Blackthorn's tea to prevent exposure of her forged invoices. "
    "The teacup establishes the means, and the dispensary ledger establishes her access. "
    "Ada and Felix's continuous recording clears them during the delivery. "
    "Vale's acknowledged dismissal letter supplies the motive, and her sole custody of the freshly poured tea at 9:22 supplies the opportunity before Blackthorn drank at 9:23 and collapsed at 9:27. "
    "The clean port was the wrong vessel; the broken clock was an unreliable time cue, not evidence of an earlier death."
)
