"""Approved Lewis endpoint and child lifecycle; fake renderer/process only in tests."""
import asyncio
import base64
import json
from pathlib import Path
import wave

import pytest
from fastapi.testclient import TestClient

from backend.characters import CHARACTERS
from backend.local_speech import tv_speech_token
from backend.main import app, rooms
from backend.scholar_speech import ScholarSpeechError, ScholarSpeechRenderer
from backend.tests.test_local_speech import FakeProcess


class FakeScholar:
    available = True
    def __init__(self, reason=None, change=None, extra=None):
        self.reason, self.change, self.extra = reason, change, extra or {}
        self.calls = []

    async def render(self, text):
        self.calls.append(text)
        if self.change: self.change()
        if self.reason: raise ScholarSpeechError(self.reason)
        return {"provider": "kokoro-onnx", "voice": "bm_lewis", "text": text, "duration_ms": 1000,
                "content_type": "audio/wav", "audio_base64": base64.b64encode(b"RIFF fake neural clip").decode(),
                "playback_rate": 1.05, **self.extra}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MYSTERY_DB_PATH", str(tmp_path / "scholar.sqlite3"))
    with TestClient(app) as client:
        monkeypatch.setattr(app.state, "scholar_speech", FakeScholar())
        yield client


def room(client):
    return client.post("/api/rooms").json()


def auth(token):
    return {"Authorization": "Bearer " + token}


def endpoint(created):
    return f"/api/rooms/{created['room_id']}/scholar-speech"


def test_status_describes_fixed_approved_voice_without_credential(client):
    response = client.get("/api/scholar-speech/status")
    data = response.json()
    assert response.status_code == 200 and response.headers["cache-control"] == "no-store"
    assert data["available"] and data["provider"] == "kokoro-onnx"
    assert data["voice"] == "bm_lewis" and data["playback_rate"] == 1.05
    assert "token" not in data and "word timings" in data["message"]


def test_existing_host_and_scoped_tv_capability_render_current_public_reply(client):
    created = room(client)
    saved = rooms[created["room_id"]]
    saved.dialogue = "Current released public facts."
    before = saved.record()
    for credential in (created["organizer_token"], tv_speech_token(saved)):
        response = client.post(endpoint(created), headers=auth(credential), json={})
        assert response.status_code == 200 and response.headers["cache-control"] == "no-store"
        data = response.json()
        assert data["voice"] == "bm_lewis" and data["playback_rate"] == 1.05
        assert data["provider"] == "kokoro-onnx" and data["text"] == saved.dialogue
        assert data["revision"] == saved.revision
        assert not {"words", "wtimes", "wdurations", "visemes"} & set(data)
    assert app.state.scholar_speech.calls == [saved.dialogue, saved.dialogue]
    assert saved.record() == before


def test_read_only_capability_does_not_cross_rooms_and_query_credentials_are_rejected(client):
    first, second = room(client), room(client)
    capability = tv_speech_token(rooms[first["room_id"]])
    assert client.post(endpoint(second), headers=auth(capability), json={}).status_code == 403
    assert client.post(endpoint(first), headers=auth("guest-token"), json={}).status_code == 403
    assert client.post(endpoint(first) + "?token=" + first["organizer_token"], json={}).status_code == 401
    assert app.state.scholar_speech.calls == []


@pytest.mark.parametrize("body", [{"voice": "bm_lewis"}, {"voice": "bm_george"}, {"text": "Private input"}, {"guest_id": "other"}, [], "speak this", None])
def test_no_client_text_or_voice_choice_is_accepted(client, body):
    created = room(client)
    # Explicit JSON null differs from an absent request body.
    response = client.post(endpoint(created), headers=auth(created["organizer_token"]), content=json.dumps(body))
    assert response.status_code == 422
    assert app.state.scholar_speech.calls == []


def test_oversized_request_is_bounded_before_generation(client):
    created = room(client)
    assert client.post(endpoint(created), headers=auth(created["organizer_token"]), content=b" " * 33).status_code == 413
    assert not app.state.scholar_speech.calls


def test_private_cards_roster_and_introductions_never_enter_voice_worker(client):
    created = room(client)
    saved = rooms[created["room_id"]]
    saved.guests["g"] = {"name": "Private roster marker", "token": "private credential"}
    saved.assignments["g"] = "margot"
    saved.introductions["g"] = "An introduction marker"
    saved.dialogue = "The currently released detective line."
    response = client.post(endpoint(created), headers=auth(created["organizer_token"]), json={})
    assert response.status_code == 200
    sent = json.dumps(app.state.scholar_speech.calls)
    assert saved.dialogue in sent and CHARACTERS["margot"]["private_brief"] not in sent
    assert "Private roster marker" not in sent and "introduction marker" not in sent


@pytest.mark.parametrize("property,value,expected", [("paused", True, 409), ("dialogue", "", 409), ("dialogue", "x" * 1501, 413)])
def test_pause_empty_and_text_bound_reject_without_generation(client, property, value, expected):
    created = room(client)
    setattr(rooms[created["room_id"]], property, value)
    assert client.post(endpoint(created), headers=auth(created["organizer_token"]), json={}).status_code == expected
    assert not app.state.scholar_speech.calls


@pytest.mark.parametrize("reason,status", [("unavailable", 503), ("busy", 429), ("timeout", 504), ("generation_failed", 503), ("invalid_output", 503)])
def test_worker_failure_is_safe_and_does_not_return_audio(client, monkeypatch, reason, status):
    created = room(client)
    monkeypatch.setattr(app.state, "scholar_speech", FakeScholar(reason=reason))
    response = client.post(endpoint(created), headers=auth(created["organizer_token"]), json={})
    assert response.status_code == status and "audio_base64" not in response.text
    assert created["organizer_token"] not in response.text


@pytest.mark.parametrize("change", ["revision", "pause", "dialogue"])
def test_room_controls_stay_unlocked_and_stale_clip_is_discarded(client, monkeypatch, change):
    created = room(client)
    saved = rooms[created["room_id"]]
    def mutate():
        assert not saved.lock.locked()
        if change == "revision": saved.revision += 1
        elif change == "pause": saved.paused = True
        else: saved.dialogue = "A different current line."
    monkeypatch.setattr(app.state, "scholar_speech", FakeScholar(change=mutate))
    response = client.post(endpoint(created), headers=auth(created["organizer_token"]), json={})
    assert response.status_code == 409 and "audio_base64" not in response.text


def test_response_allows_no_renderer_diagnostics_and_rejects_unapproved_pace(client, monkeypatch):
    created = room(client)
    monkeypatch.setattr(app.state, "scholar_speech", FakeScholar(extra={"debug_secret": "never expose"}))
    response = client.post(endpoint(created), headers=auth(created["organizer_token"]), json={})
    assert response.status_code == 200 and "debug_secret" not in response.json()
    monkeypatch.setattr(app.state, "scholar_speech", FakeScholar(extra={"playback_rate": 1.4}))
    assert client.post(endpoint(created), headers=auth(created["organizer_token"]), json={}).status_code == 503


def fake_renderer(tmp_path, **cache_options):
    executable = tmp_path / "python.exe"
    executable.write_bytes(b"test marker, never executed")
    instance = ScholarSpeechRenderer(base_dir=tmp_path / "generated", model_dir=tmp_path / "models", executable=executable, timeout=0.03, **cache_options)
    instance.available = True
    return instance


def write_result(directory, text):
    with wave.open(str(directory / "speech.wav"), "wb") as output:
        output.setnchannels(1); output.setsampwidth(2); output.setframerate(24000)
        output.writeframes(b"\0\0" * 24000)
    (directory / "speech.json").write_text(json.dumps({"text": text, "voice": "bm_lewis", "provider": "kokoro-onnx", "generation_speed": 0.92}), encoding="utf-8")


def test_missing_optional_runtime_is_unavailable_and_never_spawns(tmp_path, monkeypatch):
    async def forbidden(*args, **kwargs): raise AssertionError("Do not spawn")
    monkeypatch.setattr(asyncio, "create_subprocess_exec", forbidden)
    instance = ScholarSpeechRenderer(base_dir=tmp_path / "none", model_dir=tmp_path / "missing", executable=tmp_path / "missing-python")
    assert instance.available is False
    async def run():
        with pytest.raises(ScholarSpeechError, match="unavailable"):
            await instance.render("Current public text.")
    asyncio.run(run())


def test_worker_argv_is_fixed_literal_json_contains_only_public_text(tmp_path, monkeypatch):
    captured = {}
    text = "Current public text."
    async def create_process(*args, **kwargs):
        captured["args"], captured["kwargs"] = args, kwargs
        payload = Path(args[args.index("--input") + 1])
        data = json.loads(payload.read_text(encoding="utf-8"))
        assert data == {"text": text}
        write_result(Path(args[args.index("--output") + 1]), text)
        return FakeProcess()
    monkeypatch.setenv("OPENAI_API_KEY", "do-not-forward")
    monkeypatch.setenv("SOME_PROVIDER_TOKEN", "do-not-forward")
    monkeypatch.setattr(asyncio, "create_subprocess_exec", create_process)
    async def run():
        instance = fake_renderer(tmp_path)
        result = await instance.render(text)
        assert result["voice"] == "bm_lewis" and result["playback_rate"] == 1.05
        assert result["duration_ms"] == 1000
        assert not list(instance.base_dir.iterdir())
    asyncio.run(run())
    assert text not in captured["args"] and "shell" not in captured["kwargs"]
    assert Path(captured["args"][0]).is_absolute()
    assert "OPENAI_API_KEY" not in captured["kwargs"]["env"] and "SOME_PROVIDER_TOKEN" not in captured["kwargs"]["env"]
    assert "--download" not in captured["args"]


def test_timeout_kills_and_reaps_process_before_temp_cleanup(tmp_path, monkeypatch):
    holder = []
    async def create_process(*args, **kwargs):
        process = FakeProcess(held=True); holder.append(process); return process
    monkeypatch.setattr(asyncio, "create_subprocess_exec", create_process)
    async def run():
        instance = fake_renderer(tmp_path)
        with pytest.raises(ScholarSpeechError, match="timeout"):
            await instance.render("Public text.")
        assert holder[0].killed and holder[0].waited >= 2
        assert not instance._busy and not list(instance.base_dir.iterdir())
    asyncio.run(run())


def test_cancelled_request_kills_child_and_releases_renderer_slot(tmp_path, monkeypatch):
    holder = []
    async def create_process(*args, **kwargs):
        process = FakeProcess(held=True); holder.append(process); return process
    monkeypatch.setattr(asyncio, "create_subprocess_exec", create_process)
    async def run():
        instance = fake_renderer(tmp_path); instance.timeout = 10
        task = asyncio.create_task(instance.render("Public text."))
        await asyncio.sleep(0); task.cancel()
        with pytest.raises(asyncio.CancelledError): await task
        assert holder[0].killed and holder[0].waited >= 2
        assert not instance._busy and not list(instance.base_dir.iterdir())
    asyncio.run(run())


def test_one_job_limit_rejects_simultaneous_requests(tmp_path, monkeypatch):
    holder = []
    async def create_process(*args, **kwargs):
        payload = Path(args[args.index("--input") + 1])
        write_result(payload.parent, json.loads(payload.read_text())["text"])
        process = FakeProcess(held=True); holder.append(process); return process
    monkeypatch.setattr(asyncio, "create_subprocess_exec", create_process)
    async def run():
        instance = fake_renderer(tmp_path); instance.timeout = 10
        first = asyncio.create_task(instance.render("First public line."))
        await asyncio.sleep(0)
        with pytest.raises(ScholarSpeechError, match="busy"):
            await instance.render("Second line.")
        holder[0].event.set()
        assert (await first)["voice"] == "bm_lewis" and len(holder) == 1
    asyncio.run(run())


@pytest.mark.parametrize("field,value", [("voice", "bm_george"), ("generation_speed", 1.4), ("text", "Unapproved text")])
def test_generated_output_must_match_approved_voice_and_current_text(tmp_path, monkeypatch, field, value):
    async def create_process(*args, **kwargs):
        directory = Path(args[args.index("--output") + 1])
        write_result(directory, "Public text.")
        manifest = json.loads((directory / "speech.json").read_text())
        manifest[field] = value
        (directory / "speech.json").write_text(json.dumps(manifest))
        return FakeProcess()
    monkeypatch.setattr(asyncio, "create_subprocess_exec", create_process)
    async def run():
        with pytest.raises(ScholarSpeechError, match="invalid_output"):
            await fake_renderer(tmp_path).render("Public text.")
    asyncio.run(run())


def timing_value(end=0.5):
    return {'source':'kokoro-model-duration','clock':'audio-seconds','phonemes':[{'phoneme':'ə','start':0.1,'end':end}]}

def test_worker_sidecar_is_optional_bounded_and_validated(tmp_path):
    from backend.scholar_speech import _read_render
    write_result(tmp_path,'Public text.')
    assert 'phoneme_timing' not in _read_render(tmp_path,'Public text.')
    path=tmp_path/'speech-timing.json';path.write_text(json.dumps(timing_value()),encoding='utf-8')
    result=_read_render(tmp_path,'Public text.')
    assert result['phoneme_timing']==timing_value() and result['playback_rate']==1.05
    path.write_text(json.dumps(timing_value(1.01)),encoding='utf-8')
    with pytest.raises(ScholarSpeechError,match='invalid_output'):_read_render(tmp_path,'Public text.')
    path.write_bytes(b' '*(512*1024+1))
    with pytest.raises(ScholarSpeechError,match='invalid_output'):_read_render(tmp_path,'Public text.')
    path.write_text('{broken',encoding='utf-8')
    with pytest.raises(ScholarSpeechError,match='invalid_output'):_read_render(tmp_path,'Public text.')


def test_worker_sidecar_symlink_is_rejected(tmp_path):
    from backend.scholar_speech import _read_render
    write_result(tmp_path,'Public text.')
    outside=tmp_path/'other.json';outside.write_text(json.dumps(timing_value()),encoding='utf-8')
    try:(tmp_path/'speech-timing.json').symlink_to(outside)
    except OSError:pytest.skip('Local Windows symlink permission unavailable')
    with pytest.raises(ScholarSpeechError,match='invalid_output'):_read_render(tmp_path,'Public text.')


def test_endpoint_exposes_only_validated_optional_timing_for_current_public_text(client,monkeypatch):
    created=room(client)
    fake=FakeScholar(extra={'phoneme_timing':timing_value(),'private_extra':'never exposed'})
    monkeypatch.setattr(app.state,'scholar_speech',fake)
    response=client.post(endpoint(created),headers=auth(created['organizer_token']),json={})
    assert response.status_code==200
    assert response.json()['phoneme_timing']==timing_value()
    assert 'private_extra' not in response.json()
    assert response.headers['cache-control']=='no-store'


@pytest.mark.parametrize('value', [timing_value(1.01),{'source':'guessed','clock':'audio-seconds','phonemes':[]},None,{'source':'kokoro-model-duration','clock':'audio-seconds','phonemes':[{'phoneme':'\ud800','start':0,'end':.1}]}])
def test_endpoint_revalidates_timing_from_injected_renderer(client,monkeypatch,value):
    created=room(client)
    monkeypatch.setattr(app.state,'scholar_speech',FakeScholar(extra={'phoneme_timing':value}))
    response=client.post(endpoint(created),headers=auth(created['organizer_token']),json={})
    assert response.status_code==503 and 'phoneme_timing' not in response.json()


def test_endpoint_recovers_exact_source_sample_clock_from_rounded_milliseconds(client,monkeypatch):
    created=room(client);duration=24001/24000
    cue={'source':'kokoro-model-duration','clock':'audio-seconds','phonemes':[{'phoneme':'ə','start':0.1,'end':duration}]}
    monkeypatch.setattr(app.state,'scholar_speech',FakeScholar(extra={'duration_ms':round(duration*1000,2),'phoneme_timing':cue}))
    response=client.post(endpoint(created),headers=auth(created['organizer_token']),json={})
    assert response.status_code==200 and response.json()['phoneme_timing']==cue


def install_cache_worker(monkeypatch, calls, *, hold_after=None, invalid_first=False):
    async def create_process(*args,**kwargs):
        directory=Path(args[args.index('--output')+1])
        payload=json.loads((directory/'input.json').read_text(encoding='utf-8'))
        calls.append(payload['text'])
        write_result(directory,payload['text'])
        (directory/'speech-timing.json').write_text(json.dumps(timing_value()),encoding='utf-8')
        if invalid_first and len(calls)==1:
            (directory/'speech.json').write_text('{}',encoding='utf-8')
        process=FakeProcess(held=hold_after is not None and len(calls)>hold_after)
        holders=getattr(create_process,'holders',[]);holders.append(process);create_process.holders=holders
        return process
    monkeypatch.setattr(asyncio,'create_subprocess_exec',create_process)
    return create_process


def test_repeat_validated_clip_and_its_timing_are_reused_without_spawning(tmp_path,monkeypatch):
    calls=[];install_cache_worker(monkeypatch,calls)
    async def run():
        instance=fake_renderer(tmp_path)
        first=await instance.render('Current public line.')
        expected_audio=first['audio_base64'];first['phoneme_timing']['phonemes'][0]['end']=999
        second=await instance.render('Current public line.')
        assert second['audio_base64']==expected_audio and second['phoneme_timing']==timing_value()
        assert len(calls)==1 and not list(instance.base_dir.iterdir())
        second['text']='Caller mutation'
        assert (await instance.render('Current public line.'))['text']=='Current public line.'
        instance.available=False
        with pytest.raises(ScholarSpeechError,match='unavailable'):await instance.render('Current public line.')
    asyncio.run(run())


def test_warm_hit_can_serve_while_another_cold_clip_is_busy(tmp_path,monkeypatch):
    calls=[];worker=install_cache_worker(monkeypatch,calls,hold_after=1)
    async def run():
        instance=fake_renderer(tmp_path);instance.timeout=10
        warm=await instance.render('Warm public line.')
        cold=asyncio.create_task(instance.render('Cold public line.'));await asyncio.sleep(0)
        assert instance._busy
        assert (await instance.render('Warm public line.'))==warm
        with pytest.raises(ScholarSpeechError,match='busy'):await instance.render('Third public line.')
        assert len(calls)==2
        worker.holders[-1].event.set();await cold
    asyncio.run(run())


def test_expired_and_oversized_clips_recompute_and_failed_output_is_not_cached(tmp_path,monkeypatch):
    calls=[];install_cache_worker(monkeypatch,calls,invalid_first=True)
    async def run():
        now=[0.0];instance=fake_renderer(tmp_path,cache_ttl=5,clock=lambda:now[0])
        with pytest.raises(ScholarSpeechError,match='invalid_output'):await instance.render('Public line.')
        good=await instance.render('Public line.')
        assert (await instance.render('Public line.'))==good and len(calls)==2
        now[0]=5
        await instance.render('Public line.');assert len(calls)==3
        instance=fake_renderer(tmp_path,cache_max_bytes=1)
        await instance.render('Public line.');await instance.render('Public line.')
        assert len(calls)==5
    asyncio.run(run())


def test_warm_response_retains_authorization_pause_current_revision_and_stale_guards(client,tmp_path,monkeypatch):
    calls=[];install_cache_worker(monkeypatch,calls)
    created=room(client);saved=rooms[created['room_id']];saved.dialogue='Public warm line.'
    instance=fake_renderer(tmp_path);monkeypatch.setattr(app.state,'scholar_speech',instance)
    assert client.post(endpoint(created),headers=auth(created['organizer_token']),json={}).status_code==200
    assert len(calls)==1
    assert client.post(endpoint(created),headers=auth('wrong'),json={}).status_code==403
    saved.paused=True
    assert client.post(endpoint(created),headers=auth(created['organizer_token']),json={}).status_code==409
    saved.paused=False;saved.revision+=1
    response=client.post(endpoint(created),headers=auth(created['organizer_token']),json={})
    assert response.status_code==200 and response.json()['revision']==saved.revision and len(calls)==1
    assert response.headers['cache-control']=='no-store'
    original=instance.render
    async def stale(text):
        result=await original(text);saved.revision+=1;return result
    monkeypatch.setattr(instance,'render',stale)
    assert client.post(endpoint(created),headers=auth(created['organizer_token']),json={}).status_code==409
    assert len(calls)==1


def test_optional_cache_failure_does_not_replace_valid_speech_with_an_error(tmp_path,monkeypatch):
    calls=[];install_cache_worker(monkeypatch,calls)
    async def run():
        instance=fake_renderer(tmp_path)
        def cannot_read(key):raise RuntimeError('Simulated cache failure')
        def cannot_store(key,value):raise MemoryError('Simulated storage failure')
        monkeypatch.setattr(instance._cache,'get',cannot_read)
        monkeypatch.setattr(instance._cache,'put',cannot_store)
        result=await instance.render('Public valid line.')
        assert result['voice']=='bm_lewis' and result['phoneme_timing']==timing_value() and len(calls)==1
        assert not instance._busy and not list(instance.base_dir.iterdir())
    asyncio.run(run())


def test_timeout_and_cancellation_never_leave_a_reusable_clip(tmp_path,monkeypatch):
    calls=[];holders=[]
    async def process(*args,**kwargs):
        directory=Path(args[args.index('--output')+1]);text=json.loads((directory/'input.json').read_text())['text']
        calls.append(text);write_result(directory,text)
        child=FakeProcess(held=len(calls) in (1,3));holders.append(child);return child
    monkeypatch.setattr(asyncio,'create_subprocess_exec',process)
    async def run():
        instance=fake_renderer(tmp_path)
        with pytest.raises(ScholarSpeechError,match='timeout'):await instance.render('Retry timeout line.')
        assert instance._cache.info()['entries']==0 and holders[0].killed
        await instance.render('Retry timeout line.');assert len(calls)==2
        instance.timeout=10
        task=asyncio.create_task(instance.render('Retry cancelled line.'));await asyncio.sleep(0);task.cancel()
        with pytest.raises(asyncio.CancelledError):await task
        assert holders[-1].killed
        await instance.render('Retry cancelled line.');assert len(calls)==4
    asyncio.run(run())
