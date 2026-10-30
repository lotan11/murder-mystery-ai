"""Consent, bounded transcript memory and the three-guest contradiction demonstration."""
import asyncio
import threading
from contextlib import ExitStack
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from backend.listener import (TranscriptionConfig, OpenAITranscriber, accept_utterance, empty_memory,
                              estimated_cost_usd, load_transcription_config)
from backend.main import Room, app, rooms
from backend.storage import RoomStore


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MYSTERY_DB_PATH", str(tmp_path / "listener.sqlite3"))
    rooms.clear()
    with TestClient(app) as active:
        yield active


def join(ws, name):
    assert ws.receive_json()["type"] == "state"
    ws.send_json({"type": "join", "name": name})
    joined = ws.receive_json()
    assert joined["type"] == "joined"
    assert ws.receive_json()["type"] == "state"
    assert ws.receive_json()["type"] == "private"
    return joined["guest_id"]


def test_three_guest_contradiction_followup_and_answer_are_remembered(client):
    created = client.post("/api/rooms").json()
    room_id = created["room_id"]
    room = rooms[room_id]
    room.act = 2
    room.revealed.append("alibi")
    app.state.room_store.save(room.record())
    guests = {}
    with ExitStack() as stack:
        for name in ("Iris", "Basil", "Cecily"):
            ws = stack.enter_context(client.websocket_connect(f"/ws/{room_id}?role=guest"))
            guests[name] = (ws, join(ws, name))
            ws.send_json({"type": "listener.start", "consent": True, "source": "typed"})
            assert ws.receive_json()["type"] == "listener.status"

        observations = (
            ("Iris", "Ada was in the library at 9:20."),
            ("Basil", "Felix remained in the music room at 9:20."),
            ("Cecily", "I heard Ada remained in the music room at 9:20 on the recording."),
        )
        for name, text in observations:
            ws = guests[name][0]
            ws.send_json({"type": "listener.transcript", "text": text})
            while True:
                packet = ws.receive_json()
                if packet.get("type") == "state" and any(item["text"] == text for item in packet["data"]["listener"]["utterances"]):
                    break

        state = client.get(f"/api/rooms/{room_id}/state").json()
        listener = state["listener"]
        assert len(listener["utterances"]) == 3
        assert listener["follow_up"] is not None
        assert listener["follow_up"]["target_name"] in {"Iris", "Cecily"}
        assert "reconcile" in listener["follow_up"]["question"]

        target = listener["follow_up"]["target_guest_id"]
        answer_ws = next(ws for ws, guest_id in guests.values() if guest_id == target)
        answer_ws.send_json({"type": "listener.transcript", "text": "My account came from the guest list, not a recording."})
        remembered = client.get(f"/api/rooms/{room_id}/state").json()["listener"]
        assert remembered["follow_up"]["answered"] is True
        assert remembered["follow_up"]["answer"] == "My account came from the guest list, not a recording."
        assert remembered["utterances"][-1]["follow_up_answer"] is True
        assert remembered["usage"]["retained_audio"] is False
        assert "The solution" not in str(remembered)

    saved = RoomStore(app.state.room_store.path).load_all()[0]
    assert saved["schema_version"] == 4
    assert saved["listener"]["follow_up"]["answer"] == "My account came from the guest list, not a recording."


def test_listener_consent_pause_and_binary_audio_requirements(client):
    created = client.post("/api/rooms").json()
    room_id = created["room_id"]
    with client.websocket_connect(f"/ws/{room_id}?role=guest") as ws:
        guest_id = join(ws, "Ada Guest")
        ws.send_json({"type": "listener.start", "consent": False})
        assert ws.receive_json()["type"] == "error"
        ws.send_json({"type": "listener.start", "consent": True})
        assert ws.receive_json()["type"] == "listener.status"
        ws.send_bytes(b"not allowed")
        assert "Microphone transcription is disabled" in ws.receive_json()["message"]
        ws.send_json({"type": "listener.mute"})
        assert ws.receive_json()["type"] == "listener.status"
        ws.send_json({"type": "listener.transcript", "text": "A clue."})
        assert ws.receive_json()["type"] == "error"
        assert guest_id in rooms[room_id].guests


@pytest.mark.parametrize("interruption", ["stop", "reset"])
def test_delayed_transcription_is_cancelled_and_discarded_after_stop_or_reset(client, interruption):
    created = client.post("/api/rooms").json()
    room = rooms[created["room_id"]]
    room.act = 1
    app.state.room_store.save(room.record())
    started, release, finished = threading.Event(), threading.Event(), threading.Event()

    class DelayedTranscriber:
        async def transcribe(self, *_args):
            started.set()
            try:
                while not release.is_set():
                    await asyncio.sleep(0.01)
                return "Stale audio from the previous listening session."
            finally:
                finished.set()

    app.state.transcriber = DelayedTranscriber()
    app.state.transcription_config = replace(app.state.transcription_config, enabled=True, reason="ready")
    with client.websocket_connect(f"/ws/{room.room_id}?role=organizer&token={created['organizer_token']}") as host:
        assert host.receive_json()["type"] == "state"
        with client.websocket_connect(f"/ws/{room.room_id}?role=guest") as guest:
            join(guest, "Delayed Guest")
            guest.send_json({"type": "listener.start", "consent": True, "source": "microphone"})
            assert guest.receive_json()["type"] == "listener.status"
            guest.send_json({"type": "listener.audio", "duration_seconds": 3, "mime_type": "audio/webm"})
            guest.send_bytes(b"small injected clip")
            assert started.wait(3), "transcription worker did not start"
            if interruption == "stop":
                guest.send_json({"type": "listener.stop"})
            else:
                host.send_json({"type": "control", "action": "reset"})
                while True:
                    packet = host.receive_json()
                    if packet.get("type") == "state" and packet["data"]["act"] == 0:
                        break
                guest.send_json({"type": "listener.stop"})
            while True:
                packet = guest.receive_json()
                if packet.get("type") == "listener.status" and packet["listening"] is False:
                    break
            release.set()
            assert finished.wait(3), "cancelled transcription did not settle"
            assert room.listener["utterances"] == []
            assert all(item["text"] != "Stale audio from the previous listening session." for item in room.listener["utterances"])


def test_transcription_stays_off_without_both_explicit_flags():
    assert load_transcription_config({"OPENAI_API_KEY": "secret"}).reason == "disabled"
    assert load_transcription_config({"MYSTERY_TRANSCRIPTION_ENABLED": "true", "OPENAI_API_KEY": "secret"}).reason == "missing_paid_consent"
    assert load_transcription_config({"MYSTERY_TRANSCRIPTION_ENABLED": "true", "MYSTERY_ALLOW_PAID_TRANSCRIPTION": "true"}).reason == "missing_api_key"
    assert estimated_cost_usd(60, 0.003) == 0.003


@pytest.mark.anyio
async def test_transcriber_uses_bounded_mocked_request_without_retaining_audio():
    observed = {}

    async def handler(request):
        observed["url"] = str(request.url)
        observed["body"] = request.content
        return httpx.Response(200, json={"text": "The clock stopped at nine."})

    import httpx
    config = TranscriptionConfig(enabled=True, reason="ready", api_key="test-key")
    transcriber = OpenAITranscriber(config, transport=httpx.MockTransport(handler))
    assert await transcriber.transcribe(b"short test clip", "audio/webm") == "The clock stopped at nine."
    assert observed["url"] == "https://api.openai.com/v1/audio/transcriptions"
    assert b"gpt-4o-mini-transcribe" in observed["body"]
    assert b"short test clip" in observed["body"]


def test_detective_uses_only_released_clues_and_retains_the_answer():
    memory = empty_memory()
    for guest_id, name, text in (
        ("g1", "One", "Ada was in the library at 9:20."),
        ("g2", "Two", "Felix remained in the music room at 9:20."),
    ):
        accept_utterance(memory, guest_id=guest_id, guest_name=name, text=text, evidence=[])
    result = accept_utterance(memory, guest_id="g3", guest_name="Three",
        text="Ada remained in the music room at 9:20.", evidence=[])
    contradiction = next(event["data"] for event in result["events"] if event["type"] == "listener.contradiction")
    assert contradiction["clue_id"] is None
    follow_up = next(event["data"] for event in result["events"] if event["type"] == "listener.follow_up")
    answer_id = follow_up["target_guest_id"]
    accept_utterance(memory, guest_id=answer_id, guest_name="Answering Guest",
        text="I was repeating what I heard at the table.", evidence=[])
    assert memory["follow_up"]["answered"]
    assert memory["follow_up"]["answer"] == "I was repeating what I heard at the table."
