"""Read-only local Windows voice audition assets; never synthesize in an HTTP request."""
from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import wave

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

ROOT = Path(__file__).resolve().parents[1]
router = APIRouter(prefix="/api/audition", tags=["local voice audition"])
VOICE_IDS = {"david", "zira"}
SAMPLES = {
    "greeting": ("An impeccable introduction", "Good evening. I am Detective Reginald P. Wobblebottom. Kindly keep your theories sharp, and your fingerprints to yourself."),
    "observation": ("A dry observation", "An intriguing observation. Let us distinguish evidence from a stylish suspicion."),
    "pause": ("A considered pause", "Something is amiss. A careful question is worth several impressive guesses."),
}
TIMING_SOURCE = "SAPI SpeakProgress word starts; word durations estimated"
SYNTHETIC_TIMING_SOURCE = "Synthetic test waveform and timings; not recorded speech"
MAX_MANIFEST_BYTES = 128 * 1024
MAX_AUDIO_BYTES = 8 * 1024 * 1024
PREPARE_MESSAGE = "Run powershell -ExecutionPolicy Bypass -File .\\scripts\\prepare-audition.ps1 on Windows to prepare the local voice audition."


class InvalidAudition(ValueError):
    pass


def _root() -> Path:
    path = Path(os.environ.get("MYSTERY_AUDITION_DIR", str(ROOT / "data" / "audition")))
    return (path if path.is_absolute() else ROOT / path).resolve()


def _asset(root: Path, filename: str) -> Path:
    path = root / filename
    # Reject symlinks to other directories as well as traversal.
    if path.resolve().parent != root or not path.is_file():
        raise InvalidAudition("Unavailable local asset")
    return path


def _text(value, maximum):
    return isinstance(value, str) and 0 < len(value) <= maximum and not any(ord(character) < 32 for character in value)


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _normalized_words(text):
    return re.findall(r"[a-z0-9]+", text.casefold())


def _load():
    root = _root()
    manifest_path = _asset(root, "manifest.json")
    if manifest_path.stat().st_size > MAX_MANIFEST_BYTES:
        raise InvalidAudition("Oversized manifest")
    raw = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict) or type(raw.get("version")) is not int or raw["version"] != 1:
        raise InvalidAudition("Unsupported manifest")
    timing_source = raw.get("timing_source", TIMING_SOURCE)
    if timing_source not in (TIMING_SOURCE, SYNTHETIC_TIMING_SOURCE):
        raise InvalidAudition("Unknown timing provenance")
    voices = raw.get("voices")
    if not isinstance(voices, list) or not 1 <= len(voices) <= 2:
        raise InvalidAudition("Invalid voice list")
    seen = set()
    clean = []
    assets = {}
    for voice in voices:
        if not isinstance(voice, dict):
            raise InvalidAudition("Invalid voice")
        voice_id = voice.get("id")
        if not isinstance(voice_id, str) or voice_id not in VOICE_IDS or voice_id in seen:
            raise InvalidAudition("Unknown voice")
        seen.add(voice_id)
        if not _text(voice.get("name"), 128) or voice.get("locale") != "en-US" or voice.get("gender") not in ("Male", "Female"):
            raise InvalidAudition("Invalid voice metadata")
        samples = voice.get("samples")
        if not isinstance(samples, list) or len(samples) != len(SAMPLES):
            raise InvalidAudition("Incomplete samples")
        clean_samples = []
        seen_samples = set()
        for sample in samples:
            if not isinstance(sample, dict):
                raise InvalidAudition("Invalid sample")
            sample_id = sample.get("id")
            if not isinstance(sample_id, str) or sample_id not in SAMPLES or sample_id in seen_samples:
                raise InvalidAudition("Unknown sample")
            seen_samples.add(sample_id)
            title, text = SAMPLES[sample_id]
            if sample.get("text") != text or sample.get("title") != title:
                raise InvalidAudition("Only authored spoiler-free audition text is allowed")
            words, starts, durations = sample.get("words"), sample.get("wtimes"), sample.get("wdurations")
            if not isinstance(words, list) or not 1 <= len(words) <= 100 or not all(_text(word, 80) for word in words):
                raise InvalidAudition("Invalid words")
            if _normalized_words(" ".join(words)) != _normalized_words(text):
                raise InvalidAudition("Word sequence does not match the authored line")
            if not isinstance(starts, list) or not isinstance(durations, list) or len(starts) != len(words) or len(durations) != len(words):
                raise InvalidAudition("Invalid timing arrays")
            audio = _asset(root, f"{voice_id}-{sample_id}.wav")
            if not 44 <= audio.stat().st_size <= MAX_AUDIO_BYTES:
                raise InvalidAudition("Invalid audio size")
            with wave.open(str(audio), "rb") as stream:
                if stream.getnchannels() not in (1, 2) or stream.getsampwidth() != 2 or stream.getcomptype() != "NONE":
                    raise InvalidAudition("Unsupported audio format")
                if not 8000 <= stream.getframerate() <= 96000:
                    raise InvalidAudition("Invalid sample rate")
                expected_bytes = stream.getnframes() * stream.getnchannels() * stream.getsampwidth()
                if expected_bytes > MAX_AUDIO_BYTES or len(stream.readframes(stream.getnframes())) != expected_bytes:
                    raise InvalidAudition("Truncated audio")
                audio_ms = stream.getnframes() * 1000 / stream.getframerate()
            if not 100 <= audio_ms <= 60000:
                raise InvalidAudition("Invalid audio duration")
            if not all(_number(start) and 0 <= start <= audio_ms for start in starts) or starts != sorted(starts):
                raise InvalidAudition("Invalid word starts")
            if not all(_number(length) and length > 0 and start + length <= audio_ms + 2 for start, length in zip(starts, durations)):
                raise InvalidAudition("Invalid estimated durations")
            assets[(voice_id, sample_id)] = audio
            clean_samples.append({"id": sample_id, "title": title, "text": text, "words": words,
                                  "wtimes": starts, "wdurations": durations,
                                  "duration_ms": round(audio_ms, 2),
                                  "audio_url": f"/api/audition/audio/{voice_id}/{sample_id}"})
        clean.append({"id": voice_id, "name": voice["name"], "locale": "en-US", "gender": voice["gender"], "samples": clean_samples})
    return {"available": True, "version": 1, "voices": clean, "timing_source": timing_source,
            "synthetic": timing_source == SYNTHETIC_TIMING_SOURCE}, assets


def _read():
    try:
        return _load()
    except (OSError, ValueError, TypeError, KeyError, OverflowError, wave.Error, EOFError):
        return None


@router.get("")
def audition_manifest():
    result = _read()
    if result is None:
        return {"available": False, "version": 1, "voices": [], "message": PREPARE_MESSAGE}
    return result[0]


@router.get("/audio/{voice_id}/{sample_id}")
def audition_audio(voice_id: str, sample_id: str):
    if voice_id not in VOICE_IDS or sample_id not in SAMPLES:
        raise HTTPException(404, "Audition audio not found")
    result = _read()
    if result is None or (voice_id, sample_id) not in result[1]:
        raise HTTPException(404, "Audition audio not found")
    return FileResponse(result[1][(voice_id, sample_id)], media_type="audio/wav", headers={"Cache-Control": "no-store"})
