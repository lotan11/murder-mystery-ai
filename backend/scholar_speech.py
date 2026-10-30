"""Approved Scholar/Lewis game speech. Separate from the working Windows SAPI path."""
from __future__ import annotations

import asyncio
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import wave

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from .speech_cache import SpeechCache
from .local_speech import _authorize
from .speech_timing import MAX_TIMING_BYTES, validate_phoneme_timing

ROOT = Path(__file__).resolve().parents[1]
MAX_TEXT_CHARS = 1500
MAX_AUDIO_BYTES = 8 * 1024 * 1024
PROCESS_TIMEOUT = 40.0
PLAYBACK_RATE = 1.05
MODEL_SIZES = {"kokoro-v1.0.onnx": 325505369, "voices-v1.0.bin": 28214398}


class ScholarSpeechError(RuntimeError):
    def __init__(self, reason):
        self.reason = reason if reason in {"unavailable", "busy", "timeout", "generation_failed", "invalid_output", "text_too_long"} else "generation_failed"
        super().__init__(self.reason)


def _read_render(directory, text):
    manifest_path, audio_path = directory / "speech.json", directory / "speech.wav"
    if not manifest_path.is_file() or not audio_path.is_file() or manifest_path.stat().st_size > 16384 or not 44 <= audio_path.stat().st_size <= MAX_AUDIO_BYTES:
        raise ScholarSpeechError("invalid_output")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if not isinstance(manifest, dict) or manifest.get("text") != text or manifest.get("voice") != "bm_lewis" or manifest.get("provider") != "kokoro-onnx" or manifest.get("generation_speed") != 0.92:
        raise ScholarSpeechError("invalid_output")
    data = audio_path.read_bytes()
    with wave.open(io.BytesIO(data), "rb") as audio:
        if audio.getnchannels() != 1 or audio.getsampwidth() != 2 or audio.getframerate() != 24000 or audio.getcomptype() != "NONE":
            raise ScholarSpeechError("invalid_output")
        expected = audio.getnframes() * 2
        if expected > MAX_AUDIO_BYTES or len(audio.readframes(audio.getnframes())) != expected:
            raise ScholarSpeechError("invalid_output")
        duration = audio.getnframes() * 1000 / 24000
    if not 100 <= duration <= 170000:
        raise ScholarSpeechError("invalid_output")
    result = {"provider": "kokoro-onnx", "voice": "bm_lewis", "text": text,
              "duration_ms": round(duration, 2), "content_type": "audio/wav",
              "audio_base64": base64.b64encode(data).decode("ascii"), "playback_rate": PLAYBACK_RATE}
    timing_path = directory / "speech-timing.json"
    if timing_path.is_symlink():
        raise ScholarSpeechError("invalid_output")
    if timing_path.exists():
        try:
            if not timing_path.is_file() or timing_path.stat().st_size > MAX_TIMING_BYTES:
                raise ValueError("Invalid timing file")
            with timing_path.open("rb") as stream:
                timing_data = stream.read(MAX_TIMING_BYTES + 1)
            if len(timing_data) > MAX_TIMING_BYTES:
                raise ValueError("Timing file exceeds limit")
            result["phoneme_timing"] = validate_phoneme_timing(json.loads(timing_data), duration / 1000)
        except (OSError, ValueError, TypeError, UnicodeError, OverflowError):
            raise ScholarSpeechError("invalid_output") from None
    return result


class ScholarSpeechRenderer:
    def __init__(self, base_dir=None, model_dir=None, executable=None, timeout=PROCESS_TIMEOUT, *,
                 cache_max_entries=4, cache_max_bytes=32 * 1024 * 1024, cache_ttl=900.0, clock=time.monotonic):
        self.base_dir = Path(base_dir) if base_dir is not None else ROOT / "data" / "scholar-speech"
        self.model_dir = Path(model_dir) if model_dir is not None else ROOT / "data" / "casting-models"
        self.executable = Path(executable) if executable is not None else ROOT / "data" / "casting-runtime" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
        self.script = ROOT / "scripts" / "render-scholar-speech.py"
        self.timeout = timeout
        try:
            self.available = self.executable.is_absolute() and self.executable.is_file() and self.script.is_file() and all(
                (self.model_dir / name).is_file() and (self.model_dir / name).stat().st_size == size for name, size in MODEL_SIZES.items())
        except OSError:
            self.available = False
        self._busy = False
        self._cache = SpeechCache(cache_max_entries, cache_max_bytes, cache_ttl, clock)

    async def render(self, text):
        if not self.available:
            raise ScholarSpeechError("unavailable")
        if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT_CHARS:
            raise ScholarSpeechError("text_too_long")
        # Cache is per renderer/process and stores no room revision or credentials.
        # Bump this namespace if approved model/runtime/voice/rendering identity changes.
        identity = 'kokoro-onnx:0.6.1:model-v1.0:bm_lewis:0.92:1.05:24000:timing-v1'
        try:
            key = hashlib.sha256((identity + '\0' + text).encode('utf-8')).hexdigest()
        except UnicodeError:
            raise ScholarSpeechError('generation_failed') from None
        try:
            cached = self._cache.get(key)
        except Exception:
            # Acceleration is best-effort; cache failures must not disable valid speech.
            cached = None
        if cached is not None:
            return cached
        if self._busy:
            raise ScholarSpeechError("busy")
        self._busy = True
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="speech-", dir=self.base_dir) as temporary:
                directory = Path(temporary)
                payload = directory / "input.json"
                payload.write_text(json.dumps({"text": text}, ensure_ascii=False), encoding="utf-8")
                process = None
                try:
                    process = await asyncio.create_subprocess_exec(
                        str(self.executable), str(self.script), "--input", str(payload),
                        "--output", str(directory), "--models", str(self.model_dir.resolve()),
                        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                        env={key: value for key, value in os.environ.items() if "API_KEY" not in key.upper() and not key.upper().endswith("_TOKEN")},
                    )
                    try:
                        await asyncio.wait_for(process.wait(), timeout=self.timeout)
                    except TimeoutError:
                        raise ScholarSpeechError("timeout") from None
                    if process.returncode != 0:
                        raise ScholarSpeechError("generation_failed")
                    result = _read_render(directory, text)
                finally:
                    if process is not None and process.returncode is None:
                        try:
                            process.kill()
                        except ProcessLookupError:
                            pass
                        try:
                            await asyncio.wait_for(process.wait(), timeout=2)
                        except TimeoutError:
                            raise ScholarSpeechError("timeout") from None
            # Store only after successful child validation AND temporary-file cleanup.
            try:
                self._cache.put(key, result)
            except Exception:
                # The clip is already validated; preserve it if optional storage fails.
                pass
            return result
        except asyncio.CancelledError:
            raise
        except ScholarSpeechError:
            raise
        except Exception:
            raise ScholarSpeechError("generation_failed") from None
        finally:
            self._busy = False


def _status(renderer):
    return {"available": bool(renderer.available), "provider": "kokoro-onnx", "voice": "bm_lewis",
            "playback_rate": PLAYBACK_RATE,
            "message": "Approved local Lewis voice, five percent faster in playback with pitch preserved; no measured word timings or visemes." if renderer.available else "The optional approved Lewis runtime and verified models are not prepared. The existing Windows voice and captions remain available."}


async def _empty_body(request):
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 32:
            raise HTTPException(413, "Approved voice requests do not accept dialogue or voice choices.")
    try:
        value = json.loads(body) if body else {}
    except (ValueError, UnicodeError):
        raise HTTPException(422, "Send an empty JSON object only.") from None
    if not isinstance(value, dict) or value:
        raise HTTPException(422, "The approved voice speaks current public dialogue only; text and voice fields are not accepted.")


def create_router(get_room):
    router = APIRouter(tags=["approved Scholar game speech"])

    @router.get("/api/scholar-speech/status")
    async def scholar_status(request: Request):
        return JSONResponse(_status(request.app.state.scholar_speech), headers={"Cache-Control": "no-store"})

    @router.post("/api/rooms/{room_id}/scholar-speech")
    async def scholar_speech(room_id: str, request: Request):
        room = get_room(room_id)
        _authorize(request, room)
        await _empty_body(request)
        async with room.lock:
            if room.paused:
                raise HTTPException(409, "The evening is paused; approved voice playback is stopped.")
            text, revision = room.dialogue, room.revision
            if not isinstance(text, str) or not text.strip():
                raise HTTPException(409, "There is no current detective dialogue to speak.")
            if len(text) > MAX_TEXT_CHARS:
                raise HTTPException(413, "The current dialogue is too long for one approved voice clip. Captions remain available.")
        try:
            result = await request.app.state.scholar_speech.render(text)
        except ScholarSpeechError as exc:
            errors = {
                "unavailable": (503, "The optional Lewis runtime is unavailable. Windows speech and captions remain available."),
                "busy": (429, "The approved voice is preparing another clip. Try again shortly."),
                "timeout": (504, "The approved local voice took too long; no audio was returned. Captions remain available."),
                "generation_failed": (503, "The approved local voice could not be prepared. Captions remain available."),
                "invalid_output": (503, "The approved local voice output could not be validated. Captions remain available."),
                "text_too_long": (413, "The current dialogue is too long for one approved voice clip. Captions remain available."),
            }
            code, message = errors[exc.reason]
            raise HTTPException(code, message) from None
        async with room.lock:
            if room.paused or room.revision != revision or room.dialogue != text:
                raise HTTPException(409, "The room changed during voice preparation; the old audio was discarded.")
        keys = ("provider", "voice", "text", "duration_ms", "content_type", "audio_base64", "playback_rate")
        if not isinstance(result, dict) or result.get("text") != text or result.get("voice") != "bm_lewis" or result.get("provider") != "kokoro-onnx" or result.get("playback_rate") != PLAYBACK_RATE or not all(key in result for key in keys):
            raise HTTPException(503, "The approved voice output could not be validated. Captions remain available.")
        response = {**{key: result[key] for key in keys}, "revision": revision}
        if "phoneme_timing" in result:
            try:
                # duration_ms is rounded to0.01ms; recover the unique24000Hz frame clock.
                duration = round(result["duration_ms"] * 24) / 24000
                response["phoneme_timing"] = validate_phoneme_timing(result["phoneme_timing"], duration)
            except (ValueError, TypeError, OverflowError):
                raise HTTPException(503, "The approved voice output could not be validated. Captions remain available.") from None
        return JSONResponse(response, headers={"Cache-Control": "no-store"})

    return router
