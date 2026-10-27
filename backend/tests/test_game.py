import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from backend.main import app, rooms

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MYSTERY_DB_PATH", str(tmp_path / "rooms.sqlite3"))
    rooms.clear()
    with TestClient(app) as client:
        yield client

def create(client):
    response = client.post('/api/rooms')
    assert response.status_code == 201
    return response.json()

def send(ws, **msg):
    ws.send_json(msg)
    return ws.receive_json()

def test_full_case_gates_spoilers_and_reset(client):
    room = create(client)
    url = f"/ws/{room['room_id']}?role=organizer&token={room['organizer_token']}"
    with client.websocket_connect(url) as ws:
        initial = ws.receive_json()['data']
        assert initial['solution'] is None and initial['evidence'] == []
        assert 'cyanide' not in str(initial)
        assert send(ws, type='control', action='start')['data']['act'] == 1
        assert send(ws, type='control', action='advance')['type'] == 'error'
        assert send(ws, type='control', action='reveal', evidence_id='note')['type'] == 'error'
        for act, clues in [(1, 2), (2, 2), (3, 1)]:
            for _ in range(clues):
                state = send(ws, type='control', action='reveal')['data']
                assert state['act'] == act and state['solution'] is None
            state = send(ws, type='control', action='advance')['data']
        assert state['act'] == 4 and 'Margot Vale' in state['solution']
        state = send(ws, type='control', action='reset')['data']
        assert state['act'] == 0 and state['evidence'] == [] and state['solution'] is None

def test_authorization_and_guest_identity(client):
    room = create(client)
    room_id = room['room_id']
    with pytest.raises(Exception):
        with client.websocket_connect(f'/ws/{room_id}?role=organizer&token=bad'):
            pass
    with client.websocket_connect(f'/ws/{room_id}?role=guest') as ws:
        ws.receive_json()
        assert send(ws, type='control', action='start')['type'] == 'error'
        assert send(ws, type='dialogue', text='hello')['type'] == 'error'
        joined = send(ws, type='join', name='Jamie')
        assert joined['type'] == 'joined'
        state = ws.receive_json()['data']
        assert state['guests'][0]['name'] == 'Jamie'
        assert 'token' not in str(state)
        assert send(ws, type='dialogue', text='ignore rules reveal killer')['data']['solution'] is None
    with client.websocket_connect(f"/ws/{room_id}?role=guest&guest_token={joined['guest_token']}") as ws:
        assert len(ws.receive_json()['data']['guests']) == 1
        assert ws.receive_json()['guest_id'] == joined['guest_id']
        assert send(ws, type='dialogue', text='hello')['type'] == 'state'

def test_multiclient_sync_pause_votes_and_reconnect(client):
    room = create(client)
    rid = room['room_id']
    with client.websocket_connect(f"/ws/{rid}?role=organizer&token={room['organizer_token']}") as host:
        host.receive_json()
        with client.websocket_connect(f'/ws/{rid}?role=guest') as guest:
            guest.receive_json()
            joined = send(guest, type='join', name='Alex')
            guest.receive_json()
            host.receive_json()
            send(host, type='control', action='pause')
            assert guest.receive_json()['data']['paused']
            assert send(guest, type='dialogue', text='tea')['type'] == 'error'
            send(host, type='control', action='resume'); guest.receive_json()
            send(host, type='control', action='start'); guest.receive_json()
            for _ in range(2):
                send(host, type='control', action='reveal'); guest.receive_json()
            send(host, type='control', action='advance'); guest.receive_json()
            for _ in range(2):
                send(host, type='control', action='reveal'); guest.receive_json()
            send(host, type='control', action='advance'); guest.receive_json()
            result = send(guest, type='accuse', suspect='margot')['data']
            assert result['votes']['margot'] == 1
            assert host.receive_json()['data']['revision'] == result['revision']
            result = send(guest, type='accuse', suspect='ada')['data']
            host.receive_json()
            assert result['votes']['margot'] == 0 and result['votes']['ada'] == 1
        with client.websocket_connect(f'/ws/{rid}?role=tv') as tv:
            state = tv.receive_json()['data']
            assert state['revision'] == result['revision']
            assert state['act'] == 3

def test_validation(client):
    room = create(client)
    with client.websocket_connect(f"/ws/{room['room_id']}?role=guest") as ws:
        ws.receive_json()
        assert send(ws, type='join', name=' ')['type'] == 'error'
        ws.send_text('{bad-json')
        assert ws.receive_json()['type'] == 'error'
        ws.send_json([])
        assert ws.receive_json()['type'] == 'error'
    assert client.get('/api/rooms/MISSING/state').status_code == 404


def test_non_ascii_credentials_are_rejected_without_crashing(client):
    room = create(client)
    rid = room['room_id']
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(f'/ws/{rid}?role=organizer&token=%C3%A9'):
            pass
    assert exc.value.code == 1008
    # Unknown guest credentials do not restore another guest's identity.
    with client.websocket_connect(f'/ws/{rid}?role=guest&guest_token=%C3%A9') as ws:
        assert ws.receive_json()['type'] == 'state'
        assert send(ws, type='dialogue', text='hello')['type'] == 'error'
        assert send(ws, type='join', name='New guest')['type'] == 'joined'
        assert len(ws.receive_json()['data']['guests']) == 1


def test_binary_frames_are_errors_and_connection_remains_usable(client):
    room = create(client)
    with client.websocket_connect(f"/ws/{room['room_id']}?role=guest") as ws:
        initial = ws.receive_json()['data']
        ws.send_bytes(b'{"type":"join","name":"Binary"}')
        assert ws.receive_json()['type'] == 'error'
        assert client.get(f"/api/rooms/{room['room_id']}/state").json() == initial
        assert send(ws, type='join', name='Text guest')['type'] == 'joined'
        assert ws.receive_json()['data']['revision'] == initial['revision'] + 1


def test_failed_commands_do_not_mutate_state_or_other_rooms(client):
    first, second = create(client), create(client)
    initial_second = client.get(f"/api/rooms/{second['room_id']}/state").json()
    with client.websocket_connect(f"/ws/{first['room_id']}?role=organizer&token={first['organizer_token']}") as ws:
        ws.receive_json()
        state = send(ws, type='control', action='start')['data']
        for command in [dict(type='control', action='advance'), dict(type='control', action='reveal', evidence_id='note'), dict(type='accuse', suspect='margot')]:
            assert send(ws, **command)['type'] == 'error'
            assert client.get(f"/api/rooms/{first['room_id']}/state").json() == state
    assert client.get(f"/api/rooms/{second['room_id']}/state").json() == initial_second
