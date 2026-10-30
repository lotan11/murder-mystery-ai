import struct

import pytest

from backend.audio_validation import AudioValidationError, validate_audio_chunk


def webm_clip(seconds=3.0):
    # Minimal finalized EBML Segment/Info/Duration; the transcription test injects its own adapter.
    duration = int(seconds * 1000)
    info_payload = bytes.fromhex("448988") + struct.pack(">d", duration)
    info = bytes.fromhex("1549a966") + bytes([0x80 | len(info_payload)]) + info_payload
    segment = bytes.fromhex("18538067") + bytes([0x80 | len(info)]) + info
    return bytes.fromhex("1a45dfa380") + segment


@pytest.mark.parametrize("seconds", [0.5, 1.0, 3.0, 5.0])
def test_webm_duration_is_read_from_finalized_container(seconds):
    actual = validate_audio_chunk(webm_clip(seconds), "audio/webm;codecs=opus", seconds)
    assert actual == pytest.approx(seconds)


@pytest.mark.parametrize("declared", [0.5, 1.0, 4.0, 5.0])
def test_duration_mismatch_is_rejected(declared):
    with pytest.raises(AudioValidationError, match="does not match"):
        validate_audio_chunk(webm_clip(3.0), "audio/webm", declared)


def test_malformed_or_unsupported_audio_is_rejected():
    with pytest.raises(AudioValidationError, match="do not match"):
        validate_audio_chunk(b"not webm", "audio/webm", 3)
    with pytest.raises(AudioValidationError, match="not supported"):
        validate_audio_chunk(webm_clip(), "audio/mpeg", 3)


def test_container_duration_over_five_seconds_is_rejected():
    with pytest.raises(AudioValidationError, match="0.5–5 seconds"):
        validate_audio_chunk(webm_clip(5.5), "audio/webm", 5)
