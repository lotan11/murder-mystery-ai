"""Offline regression probes for listener fixes on feature/listener.
Run explicitly from the listener branch; the fixture creates a temporary room DB.
Not collected by the main-branch suite, which has no listener module; see docs/LISTENER_REVIEW.md.
"""
import asyncio, struct, threading
from dataclasses import replace
import pytest
import importlib.util
if importlib.util.find_spec("backend.listener") is None:
    pytest.skip("Run explicitly from an isolated listener branch snapshot; see docs/LISTENER_REVIEW.md", allow_module_level=True)
from fastapi.testclient import TestClient
from backend.main import app, rooms
from backend.listener import empty_memory, accept_utterance, _claims

@pytest.fixture
def client(tmp_path,monkeypatch):
    monkeypatch.setenv('MYSTERY_DB_PATH',str(tmp_path/'review.sqlite3'))
    monkeypatch.setenv('MYSTERY_TRANSCRIPTION_ENABLED','false')
    rooms.clear()
    with TestClient(app) as c:yield c

def join(ws):
    ws.receive_json();ws.send_json({'type':'join','name':'Review Guest'})
    assert ws.receive_json()['type']=='joined'
    ws.receive_json();ws.receive_json()
    ws.send_json({'type':'listener.start','consent':True})
    assert ws.receive_json()['type']=='listener.status'

def webm_clip(seconds=3):
    payload=bytes.fromhex('448988')+struct.pack('>d',seconds*1000)
    info=bytes.fromhex('1549a966')+bytes([0x80|len(payload)])+payload
    return bytes.fromhex('1a45dfa38018538067')+bytes([0x80|len(info)])+info

@pytest.mark.parametrize('interruption',['stop','reset'])
def test_delayed_audio_does_not_publish_after_interruption(client,interruption):
    created=client.post('/api/rooms').json();room_id=created['room_id'];room=rooms[room_id]
    room.act=1;app.state.room_store.save(room.record())
    started=threading.Event();release=threading.Event()
    class Delayed:
        async def transcribe(self,*args):
            started.set()
            while not release.is_set():await asyncio.sleep(.01)
            return 'Stale audio from the previous listening session.'
    app.state.transcriber=Delayed()
    app.state.transcription_config=replace(app.state.transcription_config,enabled=True,reason='ready')
    with client.websocket_connect(f"/ws/{room_id}?role=organizer&token={created['organizer_token']}") as host:
      host.receive_json()
      with client.websocket_connect(f'/ws/{room_id}?role=guest') as guest:
        join(guest)
        guest.send_json({'type':'listener.audio','duration_seconds':3,'mime_type':'audio/webm'})
        assert guest.receive_json()['type']=='listener.status'
        guest.send_bytes(webm_clip())
        assert started.wait(3)
        if interruption=='stop':guest.send_json({'type':'listener.stop'})
        else:
            host.send_json({'type':'control','action':'reset'})
            while True:
                packet=host.receive_json()
                if packet.get('type')=='state' and packet['data']['act']==0:break
        release.set()
        if interruption=='reset':guest.send_json({'type':'listener.stop'})
        # Wait for the delayed transcript path to complete, not a racing HTTP read.
        while True:
            packet=guest.receive_json()
            if packet.get('type')=='listener.status' and not packet['listening']:break
        assert room.listener['utterances']==[], 'Delayed audio was published after '+interruption

def test_claims_do_not_cross_assign_subjects_places_and_times():
    claims=_claims('Ada was in the library at 9:20; Felix was in the music room at 9:40.')
    assert claims==[{'subject':'ada','place':'library','time':'9:20 PM'}, {'subject':'felix','place':'music_room','time':'9:40 PM'}]

def test_theory_links_remain_bounded_with_transcript_retention():
    memory=empty_memory()
    for i in range(200):accept_utterance(memory,guest_id='g1',guest_name='Guest',text='I suspect Ada because of the clock.',evidence=[])
    assert len(memory['utterances'])==120
    assert len(memory['theories']['ada']['supporting'])<=120


def test_schema_three_migration_preserves_game_record(client):
    from backend.main import Room
    created=client.post('/api/rooms').json();room=rooms[created['room_id']]
    with client.websocket_connect(f"/ws/{room.room_id}?role=guest") as guest:join(guest)
    legacy=room.record();legacy.pop('listener');legacy['schema_version']=3
    app.state.room_store.save(legacy)
    loaded=app.state.room_store.load_all()[0]
    migrated=Room.from_record(loaded).record()
    assert migrated['schema_version']==4 and migrated['listener']==empty_memory()
    assert {key:value for key,value in migrated.items() if key not in ('schema_version','listener')}=={key:value for key,value in legacy.items() if key!='schema_version'}
    app.state.room_store.save_many([migrated])
    assert Room.from_record(app.state.room_store.load_all()[0]).record()==migrated
