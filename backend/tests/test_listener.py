"""Consent, bounded transcript memory and the three-guest contradiction demonstration."""
import asyncio
import struct
import threading
from contextlib import ExitStack
from dataclasses import replace

import pytest
from fastapi.testclient import TestClient

from backend.listener import (TranscriptionConfig, OpenAITranscriber, accept_utterance, empty_memory,
                              estimated_cost_usd, load_transcription_config)
from backend.main import Room, app, rooms
from backend.local_speech import tv_speech_token
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


def webm_clip(seconds=3.0):
    info_payload = bytes.fromhex("448988") + struct.pack(">d", seconds * 1000)
    info = bytes.fromhex("1549a966") + bytes([0x80 | len(info_payload)]) + info_payload
    return bytes.fromhex("1a45dfa38018538067") + bytes([0x80 | len(info)]) + info


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
            ("Cecily", "Ada remained in the music room at 9:20."),
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
        ws.send_json({"type": "listener.audio", "duration_seconds": 3, "mime_type": "audio/webm"})
        assert ws.receive_json()["type"] == "listener.status"
        ws.send_bytes(b"not allowed")
        error = ws.receive_json()
        assert error["type"] == "listener.error" and error["code"] == "invalid_audio"
        ws.send_json({"type": "listener.mute"})
        assert ws.receive_json()["type"] == "listener.status"
        ws.send_json({"type": "listener.transcript", "text": "A clue."})
        assert ws.receive_json()["type"] == "error"
        ws.send_json({"type": "listener.resume", "consent": False})
        assert ws.receive_json()["type"] == "error"
        ws.send_json({"type": "listener.resume", "consent": True})
        resumed = ws.receive_json()
        assert resumed["type"] == "listener.status" and resumed["listening"] and not resumed["muted"]
        ws.send_json({"type": "listener.transcript", "text": "A clue after resuming."})
        while True:
            packet = ws.receive_json()
            if packet.get("type") == "state" and packet["data"]["listener"]["utterances"]:
                break
        assert guest_id in rooms[room_id].guests


def test_room_reset_emits_listener_reset_for_lobby_sessions(client):
    created = client.post("/api/rooms").json()
    room = rooms[created["room_id"]]
    with client.websocket_connect(f"/ws/{room.room_id}?role=organizer&token={created['organizer_token']}") as host:
        host.receive_json()
        with client.websocket_connect(f"/ws/{room.room_id}?role=guest") as guest:
            join(guest, "Lobby Listener")
            guest.send_json({"type": "listener.start", "consent": True, "source": "typed"})
            assert guest.receive_json()["type"] == "listener.status"
            host.send_json({"type": "control", "action": "reset"})
            while True:
                event = guest.receive_json()
                if event.get("type") == "listener.reset":
                    break
            session = next(iter(room.listener_sessions.values()))
            assert not session["listening"] and session["muted"]


def test_disabled_transcription_reports_listener_error_without_calling_provider(client):
    created = client.post("/api/rooms").json()
    room = rooms[created["room_id"]]
    with client.websocket_connect(f"/ws/{room.room_id}?role=guest") as ws:
        join(ws, "Disabled Mic")
        ws.send_json({"type": "listener.start", "consent": True, "source": "microphone"})
        assert ws.receive_json()["type"] == "listener.status"
        ws.send_json({"type": "listener.audio", "duration_seconds": 3, "mime_type": "audio/webm"})
        assert ws.receive_json()["type"] == "listener.status"
        ws.send_bytes(webm_clip())
        while True:
            event = ws.receive_json()
            if event.get("type") == "listener.error":
                break
        assert event["code"] == "disabled"
        assert "Microphone transcription is disabled" in event["message"]
        assert room.listener["transcription_calls"] == 0


def test_authorized_tv_speaking_state_suppresses_capture_and_clears_on_disconnect(client):
    created = client.post("/api/rooms").json()
    room_id = created["room_id"]
    room = rooms[room_id]
    with client.websocket_connect(f"/ws/{room_id}?role=guest") as guest:
        join(guest, "Echo Test Guest")
        revision = room.revision
        with client.websocket_connect(f"/ws/{room_id}?role=tv&token={tv_speech_token(room)}") as tv:
            assert tv.receive_json()["type"] == "state"
            tv.send_json({"type": "scholar.speaking", "speaking": True})
            while True:
                event = guest.receive_json()
                if event.get("type") == "state" and event["data"].get("scholar_speaking") is True:
                    break
            assert len(room.speech_clients) == 1
            assert room.revision == revision
            assert "speech_clients" not in room.record()
            with client.websocket_connect(f"/ws/{room_id}?role=tv") as untrusted_tv:
                reconnect_snapshot = untrusted_tv.receive_json()
                assert reconnect_snapshot["data"]["scholar_speaking"] is True
                untrusted_tv.send_json({"type": "scholar.speaking", "speaking": False})
                assert untrusted_tv.receive_json()["type"] == "error"
                assert room.speech_clients
            assert room.snapshot()["scholar_speaking"] is True
        while True:
            event = guest.receive_json()
            if event.get("type") == "state" and event["data"].get("scholar_speaking") is False:
                break
        assert not room.speech_clients


def test_tv_disconnect_cleanup_survives_asgi_scope_cancellation(client, monkeypatch):
    from backend import main
    created = client.post("/api/rooms").json()
    room = rooms[created["room_id"]]
    original_broadcast = main.broadcast
    armed = threading.Event()
    delivered = threading.Event()

    async def delayed_disconnect_broadcast(current):
        cleanup = current is room and armed.is_set() and not room.speech_clients
        if cleanup:
            # TestClient cancels the ASGI scope immediately after sending disconnect.
            # A real notification checkpoint must not skip cleanup or lose the flag.
            await asyncio.sleep(0.03)
        await original_broadcast(current)
        if cleanup:
            delivered.set()

    monkeypatch.setattr(main, "broadcast", delayed_disconnect_broadcast)
    with client.websocket_connect(f"/ws/{room.room_id}?role=guest") as guest:
        join(guest, "Cancellation Guest")
        revision = room.revision
        with client.websocket_connect(f"/ws/{room.room_id}?role=tv&token={tv_speech_token(room)}") as tv:
            tv.receive_json()
            tv.send_json({"type": "scholar.speaking", "speaking": True})
            while True:
                packet = guest.receive_json()
                if packet.get("type") == "state" and packet["data"]["scholar_speaking"]:
                    break
            armed.set()
        # Bound the assertion before reading: a missed notification must fail, not hang.
        assert delivered.wait(1), "TV cancellation lost the microphone recovery notification"
        assert not room.speech_clients and len(room.clients) == 1
        assert room.revision == revision
        while True:
            packet = guest.receive_json()
            if packet.get("type") == "state" and packet["data"]["scholar_speaking"] is False:
                break


@pytest.mark.parametrize("interruption", ["stop", "reset"])
def test_delayed_transcription_is_cancelled_and_discarded_after_stop_or_reset(client, interruption):
    created = client.post("/api/rooms").json()
    room = rooms[created["room_id"]]
    room.act = 1
    app.state.room_store.save(room.record())
    started, release, finished = threading.Event(), threading.Event(), threading.Event()
    calls = []

    class DelayedTranscriber:
        async def transcribe(self, *_args):
            calls.append("started")
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
            assert guest.receive_json()["type"] == "listener.status"
            guest.send_bytes(webm_clip())
            assert started.wait(3), "transcription worker did not start"
            # These clips are accepted into the worker queue while the first is in flight.
            for _ in range(2):
                guest.send_json({"type": "listener.audio", "duration_seconds": 0.5, "mime_type": "audio/webm"})
                while guest.receive_json()["type"] != "listener.status":
                    pass
                guest.send_bytes(webm_clip(0.5))
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
            assert calls == ["started"], "queued stale chunks were transcribed after interruption"
            assert all(item["text"] != "Stale audio from the previous listening session." for item in room.listener["utterances"])


@pytest.mark.parametrize("interruption", ["pause_resume", "disconnect_reconnect"])
def test_delayed_transcription_cannot_cross_pause_or_socket_reconnect(client, interruption):
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
                return "An answer from before the session boundary."
            finally:
                finished.set()

    app.state.transcriber = DelayedTranscriber()
    app.state.transcription_config = replace(app.state.transcription_config, enabled=True, reason="ready")
    with client.websocket_connect(f"/ws/{room.room_id}?role=organizer&token={created['organizer_token']}") as host:
        host.receive_json()
        with client.websocket_connect(f"/ws/{room.room_id}?role=guest") as guest:
            guest_id = join(guest, "Boundary Guest")
            guest.send_json({"type": "listener.start", "consent": True, "source": "microphone"})
            assert guest.receive_json()["type"] == "listener.status"
            guest.send_json({"type": "listener.audio", "duration_seconds": 3, "mime_type": "audio/webm"})
            assert guest.receive_json()["type"] == "listener.status"
            guest.send_bytes(webm_clip())
            assert started.wait(3)
            if interruption == "pause_resume":
                host.send_json({"type": "control", "action": "pause"})
                while not host.receive_json().get("data", {}).get("paused", False):
                    pass
                host.send_json({"type": "control", "action": "resume"})
                while host.receive_json().get("data", {}).get("paused", True):
                    pass
                guest.send_json({"type": "listener.resume", "consent": True})
                while guest.receive_json()["type"] != "listener.status":
                    pass
                release.set()
                assert finished.wait(3)
            else:
                token = room.guests[guest_id]["token"]
                guest.close()
                assert finished.wait(3), "disconnect did not cancel transcription"
                with client.websocket_connect(f"/ws/{room.room_id}?role=guest&guest_token={token}") as reconnected:
                    reconnected.receive_json()  # current authoritative state
                    assert reconnected.receive_json()["type"] == "joined"
                    reconnected.receive_json()  # private character state
                    release.set()
                    assert room.listener["utterances"] == []
            assert room.listener["utterances"] == []
            assert all(item["text"] != "An answer from before the session boundary." for item in room.listener["utterances"])


@pytest.mark.parametrize("failure", ["provider", "allowance"])
def test_provider_failure_and_allowance_exhaustion_are_reported_without_transcript(client, failure):
    created = client.post("/api/rooms").json()
    room = rooms[created["room_id"]]
    app.state.transcription_config = replace(app.state.transcription_config, enabled=True, reason="ready",
                                               max_audio_seconds=1 if failure == "allowance" else 900)

    class FailingTranscriber:
        async def transcribe(self, *_args):
            from backend.listener import TranscriptionError
            raise TranscriptionError("provider_error")

    app.state.transcriber = FailingTranscriber()
    with client.websocket_connect(f"/ws/{room.room_id}?role=guest") as ws:
        join(ws, "Listener Guest")
        ws.send_json({"type": "listener.start", "consent": True, "source": "microphone"})
        assert ws.receive_json()["type"] == "listener.status"
        ws.send_json({"type": "listener.audio", "duration_seconds": 3, "mime_type": "audio/webm"})
        assert ws.receive_json()["type"] == "listener.status"
        ws.send_bytes(webm_clip())
        while True:
            packet = ws.receive_json()
            if packet.get("type") == "listener.error":
                break
        assert packet["code"] == ("provider_error" if failure == "provider" else "allowance_exhausted")
        assert room.listener["utterances"] == []
        if failure == "allowance":
            assert room.listener["transcription_calls"] == 0


def test_audio_usage_uses_verified_container_duration_and_rejects_client_mismatch(client):
    created = client.post("/api/rooms").json()
    room = rooms[created["room_id"]]
    app.state.transcription_config = replace(app.state.transcription_config, enabled=True, reason="ready")
    observed = []

    class RecordingTranscriber:
        async def transcribe(self, audio, mime_type):
            observed.append((audio, mime_type))
            return "The guests discussed a test clip."

    app.state.transcriber = RecordingTranscriber()
    with client.websocket_connect(f"/ws/{room.room_id}?role=guest") as ws:
        join(ws, "Audio Guest")
        ws.send_json({"type": "listener.start", "consent": True, "source": "microphone"})
        assert ws.receive_json()["type"] == "listener.status"
        ws.send_json({"type": "listener.audio", "duration_seconds": 3.0, "mime_type": "audio/webm;codecs=opus"})
        assert ws.receive_json()["type"] == "listener.status"
        ws.send_bytes(webm_clip(3.0))
        confirmation = None
        while True:
            packet = ws.receive_json()
            if packet.get("type") == "listener.confirmation_required":
                confirmation = packet
                break
        assert room.listener["utterances"] == []
        assert confirmation["text"] == "The guests discussed a test clip."
        assert confirmation["guests"] == [{"id": next(iter(room.guests)), "name": "Audio Guest"}]
        ws.send_json({"type": "listener.confirm_transcript", "id": confirmation["id"], "speaker_id": next(iter(room.guests))})
        while True:
            packet = ws.receive_json()
            if packet.get("type") == "state" and packet["data"]["listener"]["utterances"]:
                break
        assert room.listener["audio_seconds"] == 3
        assert room.listener["transcription_calls"] == 1
        assert observed == [(webm_clip(3.0), "audio/webm;codecs=opus")]
        assert room.listener["utterances"][0]["guest_id"] == next(iter(room.guests))

        ws.send_json({"type": "listener.resume", "consent": True})
        while ws.receive_json()["type"] != "listener.status":
            pass
        ws.send_json({"type": "listener.audio", "duration_seconds": 1.0, "mime_type": "audio/webm"})
        while ws.receive_json()["type"] != "listener.status":
            pass
        ws.send_bytes(webm_clip(3.0))
        error = ws.receive_json()
        while error["type"] != "listener.error":
            error = ws.receive_json()
        assert error["type"] == "listener.error" and error["code"] == "invalid_audio"
        assert "does not match" in error["message"]
        assert room.listener["audio_seconds"] == 3
        assert room.listener["transcription_calls"] == 1


def test_unattributed_audio_is_remembered_without_claims_or_interrogation():
    memory = empty_memory()
    result = accept_utterance(memory, guest_id=None, guest_name="Unattributed audio",
                              text="Ada was in the library at 9:20.", evidence=[])
    item = memory["utterances"][0]
    assert item["guest_id"] is None
    assert item["speaker"] == "Unattributed audio"
    assert item["claims"] == []
    assert memory["theories"] == {}
    assert not any(event["type"] in {"listener.contradiction", "listener.follow_up"} for event in result["events"])


def test_microphone_source_can_be_marked_uncertain_without_assigning_the_owner(client):
    created = client.post("/api/rooms").json()
    room = rooms[created["room_id"]]
    app.state.transcription_config = replace(app.state.transcription_config, enabled=True, reason="ready")

    class Transcriber:
        async def transcribe(self, *_args):
            return "I suspect Ada because she lied."

    app.state.transcriber = Transcriber()
    with client.websocket_connect(f"/ws/{room.room_id}?role=guest") as ws:
        join(ws, "Mic Owner")
        owner = next(iter(room.guests))
        ws.send_json({"type": "listener.start", "consent": True, "source": "microphone"})
        assert ws.receive_json()["type"] == "listener.status"
        ws.send_json({"type": "listener.audio", "duration_seconds": 3, "mime_type": "audio/webm"})
        assert ws.receive_json()["type"] == "listener.status"
        ws.send_bytes(webm_clip())
        confirmation = None
        while confirmation is None:
            packet = ws.receive_json()
            if packet.get("type") == "listener.confirmation_required":
                confirmation = packet
        assert room.listener["utterances"] == []
        ws.send_json({"type": "listener.confirm_transcript", "id": confirmation["id"], "speaker_id": "unattributed"})
        while ws.receive_json()["type"] != "listener.confirmation_cleared":
            pass
        listener = client.get(f"/api/rooms/{room.room_id}/state").json()["listener"]
        item = listener["utterances"][0]
        assert item["guest_id"] is None and item["speaker"] == "Unattributed audio"
        assert item["claims"] == [] and listener["theories"] == {}
        assert owner in room.guests


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
