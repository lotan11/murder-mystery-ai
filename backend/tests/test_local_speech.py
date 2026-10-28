"""Local game speech accepts only authoritative public dialogue; no real speech subprocess in tests."""
import asyncio
import base64
import json
from pathlib import Path
import wave

import pytest
from fastapi.testclient import TestClient

from backend.characters import CHARACTERS
from backend.local_speech import LocalSpeechRenderer, SpeechError, TIMING_SOURCE, tv_speech_token
from backend.main import app, rooms


class FakeRenderer:
    available = True
    def __init__(self, reason=None, change=None):
        self.calls = []
        self.reason = reason
        self.change = change

    async def render(self, text, voice):
        self.calls.append((text, voice))
        if self.change:
            self.change()
        if self.reason:
            raise SpeechError(self.reason)
        return {"provider": "windows-sapi", "voice": voice, "text": text,
                "words": text.split(), "wtimes": [i * 100 for i, _ in enumerate(text.split())],
                "wdurations": [80] * len(text.split()), "duration_ms": 1000,
                "content_type": "audio/wav", "audio_base64": base64.b64encode(b"RIFF mocked speech").decode(),
                "timing_source": TIMING_SOURCE}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MYSTERY_DB_PATH", str(tmp_path / "speech.sqlite3"))
    with TestClient(app) as active:
        monkeypatch.setattr(app.state, "local_speech", FakeRenderer())
        yield active


def create(client):
    response = client.post("/api/rooms")
    assert response.status_code == 201
    return response.json()


def auth(token):
    return {"Authorization": "Bearer " + token}


def endpoint(room):
    return f"/api/rooms/{room['room_id']}/speech"


def test_host_config_and_public_status_keep_capability_private(client):
    room = create(client)
    public = client.get("/api/speech/status")
    assert public.status_code == 200 and public.json()["available"]
    assert "tv_token" not in public.json()
    assert public.headers["cache-control"] == "no-store"
    assert client.get(endpoint(room) + "/config").status_code == 401
    config = client.get(endpoint(room) + "/config", headers=auth(room["organizer_token"]))
    assert config.status_code == 200 and config.headers["cache-control"] == "no-store"
    capability = config.json()["tv_token"]
    assert capability == tv_speech_token(rooms[room["room_id"]])
    assert capability != room["organizer_token"]
    assert [voice["id"] for voice in config.json()["voices"]] == ["david", "zira"]
    assert client.get(endpoint(room) + "/config", headers=auth(capability)).status_code == 403
    assert capability not in json.dumps(client.get(f"/api/rooms/{room['room_id']}/state").json())


def test_host_and_tv_capability_speak_current_public_reply_only(client):
    room = create(client)
    saved = rooms[room["room_id"]]
    saved.dialogue = "A released public observation."
    before = saved.record()
    for credential in (room["organizer_token"], tv_speech_token(saved)):
        response = client.post(endpoint(room), headers=auth(credential), json={"voice": "zira"})
        assert response.status_code == 200
        assert response.headers["cache-control"] == "no-store"
        assert response.json()["text"] == saved.dialogue
        assert response.json()["revision"] == saved.revision
        assert response.json()["voice"] == "zira"
        assert response.json()["content_type"] == "audio/wav"
    assert app.state.local_speech.calls == [(saved.dialogue, "zira"), (saved.dialogue, "zira")]
    assert saved.record() == before


def test_speech_token_does_not_authorize_host_controls_or_another_room(client):
    first, second = create(client), create(client)
    token = tv_speech_token(rooms[first["room_id"]])
    assert client.post(endpoint(second), headers=auth(token), json={}).status_code == 403
    assert client.post(endpoint(first) + '?token=' + first["organizer_token"], json={}).status_code == 401
    assert client.post(endpoint(first), headers=auth("unknown guest"), json={}).status_code == 403
    assert app.state.local_speech.calls == []
    with pytest.raises(Exception):
        with client.websocket_connect(f"/ws/{first['room_id']}?role=organizer&token={token}"):
            pass


@pytest.mark.parametrize("body", [
    {"text": "Speak private data"}, {"voice": "david", "text": "'; Start-Process bad"},
    {"voice": {}}, {"voice": []}, {"voice": "external-provider"}, {"voice": True},
    [], "caller text", {"guest_id": "someone", "voice": "david"},
])
def test_arbitrary_text_and_unrecognized_body_are_rejected(client, body):
    room = create(client)
    response = client.post(endpoint(room), headers=auth(room["organizer_token"]), json=body)
    assert response.status_code == 422
    assert app.state.local_speech.calls == []


def test_large_body_rejected_before_renderer(client):
    room = create(client)
    response = client.post(endpoint(room), headers=auth(room["organizer_token"]), content=b"x" * 129)
    assert response.status_code == 413 and not app.state.local_speech.calls


def test_private_card_or_introduction_never_enters_renderer(client):
    room = create(client)
    saved = rooms[room["room_id"]]
    saved.guests["g"] = {"name": "Private roster marker", "token": "private-token"}
    saved.assignments["g"] = "margot"
    saved.introductions["g"] = "Voluntary introduction marker"
    saved.dialogue = "Only the current public detective reply."
    result = client.post(endpoint(room), headers=auth(room["organizer_token"]), json={})
    assert result.status_code == 200
    sent = json.dumps(app.state.local_speech.calls)
    assert saved.dialogue in sent
    assert CHARACTERS["margot"]["private_brief"] not in sent
    assert "Private roster marker" not in sent and "Voluntary introduction marker" not in sent
    assert "private-token" not in sent


@pytest.mark.parametrize("property,value,status", [("paused", True, 409), ("dialogue", "", 409), ("dialogue", "x" * 1501, 413)])
def test_pause_empty_and_bounded_text_do_not_start_generation(client, property, value, status):
    room = create(client)
    setattr(rooms[room["room_id"]], property, value)
    assert client.post(endpoint(room), headers=auth(room["organizer_token"]), json={}).status_code == status
    assert app.state.local_speech.calls == []


@pytest.mark.parametrize("reason,status", [("unavailable", 503), ("busy", 429), ("timeout", 504), ("generation_failed", 503), ("invalid_output", 503)])
def test_renderer_errors_are_safe_and_caption_friendly(client, monkeypatch, reason, status):
    room = create(client)
    monkeypatch.setattr(app.state, "local_speech", FakeRenderer(reason=reason))
    response = client.post(endpoint(room), headers=auth(room["organizer_token"]), json={})
    assert response.status_code == status
    assert "audio_base64" not in response.text
    assert room["organizer_token"] not in response.text


@pytest.mark.parametrize("change", ["revision", "pause", "dialogue"])
def test_generation_holds_no_room_lock_and_discards_stale_audio(client, monkeypatch, change):
    room = create(client)
    saved = rooms[room["room_id"]]
    def mutate():
        assert not saved.lock.locked()
        if change == "revision": saved.revision += 1
        elif change == "pause": saved.paused = True
        else: saved.dialogue = "New current text."
    monkeypatch.setattr(app.state, "local_speech", FakeRenderer(change=mutate))
    response = client.post(endpoint(room), headers=auth(room["organizer_token"]), json={})
    assert response.status_code == 409 and "audio_base64" not in response.text


def write_render(directory, text, voice):
    words = text.split()
    with wave.open(str(directory / "speech.wav"), "wb") as audio:
        audio.setnchannels(1); audio.setsampwidth(2); audio.setframerate(16000)
        audio.writeframes(b"\0\0" * 16000)
    (directory / "speech.json").write_text(json.dumps({
        "text": text, "voice": voice, "words": words,
        "wtimes": [i * 100 for i in range(len(words))], "wdurations": [80] * len(words),
    }), encoding="utf-8")


class FakeProcess:
    def __init__(self, held=False, code=0):
        self.returncode = None
        self.code = code
        self.killed = False
        self.waited = 0
        self.event = asyncio.Event()
        if not held: self.event.set()

    async def wait(self):
        self.waited += 1
        await self.event.wait()
        if self.returncode is None: self.returncode = self.code
        return self.returncode

    def kill(self):
        self.killed = True
        self.returncode = -9
        self.event.set()


def renderer(tmp_path):
    executable = tmp_path / "powershell.exe"
    executable.write_bytes(b"test marker, never executed")
    return LocalSpeechRenderer(base_dir=tmp_path / "generated", executable=executable, platform_name="win32", timeout=0.03)


def test_non_windows_returns_unavailable_without_subprocess(tmp_path, monkeypatch):
    async def forbidden(*args, **kwargs):
        raise AssertionError("No process is allowed")
    monkeypatch.setattr(asyncio, "create_subprocess_exec", forbidden)
    instance = LocalSpeechRenderer(base_dir=tmp_path, platform_name="linux")
    assert instance.available is False
    async def run():
        with pytest.raises(SpeechError, match="unavailable"):
            await instance.render("Public words.", "david")
    asyncio.run(run())


def test_subprocess_receives_literal_json_not_interpolated_dialogue(tmp_path, monkeypatch):
    captured = {}
    text = "Public words only."
    async def create_process(*args, **kwargs):
        captured["args"], captured["kwargs"] = args, kwargs
        payload = Path(args[args.index("-InputFile") + 1])
        data = json.loads(payload.read_text(encoding="utf-8"))
        assert data == {"text": text, "voice": "david"}
        write_render(payload.parent, data["text"], data["voice"])
        return FakeProcess()
    monkeypatch.setenv("OPENAI_API_KEY", "should-not-reach-voice-process")
    monkeypatch.setattr(asyncio, "create_subprocess_exec", create_process)
    async def run():
        instance = renderer(tmp_path)
        result = await instance.render(text, "david")
        assert result["text"] == text and result["content_type"] == "audio/wav"
        assert result["words"] == text.split()
        assert not list(instance.base_dir.iterdir())
    asyncio.run(run())
    assert text not in captured["args"]
    assert "OPENAI_API_KEY" not in captured["kwargs"]["env"]
    assert "shell" not in captured["kwargs"]
    assert Path(captured["args"][0]).is_absolute()


def test_timeout_kills_and_reaps_before_temporary_cleanup(tmp_path, monkeypatch):
    process_holder = []
    async def create_process(*args, **kwargs):
        process = FakeProcess(held=True)
        process_holder.append(process)
        return process
    monkeypatch.setattr(asyncio, "create_subprocess_exec", create_process)
    async def run():
        instance = renderer(tmp_path)
        with pytest.raises(SpeechError, match="timeout"):
            await instance.render("Public words.", "david")
        assert process_holder[0].killed and process_holder[0].waited >= 2
        assert not instance._busy and not list(instance.base_dir.iterdir())
    asyncio.run(run())


def test_cancellation_kills_and_reaps_before_cleanup(tmp_path, monkeypatch):
    holder = []
    async def create_process(*args, **kwargs):
        process = FakeProcess(held=True); holder.append(process); return process
    monkeypatch.setattr(asyncio, "create_subprocess_exec", create_process)
    async def run():
        instance = renderer(tmp_path)
        instance.timeout = 10
        task = asyncio.create_task(instance.render("Public words.", "david"))
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError): await task
        assert holder[0].killed and holder[0].waited >= 2
        assert not instance._busy and not list(instance.base_dir.iterdir())
    asyncio.run(run())


def test_global_renderer_slot_rejects_concurrency_without_second_process(tmp_path, monkeypatch):
    holder = []
    async def create_process(*args, **kwargs):
        data = json.loads(Path(args[args.index("-InputFile") + 1]).read_text())
        write_render(Path(args[args.index("-OutputDirectory") + 1]), data["text"], data["voice"])
        process = FakeProcess(held=True); holder.append(process); return process
    monkeypatch.setattr(asyncio, "create_subprocess_exec", create_process)
    async def run():
        instance = renderer(tmp_path)
        instance.timeout = 10
        first = asyncio.create_task(instance.render("Public words.", "david"))
        await asyncio.sleep(0)
        with pytest.raises(SpeechError, match="busy"):
            await instance.render("Another request.", "zira")
        holder[0].event.set()
        assert (await first)["voice"] == "david"
        assert len(holder) == 1
    asyncio.run(run())


def test_invalid_generated_output_never_returns_audio(tmp_path, monkeypatch):
    async def create_process(*args, **kwargs):
        directory = Path(args[args.index("-OutputDirectory") + 1])
        write_render(directory, "Wrong hidden text.", "david")
        return FakeProcess()
    monkeypatch.setattr(asyncio, "create_subprocess_exec", create_process)
    async def run():
        with pytest.raises(SpeechError, match="invalid_output"):
            await renderer(tmp_path).render("Public words.", "david")
    asyncio.run(run())
