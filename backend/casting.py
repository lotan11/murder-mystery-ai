"""Read-only approval sandbox: fixed public scenes and offline neural voice recordings."""
from __future__ import annotations

import json
import os
from pathlib import Path
import wave

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

ROOT = Path(__file__).resolve().parents[1]
router = APIRouter(prefix="/api/casting", tags=["character and voice approval"])
VOICES = {
    "bm_george": "George",
    "bm_daniel": "Daniel",
    "bm_lewis": "Lewis",
}
SCENES = {
    "arrival": ("Arrival", "Good evening. I am Detective Reginald P. Wobblebottom. A pleasure to meet you. I trust your evening has been less eventful than mine."),
    "evidence": ("An evidence review", "An interesting theory. Let us see whether the evidence is prepared to support it."),
    "reassurance": ("Reassurance", "Take your time. A careful answer is far more useful than a confident guess."),
}
PROVENANCE = {
    "model": "Kokoro-82M v1.0",
    "runtime": "kokoro-onnx 0.6.1",
    "code_license": "MIT",
    "model_license": "Apache-2.0",
    "voice_catalog": "https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md",
    "source": "https://github.com/thewh1teagle/kokoro-onnx",
    "timing": "Audio duration only; no word timings or measured visemes",
    "speech_source": "Locally generated neural TTS",
    "speed": 0.92,
    "sample_rate": 24000,
    "model_assets": {
        "kokoro-v1.0.onnx": "beb0d1848dee9a49da392cc3df26958d46cfa35d321edf434f52949153f0df3a",
        "voices-v1.0.bin": "bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d",
    },
    "dependency_notice": "Core runtime MIT; optional phonemizer/eSpeak dependencies retain their own licenses, including GPLv3+. Models and runtime are not bundled in the game repository.",
}
MAX_MANIFEST_BYTES = 64 * 1024
MAX_AUDIO_BYTES = 8 * 1024 * 1024
PREPARE_MESSAGE = "Prepare the optional Kokoro runtime and run scripts/prepare-casting.py to generate the local neural voice comparison. The working game is unchanged."


class InvalidCasting(ValueError):
    pass


def _root():
    path = Path(os.environ.get("MYSTERY_CASTING_DIR", str(ROOT / "data" / "casting")))
    return (path if path.is_absolute() else ROOT / path).resolve()


def _asset(root, name):
    path = root / name
    if path.resolve().parent != root or not path.is_file():
        raise InvalidCasting("Missing local casting asset")
    return path


def _load():
    root = _root()
    manifest_path = _asset(root, "manifest.json")
    if manifest_path.stat().st_size > MAX_MANIFEST_BYTES:
        raise InvalidCasting("Oversized manifest")
    raw = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict) or type(raw.get("version")) is not int or raw["version"] != 1 or raw.get("provider") != "kokoro-onnx":
        raise InvalidCasting("Unsupported casting manifest")
    voices = raw.get("voices")
    if not isinstance(voices, list) or len(voices) != len(VOICES):
        raise InvalidCasting("Incomplete voice comparison")
    clean, assets, seen_voices = [], {}, set()
    for voice in voices:
        if not isinstance(voice, dict):
            raise InvalidCasting("Invalid voice")
        voice_id = voice.get("id")
        if not isinstance(voice_id, str) or voice_id not in VOICES or voice_id in seen_voices:
            raise InvalidCasting("Unknown voice")
        seen_voices.add(voice_id)
        if voice.get("name") != VOICES[voice_id] or voice.get("locale") != "en-GB" or voice.get("gender") != "Male":
            raise InvalidCasting("Invalid voice metadata")
        samples = voice.get("samples")
        if not isinstance(samples, list) or len(samples) != len(SCENES):
            raise InvalidCasting("Incomplete scenes")
        clean_samples, seen_samples = [], set()
        for sample in samples:
            if not isinstance(sample, dict):
                raise InvalidCasting("Invalid scene")
            sample_id = sample.get("id")
            if not isinstance(sample_id, str) or sample_id not in SCENES or sample_id in seen_samples:
                raise InvalidCasting("Unknown scene")
            seen_samples.add(sample_id)
            title, text = SCENES[sample_id]
            if sample.get("title") != title or sample.get("text") != text:
                raise InvalidCasting("Only authored spoiler-free scenes are served")
            audio = _asset(root, f"{voice_id}-{sample_id}.wav")
            if not 44 <= audio.stat().st_size <= MAX_AUDIO_BYTES:
                raise InvalidCasting("Invalid audio size")
            with wave.open(str(audio), "rb") as stream:
                if stream.getnchannels() != 1 or stream.getsampwidth() != 2 or stream.getcomptype() != "NONE" or not 8000 <= stream.getframerate() <= 48000:
                    raise InvalidCasting("Unsupported audio format")
                expected_bytes = stream.getnframes() * 2
                if expected_bytes > MAX_AUDIO_BYTES or len(stream.readframes(stream.getnframes())) != expected_bytes:
                    raise InvalidCasting("Truncated audio")
                duration_ms = stream.getnframes() * 1000 / stream.getframerate()
            if not 500 <= duration_ms <= 60000:
                raise InvalidCasting("Invalid audio duration")
            assets[(voice_id, sample_id)] = audio
            clean_samples.append({"id": sample_id, "title": title, "text": text,
                                  "duration_ms": round(duration_ms, 2),
                                  "audio_url": f"/api/casting/audio/{voice_id}/{sample_id}"})
        clean.append({"id": voice_id, "name": VOICES[voice_id], "locale": "en-GB", "gender": "Male", "samples": clean_samples})
    test_fixture = raw.get("test_fixture", False)
    if type(test_fixture) is not bool:
        raise InvalidCasting("Invalid provenance")
    return {"available": True, "version": 1, "provider": "kokoro-onnx", "voices": clean,
            "test_fixture": test_fixture, "provenance": {**PROVENANCE, "test_fixture": test_fixture,
                "speech_source": "Synthetic test waveform; not a voice-quality sample" if test_fixture else PROVENANCE["speech_source"]}}, assets


def _read():
    try:
        return _load()
    except (OSError, ValueError, TypeError, KeyError, OverflowError, wave.Error, EOFError):
        return None


@router.get("")
def casting_manifest():
    result = _read()
    payload = result[0] if result else {"available": False, "version": 1, "provider": "kokoro-onnx", "voices": [], "message": PREPARE_MESSAGE}
    return JSONResponse(payload, headers={"Cache-Control": "no-store"})


@router.get("/audio/{voice_id}/{sample_id}")
def casting_audio(voice_id: str, sample_id: str):
    if voice_id not in VOICES or sample_id not in SCENES:
        raise HTTPException(404, "Casting audio not found")
    result = _read()
    if result is None or (voice_id, sample_id) not in result[1]:
        raise HTTPException(404, "Casting audio not found")
    return FileResponse(result[1][(voice_id, sample_id)], media_type="audio/wav", headers={"Cache-Control": "no-store"})
