"""Bounded model-predicted phoneme metadata, on the original audio clock."""
from __future__ import annotations
import json
import math
import unicodedata

MAX_TIMING_BYTES = 512 * 1024
MAX_PHONEMES = 4000
TIMING_SOURCE = "kokoro-model-duration"
TIMING_CLOCK = "audio-seconds"


def validate_phoneme_timing(value, duration_seconds):
    """Return only the accepted schema; never synthesize or rescale missing cues."""
    if type(duration_seconds) not in (int, float) or not math.isfinite(duration_seconds) or not 0.1 <= duration_seconds <= 170:
        raise ValueError("Invalid source audio duration")
    if not isinstance(value, dict) or set(value) != {"source", "clock", "phonemes"}:
        raise ValueError("Invalid timing schema")
    if value["source"] != TIMING_SOURCE or value["clock"] != TIMING_CLOCK:
        raise ValueError("Unsupported timing source or clock")
    cues = value["phonemes"]
    if not isinstance(cues, list) or not 1 <= len(cues) <= MAX_PHONEMES:
        raise ValueError("Missing or excessive phoneme cues")
    # Validate size on injected renderer dictionaries as well as worker files.
    try:
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, UnicodeError, OverflowError):
        raise ValueError("Timing metadata cannot be serialized") from None
    if len(encoded) > MAX_TIMING_BYTES:
        raise ValueError("Timing metadata exceeds limit")
    normalized = []
    previous_end = 0.0
    for cue in cues:
        if not isinstance(cue, dict) or set(cue) != {"phoneme", "start", "end"}:
            raise ValueError("Invalid phoneme cue schema")
        symbol, start, end = cue["phoneme"], cue["start"], cue["end"]
        if not isinstance(symbol, str) or not 1 <= len(symbol) <= 8 or any(unicodedata.category(char).startswith("C") or (char.isspace() and char != " ") for char in symbol):
            raise ValueError("Invalid phoneme symbol")
        if any(type(number) not in (int, float) or not math.isfinite(number) for number in (start, end)):
            raise ValueError("Invalid phoneme time")
        if not 0 <= start <= end <= duration_seconds or start < previous_end:
            raise ValueError("Out-of-range or overlapping phoneme cue")
        normalized.append({"phoneme": symbol, "start": start, "end": end})
        previous_end = end
    return {"source": TIMING_SOURCE, "clock": TIMING_CLOCK, "phonemes": normalized}
