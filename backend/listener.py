"""Consent-driven live transcript memory and evidence-bounded conversation analysis.

Audio bytes are sent only to the configured transcription adapter and are never
written to room records. The deterministic detective consumes transcript text,
public released clues, and guest utterances only.
"""
from __future__ import annotations

import asyncio
import os
import re
from dataclasses import dataclass, field
from typing import Mapping

import httpx


TRANSCRIPTION_ENDPOINT = "https://api.openai.com/v1/audio/transcriptions"
DEFAULT_RATE_USD_PER_MINUTE = 0.003
DEFAULT_MAX_AUDIO_SECONDS = 900
MAX_AUDIO_BYTES = 512 * 1024
MAX_TRANSCRIPT_ITEMS = 120
MAX_TRANSCRIPT_CHARS = 40_000
MIME_EXTENSIONS = {
    "audio/webm": "webm",
    "audio/webm;codecs=opus": "webm",
    "audio/ogg;codecs=opus": "ogg",
    "audio/mp4": "m4a",
    "audio/mpeg": "mp3",
}


@dataclass(frozen=True)
class TranscriptionConfig:
    enabled: bool = False
    reason: str = "scripted_default"
    model: str = "gpt-4o-mini-transcribe"
    rate_usd_per_minute: float = DEFAULT_RATE_USD_PER_MINUTE
    max_audio_seconds: int = DEFAULT_MAX_AUDIO_SECONDS
    timeout_seconds: float = 12.0
    api_key: str = field(default="", repr=False)


def load_transcription_config(environ: Mapping[str, str] | None = None) -> TranscriptionConfig:
    env = os.environ if environ is None else environ
    try:
        rate = float(env.get("MYSTERY_TRANSCRIPTION_USD_PER_MINUTE", str(DEFAULT_RATE_USD_PER_MINUTE)))
        allowance = int(env.get("MYSTERY_TRANSCRIPTION_SECONDS_PER_ROOM", str(DEFAULT_MAX_AUDIO_SECONDS)))
        timeout = float(env.get("MYSTERY_TRANSCRIPTION_TIMEOUT", "12"))
        model = str(env.get("MYSTERY_TRANSCRIPTION_MODEL", "gpt-4o-mini-transcribe")).strip()
        key = str(env.get("OPENAI_API_KEY", "")).strip()
        if not 0 <= rate <= 10 or not 1 <= allowance <= 7200 or not 1 <= timeout <= 30:
            raise ValueError
        if not model or len(model) > 100 or len(key) > 1024 or not key.isascii():
            raise ValueError
    except (ValueError, TypeError, OverflowError):
        return TranscriptionConfig(reason="invalid_configuration")
    if str(env.get("MYSTERY_TRANSCRIPTION_ENABLED", "")).strip().lower() != "true":
        reason = "disabled"
    elif str(env.get("MYSTERY_ALLOW_PAID_TRANSCRIPTION", "")).strip().lower() != "true":
        reason = "missing_paid_consent"
    elif not key:
        reason = "missing_api_key"
    else:
        reason = "ready"
    return TranscriptionConfig(reason == "ready", reason, model, rate, allowance, timeout, key)


class TranscriptionError(RuntimeError):
    def __init__(self, reason: str):
        self.reason = reason if reason in {"timeout", "provider_error", "invalid_audio"} else "provider_error"
        super().__init__(self.reason)


class OpenAITranscriber:
    """One bounded short audio chunk per request; raw audio is not retained."""

    def __init__(self, config: TranscriptionConfig, transport: httpx.AsyncBaseTransport | None = None):
        self.config = config
        self.transport = transport

    async def transcribe(self, audio: bytes, mime_type: str) -> str:
        if not self.config.enabled:
            raise TranscriptionError("provider_error")
        extension = MIME_EXTENSIONS.get(mime_type.lower())
        if extension is None or not audio or len(audio) > MAX_AUDIO_BYTES:
            raise TranscriptionError("invalid_audio")
        try:
            async with asyncio.timeout(self.config.timeout_seconds):
                async with httpx.AsyncClient(timeout=self.config.timeout_seconds, transport=self.transport, follow_redirects=False) as client:
                    response = await client.post(
                        TRANSCRIPTION_ENDPOINT,
                        headers={"Authorization": f"Bearer {self.config.api_key}"},
                        data={"model": self.config.model, "response_format": "json"},
                        files={"file": (f"chunk.{extension}", audio, mime_type.split(";")[0])},
                    )
                    response.raise_for_status()
                    if len(response.content) > 65536:
                        raise TranscriptionError("provider_error")
                    body = response.json()
        except (httpx.TimeoutException, TimeoutError):
            raise TranscriptionError("timeout") from None
        except (httpx.HTTPError, ValueError):
            raise TranscriptionError("provider_error") from None
        text = body.get("text") if isinstance(body, dict) else None
        if not isinstance(text, str) or len(text.strip()) > 1200:
            raise TranscriptionError("invalid_audio")
        return text.strip()


def empty_memory() -> dict:
    return {
        "utterances": [],
        "theories": {},
        "follow_up": None,
        "interventions": [],
        "audio_seconds": 0,
        "transcription_calls": 0,
    }


def estimated_cost_usd(audio_seconds: int, rate_per_minute: float) -> float:
    return round(max(0, audio_seconds) * rate_per_minute / 60, 6)


def public_usage(memory: dict, config: TranscriptionConfig) -> dict:
    return {
        "enabled": config.enabled,
        "reason": config.reason,
        "model": config.model if config.enabled else None,
        "audio_seconds": memory["audio_seconds"],
        "audio_limit_seconds": config.max_audio_seconds,
        "transcription_calls": memory["transcription_calls"],
        "estimated_cost_usd": estimated_cost_usd(memory["audio_seconds"], config.rate_usd_per_minute),
        "rate_usd_per_minute": config.rate_usd_per_minute,
        "retained_audio": False,
    }


def _claims(text: str) -> list[dict]:
    """Extract only explicit suspect/place/time statements; never infer guilt."""
    lowered = text.casefold()
    people = {
        "ada": ("ada blackwood", "ada"),
        "felix": ("felix finch", "felix"),
        "margot": ("dr. margot vale", "margot vale", "dr margot", "vale"),
    }
    places = {
        "library": ("library", "study"),
        "music_room": ("music room", "billiard room", "billiards"),
        "telephone": ("telephone", "phone", "on the call"),
        "conservatory": ("conservatory",),
    }
    if not re.search(r"\b(was|were|stayed|remained|stood|sat|recorded|placed|saw)\b", lowered):
        return []
    found = []
    for identity, aliases in people.items():
        if not any(re.search(rf"\b{re.escape(alias)}\b", lowered) for alias in aliases):
            continue
        for place, terms in places.items():
            if not any(term in lowered for term in terms):
                continue
            time = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", lowered)
            if not time:
                continue
            hour = int(time.group(1))
            minute = int(time.group(2) or 0)
            if hour > 12 or minute > 59:
                continue
            suffix = (time.group(3) or "pm").upper()
            found.append({"subject": identity, "place": place, "time": f"{hour}:{minute:02d} {suffix}"})
    return found


def _released_alibi(evidence: list[dict], subject: str, time_label: str) -> dict | None:
    if subject not in {"ada", "felix"}:
        return None
    for clue in evidence:
        if clue.get("id") == "alibi":
            return clue
    return None


def _follow_up(question: str, target: dict, contradiction: dict, clue: dict | None) -> dict:
    proof = f" The released clue “{clue['title']}” records the music-room account." if clue else ""
    return {
        "target_guest_id": target["guest_id"],
        "target_name": target["name"],
        "question": "For the record: " + question + proof + " A contradiction is not a verdict, merely a request for a better account. What is your source, or how should the table reconcile the difference?",
        "contradiction_id": contradiction["id"],
    }


def accept_utterance(
    memory: dict,
    *,
    guest_id: str,
    guest_name: str,
    text: str,
    evidence: list[dict],
) -> dict:
    """Persist a transcript and return safe, deterministic detective events."""
    clean = " ".join(text.split())[:1200]
    if len(clean) < 2:
        raise ValueError("Transcript is too short to add to the room.")
    transcript_id = f"u{memory['utterances'][-1]['sequence'] + 1 if memory['utterances'] else 1}"
    utterance = {
        "id": transcript_id,
        "sequence": int(transcript_id[1:]),
        "guest_id": guest_id,
        "speaker": guest_name[:40],
        "text": clean,
        "claims": _claims(clean),
        "follow_up_answer": False,
    }
    follow_up = memory.get("follow_up")
    if follow_up and follow_up["target_guest_id"] == guest_id and follow_up.get("answer_id") is None:
        utterance["follow_up_answer"] = True
        follow_up["answer_id"] = transcript_id
        follow_up["answer"] = clean
        follow_up["answered"] = True
    memory["utterances"].append(utterance)
    memory["utterances"] = memory["utterances"][-MAX_TRANSCRIPT_ITEMS:]
    while sum(len(item["text"]) for item in memory["utterances"]) > MAX_TRANSCRIPT_CHARS:
        memory["utterances"].pop(0)
    events = [{"type": "listener.utterance", "data": utterance}]

    # Capture explicit, unverified suspect theories and link them to the utterance.
    lowered = clean.casefold()
    for suspect, aliases in {
        "ada": ("ada", "ada blackwood"),
        "felix": ("felix", "felix finch"),
        "margot": ("margot", "vale", "dr. vale"),
    }.items():
        if not any(re.search(rf"\b{re.escape(name)}\b", lowered) for name in aliases):
            continue
        if not any(term in lowered for term in ("think", "theory", "suspect", "might be", "could be", "because", "innocent")):
            continue
        theory = memory["theories"].setdefault(suspect, {"status": "unverified", "supporting": [], "challenging": []})
        (theory["challenging"] if "innocent" in lowered else theory["supporting"]).append(transcript_id)
        theory["status"] = "contested" if theory["supporting"] and theory["challenging"] else "unverified"
        events.append({"type": "listener.theory", "data": {"suspect_id": suspect, **theory}})

    earlier = [item for item in memory["utterances"][:-1] if item["guest_id"] != guest_id]
    # Wait for at least three guests to contribute before actively interrupting.
    distinct = {item["guest_id"] for item in memory["utterances"]}
    if len(distinct) >= 3 and (memory.get("follow_up") is None or memory["follow_up"].get("answered")):
        for claim in utterance["claims"]:
            conflict = next((old for old in earlier for prior in old["claims"]
                             if prior["subject"] == claim["subject"] and prior["time"] == claim["time"]
                             and prior["place"] != claim["place"]), None)
            if not conflict:
                continue
            prior_claim = next(item for item in conflict["claims"] if item["subject"] == claim["subject"] and item["time"] == claim["time"] and item["place"] != claim["place"])
            clue = _released_alibi(evidence, claim["subject"], claim["time"])
            contradiction = {
                "id": f"x{utterance['sequence']}",
                "subject": claim["subject"],
                "time": claim["time"],
                "accounts": [
                    {"guest_id": conflict["guest_id"], "name": conflict["speaker"], "place": prior_claim["place"], "utterance_id": conflict["id"]},
                    {"guest_id": guest_id, "name": guest_name[:40], "place": claim["place"], "utterance_id": transcript_id},
                ],
                "clue_id": clue["id"] if clue else None,
            }
            events.append({"type": "listener.contradiction", "data": contradiction})
            # Prefer asking the participant with fewer recorded turns.
            counts: dict[str, int] = {}
            names: dict[str, str] = {}
            for item in memory["utterances"]:
                counts[item["guest_id"]] = counts.get(item["guest_id"], 0) + 1
                names[item["guest_id"]] = item["speaker"]
            target_id = min(
                (conflict["guest_id"], guest_id),
                key=lambda identity: (counts.get(identity, 0), identity),
            )
            if target_id == conflict["guest_id"]:
                question = f"Earlier you placed {claim['subject'].title()} in the {prior_claim['place'].replace('_', ' ')} at {claim['time']}. Another account places them in the {claim['place'].replace('_', ' ')}."
            else:
                question = f"You placed {claim['subject'].title()} in the {claim['place'].replace('_', ' ')} at {claim['time']}. An earlier account places them in the {prior_claim['place'].replace('_', ' ')}."
            pending = _follow_up(question, {"guest_id": target_id, "name": names[target_id]}, contradiction, clue)
            memory["follow_up"] = pending
            events.append({"type": "listener.follow_up", "data": pending})
            break

    # Invite a quieter guest after three consecutive turns without a reply for them.
    if len(memory["utterances"]) >= 4 and (memory.get("follow_up") is None or memory["follow_up"].get("answered")):
        recent = memory["utterances"][-4:]
        recent_counts: dict[str, int] = {}
        for item in recent:
            recent_counts[item["guest_id"]] = recent_counts.get(item["guest_id"], 0) + 1
        if len(recent_counts) >= 2 and max(recent_counts.values()) >= min(recent_counts.values()) + 2:
            quiet_id = min(recent_counts, key=lambda identity: (recent_counts[identity], identity))
            quiet = next(item for item in recent if item["guest_id"] == quiet_id)
            invitation = {"target_guest_id": quiet_id, "target_name": quiet["speaker"],
                          "question": f"{quiet['speaker']}, the loudest voice is not automatically the best witness. Which released clue most changes your view?"}
            memory["interventions"].append(invitation)
            memory["interventions"] = memory["interventions"][-20:]
            events.append({"type": "listener.invitation", "data": invitation})
    return {"utterance": utterance, "events": events}

