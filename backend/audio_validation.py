"""Validate independently finalized browser audio clips and their actual duration."""
from __future__ import annotations

import math
import struct

DECLARED_DURATION_TOLERANCE_SECONDS = 1.25

class AudioValidationError(ValueError):
    pass


def _vint(data: bytes, offset: int, *, element_id: bool = False) -> tuple[int, int]:
    if offset >= len(data) or data[offset] == 0:
        raise AudioValidationError("The audio container header is incomplete.")
    first = data[offset]
    mask = 0x80
    length = 1
    while not first & mask and length <= 8:
        mask >>= 1
        length += 1
    if length > 8 or offset + length > len(data):
        raise AudioValidationError("The audio container header is invalid.")
    raw = data[offset:offset + length]
    value = int.from_bytes(raw, "big")
    if not element_id:
        value &= (1 << (7 * length)) - 1
    return value, length


def _webm_duration(data: bytes) -> float:
    if not data.startswith(b"\x1a\x45\xdf\xa3"):
        raise AudioValidationError("The bytes do not match the declared WebM audio format.")

    def elements(start: int, end: int):
        offset = start
        while offset < end:
            element_id, id_len = _vint(data, offset, element_id=True)
            size, size_len = _vint(data, offset + id_len)
            payload = offset + id_len + size_len
            unknown = size == (1 << (7 * size_len)) - 1
            item_end = end if unknown else payload + size
            if payload > end or item_end > end or item_end < payload:
                raise AudioValidationError("The WebM container has an invalid element size.")
            yield element_id, payload, item_end
            if item_end <= offset:
                raise AudioValidationError("The WebM container has an invalid element boundary.")
            offset = item_end

    duration = None
    scale = 1_000_000  # Matroska's default TimecodeScale is one millisecond in nanoseconds.
    for element_id, payload, item_end in elements(0, len(data)):
        if element_id != 0x18538067:  # Segment
            continue
        for child_id, child_payload, child_end in elements(payload, item_end):
            if child_id != 0x1549A966:  # Info
                continue
            for info_id, info_payload, info_end in elements(child_payload, child_end):
                if info_id == 0x2AD7B1 and info_end - info_payload <= 8:  # TimecodeScale
                    scale = int.from_bytes(data[info_payload:info_end], "big")
                elif info_id == 0x4489:  # Duration, float or double
                    raw = data[info_payload:info_end]
                    if len(raw) == 8:
                        duration = struct.unpack(">d", raw)[0]
                    elif len(raw) == 4:
                        duration = struct.unpack(">f", raw)[0]
                    else:
                        raise AudioValidationError("The WebM duration field is invalid.")
            break
        break
    if duration is None or not math.isfinite(duration) or scale <= 0:
        raise AudioValidationError("The finalized WebM clip has no valid duration metadata.")
    return duration * scale / 1_000_000_000


def _mp4_duration(data: bytes) -> float:
    duration = None

    def boxes(start: int, end: int, depth: int = 0):
        nonlocal duration
        if depth > 8:
            raise AudioValidationError("The MP4 container nesting is invalid.")
        offset = start
        while offset + 8 <= end:
            size = int.from_bytes(data[offset:offset + 4], "big")
            kind = data[offset + 4:offset + 8]
            header = 8
            if size == 1:
                if offset + 16 > end:
                    raise AudioValidationError("The MP4 extended box header is incomplete.")
                size = int.from_bytes(data[offset + 8:offset + 16], "big")
                header = 16
            elif size == 0:
                size = end - offset
            if size < header or offset + size > end:
                raise AudioValidationError("The MP4 container has an invalid box size.")
            payload = offset + header
            box_end = offset + size
            if kind in (b"moov",):
                boxes(payload, box_end, depth + 1)
            elif kind == b"mvhd":
                version = data[payload]
                if version == 0 and box_end - payload >= 20:
                    timescale = int.from_bytes(data[payload + 12:payload + 16], "big")
                    ticks = int.from_bytes(data[payload + 16:payload + 20], "big")
                elif version == 1 and box_end - payload >= 32:
                    timescale = int.from_bytes(data[payload + 20:payload + 24], "big")
                    ticks = int.from_bytes(data[payload + 24:payload + 32], "big")
                else:
                    raise AudioValidationError("The MP4 movie duration is invalid.")
                if not timescale or not ticks:
                    raise AudioValidationError("The MP4 movie duration is empty.")
                duration = ticks / timescale
            offset = box_end

    if len(data) < 12 or data[4:8] != b"ftyp":
        raise AudioValidationError("The bytes do not match the declared MP4 audio format.")
    boxes(0, len(data))
    if duration is None:
        raise AudioValidationError("The finalized MP4 clip has no movie duration.")
    return duration


def _ogg_opus_duration(data: bytes) -> float:
    if not data.startswith(b"OggS"):
        raise AudioValidationError("The bytes do not match the declared Ogg audio format.")
    offset = 0
    last_granule = None
    opus_head = None
    ended = False
    while offset < len(data):
        if offset + 27 > len(data) or data[offset:offset + 4] != b"OggS" or data[offset + 4] != 0:
            raise AudioValidationError("The Ogg page header is invalid.")
        flags = data[offset + 5]
        granule = int.from_bytes(data[offset + 6:offset + 14], "little")
        segments = data[offset + 26]
        table = offset + 27
        if table + segments > len(data):
            raise AudioValidationError("The Ogg segment table is incomplete.")
        page_size = sum(data[table:table + segments])
        page_end = table + segments + page_size
        if page_end > len(data):
            raise AudioValidationError("The Ogg audio page is incomplete.")
        if opus_head is None:
            opus_head = data[table + segments:page_end]
        if granule != (1 << 64) - 1:
            last_granule = granule
        ended = bool(flags & 0x04)
        offset = page_end
    if not opus_head or not opus_head.startswith(b"OpusHead") or len(opus_head) < 12 or last_granule is None or not ended:
        raise AudioValidationError("Only finalized Ogg Opus clips with duration metadata are supported.")
    pre_skip = int.from_bytes(opus_head[10:12], "little")
    return max(0, last_granule - pre_skip) / 48_000


def validate_audio_chunk(data: bytes, mime_type: str, declared_seconds: float) -> float:
    """Return verified duration, rejecting mismatched, unfinished or overlong clips."""
    mime = mime_type.lower()
    if mime in {"audio/webm", "audio/webm;codecs=opus"}:
        duration = _webm_duration(data)
    elif mime == "audio/mp4":
        duration = _mp4_duration(data)
    elif mime == "audio/ogg;codecs=opus":
        duration = _ogg_opus_duration(data)
    else:
        raise AudioValidationError("This microphone audio format is not supported.")
    if not math.isfinite(duration) or not 0.5 <= duration <= 5.25:
        raise AudioValidationError("Audio clips must contain 0.5–5 seconds of finalized audio.")
    # MediaRecorder stop/dataavailable scheduling can drift by about a second;
    # usage is always charged from this parsed duration, never the declaration.
    if abs(duration - declared_seconds) > DECLARED_DURATION_TOLERANCE_SECONDS:
        raise AudioValidationError("The announced audio duration does not match the clip.")
    return duration
