"""Bounded local Windows speech of the current public room reply, never caller text."""
from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import wave

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

ROOT = Path(__file__).resolve().parents[1]
VOICE_NAMES = {"david": "Microsoft David", "zira": "Microsoft Zira"}
MAX_TEXT_CHARS = 1500
MAX_AUDIO_BYTES = 4 * 1024 * 1024
MAX_MANIFEST_BYTES = 128 * 1024
PROCESS_TIMEOUT = 20.0
TIMING_SOURCE = "SAPI SpeakProgress word starts; word durations estimated"


class SpeechError(RuntimeError):
    def __init__(self, reason):
        self.reason = reason if reason in {"unavailable", "busy", "timeout", "generation_failed", "invalid_output", "text_too_long"} else "generation_failed"
        super().__init__(self.reason)


def tv_speech_token(room):
    """A durable read-only capability derived from an existing room secret; no schema change."""
    return hmac.new(room.organizer_token.encode("utf-8"),
                    ("wobblebottom-tv-speech-v1:" + room.room_id).encode("utf-8"), hashlib.sha256).hexdigest()


def _same_token(candidate, expected):
    return hmac.compare_digest(candidate.encode("utf-8"), expected.encode("utf-8"))


def _authorize(request, room, host_only=False):
    authorization = request.headers.get("authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "A host or TV speech credential is required.")
    candidate = authorization[7:]
    if not _same_token(candidate, room.organizer_token) and (host_only or not _same_token(candidate, tv_speech_token(room))):
        raise HTTPException(403, "The speech credential is not valid for this room.")


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _words(text):
    return re.findall(r"[a-z0-9]+", text.casefold())


def _read_render(directory, text, voice):
    manifest_path, audio_path = directory / "speech.json", directory / "speech.wav"
    if not manifest_path.is_file() or not audio_path.is_file():
        raise SpeechError("invalid_output")
    if manifest_path.stat().st_size > MAX_MANIFEST_BYTES or not 44 <= audio_path.stat().st_size <= MAX_AUDIO_BYTES:
        raise SpeechError("invalid_output")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if not isinstance(manifest, dict) or manifest.get("text") != text or manifest.get("voice") != voice:
        raise SpeechError("invalid_output")
    words, starts, lengths = manifest.get("words"), manifest.get("wtimes"), manifest.get("wdurations")
    if not isinstance(words, list) or not 1 <= len(words) <= 400 or not all(isinstance(word, str) and 0 < len(word) <= 120 for word in words):
        raise SpeechError("invalid_output")
    if _words(" ".join(words)) != _words(text):
        raise SpeechError("invalid_output")
    if not isinstance(starts, list) or not isinstance(lengths, list) or len(starts) != len(words) or len(lengths) != len(words):
        raise SpeechError("invalid_output")
    data = audio_path.read_bytes()
    with wave.open(io.BytesIO(data), "rb") as audio:
        if audio.getnchannels() != 1 or audio.getsampwidth() != 2 or audio.getframerate() != 16000 or audio.getcomptype() != "NONE":
            raise SpeechError("invalid_output")
        expected = audio.getnframes() * 2
        if expected > MAX_AUDIO_BYTES or len(audio.readframes(audio.getnframes())) != expected:
            raise SpeechError("invalid_output")
        duration = audio.getnframes() * 1000 / 16000
    if not 100 <= duration <= 130000:
        raise SpeechError("invalid_output")
    if not all(_number(start) and 0 <= start <= duration for start in starts) or starts != sorted(starts):
        raise SpeechError("invalid_output")
    if not all(_number(length) and 0 < length <= 400 and start + length <= duration + 2 for start, length in zip(starts, lengths)):
        raise SpeechError("invalid_output")
    return {"provider": "windows-sapi", "voice": voice, "text": text, "words": words,
            "wtimes": starts, "wdurations": lengths, "duration_ms": round(duration, 2),
            "content_type": "audio/wav", "audio_base64": base64.b64encode(data).decode("ascii"),
            "timing_source": TIMING_SOURCE}


class LocalSpeechRenderer:
    def __init__(self, base_dir=None, timeout=PROCESS_TIMEOUT, executable=None, platform_name=None):
        self.base_dir = Path(base_dir) if base_dir is not None else ROOT / "data" / "local-speech"
        self.timeout = timeout
        system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        self.executable = Path(executable) if executable is not None else system_root / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        self.script = ROOT / "scripts" / "render-local-speech.ps1"
        self.available = (platform_name or sys.platform) == "win32" and self.executable.is_absolute() and self.executable.is_file() and self.script.is_file()
        self._busy = False

    async def render(self, text, voice):
        if not self.available:
            raise SpeechError("unavailable")
        if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT_CHARS:
            raise SpeechError("text_too_long")
        if voice not in VOICE_NAMES:
            raise SpeechError("generation_failed")
        if self._busy:
            raise SpeechError("busy")
        self._busy = True
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="speech-", dir=self.base_dir) as temporary:
                directory = Path(temporary)
                payload = directory / "input.json"
                payload.write_text(json.dumps({"text": text, "voice": voice}, ensure_ascii=False), encoding="utf-8")
                process = None
                try:
                    process = await asyncio.create_subprocess_exec(
                        str(self.executable), "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                        "-File", str(self.script), "-InputFile", str(payload), "-OutputDirectory", str(directory),
                        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
                        env={key: value for key, value in os.environ.items() if key != "OPENAI_API_KEY"},
                    )
                    try:
                        await asyncio.wait_for(process.wait(), timeout=self.timeout)
                    except TimeoutError:
                        raise SpeechError("timeout")
                    if process.returncode != 0:
                        raise SpeechError("generation_failed")
                    return _read_render(directory, text, voice)
                finally:
                    # Kill and reap before TemporaryDirectory removes files (important on Windows).
                    if process is not None and process.returncode is None:
                        try:
                            process.kill()
                        except ProcessLookupError:
                            pass
                        try:
                            await asyncio.wait_for(process.wait(), timeout=2)
                        except TimeoutError:
                            raise SpeechError("timeout") from None
        except asyncio.CancelledError:
            raise
        except SpeechError:
            raise
        except Exception:
            raise SpeechError("generation_failed") from None
        finally:
            self._busy = False


def _status(renderer):
    return {"available": bool(renderer.available), "provider": "windows-sapi",
            "voices": [{"id": key, "name": name} for key, name in VOICE_NAMES.items()],
            "message": "Uses installed local Windows voices; word starts are engine reported and mouth durations are estimates." if renderer.available else "Local timed speech requires Windows PowerShell and installed David/Zira voices. Captions remain available."}


async def _voice_body(request):
    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > 128:
            raise HTTPException(413, "Speech requests contain only a voice choice.")
    try:
        value = json.loads(body) if body else {}
    except (ValueError, UnicodeError):
        raise HTTPException(422, "Send a JSON voice choice only.") from None
    if not isinstance(value, dict) or set(value) - {"voice"} or not isinstance(value.get("voice", "david"), str) or value.get("voice", "david") not in VOICE_NAMES:
        raise HTTPException(422, "Only the David or Zira voice choice is accepted; client dialogue is not accepted.")
    return value.get("voice", "david")


def create_router(get_room):
    router = APIRouter(tags=["local timed game speech"])

    @router.get("/api/speech/status")
    async def speech_status(request: Request):
        return JSONResponse(_status(request.app.state.local_speech), headers={"Cache-Control": "no-store"})

    @router.get("/api/rooms/{room_id}/speech/config")
    async def speech_config(room_id: str, request: Request):
        room = get_room(room_id)
        _authorize(request, room, host_only=True)
        return JSONResponse({**_status(request.app.state.local_speech), "tv_token": tv_speech_token(room)}, headers={"Cache-Control": "no-store"})

    @router.post("/api/rooms/{room_id}/speech")
    async def speech(room_id: str, request: Request):
        room = get_room(room_id)
        _authorize(request, room)
        voice = await _voice_body(request)
        async with room.lock:
            if room.paused:
                raise HTTPException(409, "The evening is paused; timed speech is stopped.")
            text, revision = room.dialogue, room.revision
            if not isinstance(text, str) or not text.strip():
                raise HTTPException(409, "There is no current detective dialogue to speak.")
            if len(text) > MAX_TEXT_CHARS:
                raise HTTPException(413, "The current dialogue is too long for a single local speech clip. Captions remain available.")
        try:
            result = await request.app.state.local_speech.render(text, voice)
        except SpeechError as exc:
            errors = {
                "unavailable": (503, "Local timed speech is unavailable on this server. Captions remain available."),
                "busy": (429, "The local speech renderer is busy. Try again shortly."),
                "timeout": (504, "The local voice took too long; no audio was returned. Captions remain available."),
                "generation_failed": (503, "The local Windows voice could not be generated. Check that the chosen voice is installed; captions remain available."),
                "invalid_output": (503, "The local speech output could not be validated. Captions remain available."),
                "text_too_long": (413, "The current dialogue is too long for local speech. Captions remain available."),
            }
            code, message = errors[exc.reason]
            raise HTTPException(code, message) from None
        async with room.lock:
            if room.paused or room.revision != revision or room.dialogue != text:
                raise HTTPException(409, "The room changed while audio was generated; the old clip was discarded.")
        # Keep the HTTP projection explicit even if a future renderer adds diagnostics.
        keys = ("provider", "voice", "text", "words", "wtimes", "wdurations", "duration_ms",
                "content_type", "audio_base64", "timing_source")
        if not isinstance(result, dict) or result.get("text") != text or result.get("voice") != voice or not all(key in result for key in keys):
            raise HTTPException(503, "The local speech output could not be validated. Captions remain available.")
        return JSONResponse({**{key: result[key] for key in keys}, "revision": revision}, headers={"Cache-Control": "no-store"})

    return router
