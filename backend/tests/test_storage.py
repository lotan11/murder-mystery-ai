import json
from contextlib import closing
import sqlite3

def receive(ws):
    """Legacy state tests ignore additive identity-only character updates."""
    while True:
        packet = ws.receive_json()
        if packet["type"] != "private":
            return packet


import pytest
from fastapi.testclient import TestClient

from backend.main import app, rooms, Room
from backend.mystery import EVIDENCE
from backend.storage import RoomStore, StorageError


def test_sqlite_commit_can_be_loaded_by_independent_store(tmp_path):
    path = tmp_path / "nested" / "rooms.sqlite3"
    store = RoomStore(path)
    record = {"schema_version": 1, "room_id": "ABC123", "dialogue": "A guest’s theory"}
    store.save(record)
    record["dialogue"] = "Committed replacement"
    store.save(record)
    assert RoomStore(path).load_all() == [record]
    # SQL values are parameterized: dialogue punctuation is ordinary data.
    record["dialogue"] = "'); DROP TABLE rooms; --"
    store.save(record)
    assert RoomStore(path).load_all() == [record]


def test_restart_restores_progress_votes_and_credentials(tmp_path, monkeypatch):
    path = tmp_path / "rooms.sqlite3"
    monkeypatch.setenv("MYSTERY_DB_PATH", str(path))
    with TestClient(app) as client:
        room = client.post("/api/rooms").json()
        rid = room["room_id"]
        with client.websocket_connect(f"/ws/{rid}?role=organizer&token={room['organizer_token']}") as host:
            receive(host)
            host.send_json({"type": "control", "action": "start"})
            receive(host)
            for act in (1, 2):
                for _ in range(2):
                    host.send_json({"type": "control", "action": "reveal"})
                    receive(host)
                host.send_json({"type": "control", "action": "advance"})
                assert receive(host)["data"]["act"] == act + 1
        with client.websocket_connect(f"/ws/{rid}?role=guest") as guest:
            receive(guest)
            guest.send_json({"type": "join", "name": "Returning sleuth"})
            identity = receive(guest)
            receive(guest)
            guest.send_json({"type": "accuse", "suspect": "margot"})
            expected = receive(guest)["data"]
        with client.websocket_connect(f"/ws/{rid}?role=organizer&token={room['organizer_token']}") as host:
            receive(host)
            host.send_json({"type": "control", "action": "pause"})
            expected = receive(host)["data"]
        assert expected["solution"] is None
        assert len(expected["evidence"]) == 4
    # Discard all live state. A new application lifespan must recover from SQLite only.
    rooms.clear()
    with TestClient(app) as restarted:
        assert restarted.get("/health").json()["storage"] == "sqlite"
        assert restarted.get(f"/api/rooms/{rid}/state").json() == expected
        with restarted.websocket_connect(f"/ws/{rid}?role=guest&guest_token={identity['guest_token']}") as guest:
            assert receive(guest)["data"] == expected
            assert receive(guest)["guest_id"] == identity["guest_id"]
        with restarted.websocket_connect(f"/ws/{rid}?role=organizer&token={room['organizer_token']}") as host:
            receive(host)
            host.send_json({"type": "control", "action": "resume"})
            resumed = receive(host)["data"]
            assert resumed["revision"] == expected["revision"] + 1
            assert not resumed["paused"]
        public = json.dumps(resumed)
        assert room["organizer_token"] not in public
        assert identity["guest_token"] not in public
        for clue in EVIDENCE:
            if clue["id"] not in {item["id"] for item in resumed["evidence"]}:
                assert clue["description"] not in public
    persisted = RoomStore(path).load_all()[0]
    assert "clients" not in persisted and "lock" not in persisted
    assert "solution" not in persisted and "evidence" not in persisted


def test_failed_write_rolls_back_state_and_guest_identity(tmp_path, monkeypatch):
    monkeypatch.setenv("MYSTERY_DB_PATH", str(tmp_path / "rooms.sqlite3"))
    with TestClient(app) as client:
        room = client.post("/api/rooms").json()
        rid = room["room_id"]
        initial = client.get(f"/api/rooms/{rid}/state").json()
        save = app.state.room_store.save
        def fail(_record):
            raise StorageError("disk full")
        monkeypatch.setattr(app.state.room_store, "save", fail)
        with client.websocket_connect(f"/ws/{rid}?role=guest") as guest:
            receive(guest)
            guest.send_json({"type": "join", "name": "Not yet committed"})
            assert receive(guest)["type"] == "error"
            assert client.get(f"/api/rooms/{rid}/state").json() == initial
            monkeypatch.setattr(app.state.room_store, "save", save)
            guest.send_json({"type": "dialogue", "text": "Am I joined?"})
            assert receive(guest)["type"] == "error"
            guest.send_json({"type": "join", "name": "Committed guest"})
            assert receive(guest)["type"] == "joined"
            committed = receive(guest)["data"]
            assert len(committed["guests"]) == 1
        monkeypatch.setattr(app.state.room_store, "save", fail)
        with client.websocket_connect(f"/ws/{rid}?role=organizer&token={room['organizer_token']}") as host:
            receive(host)
            host.send_json({"type": "control", "action": "start"})
            assert receive(host)["type"] == "error"
        assert client.get(f"/api/rooms/{rid}/state").json() == committed
        assert app.state.room_store.load_all()[0]["revision"] == committed["revision"]
        assert client.post("/api/rooms").status_code == 503
        assert len(rooms) == 1


def test_corrupt_storage_fails_without_discarding_saved_data(tmp_path):
    path = tmp_path / "rooms.sqlite3"
    RoomStore(path)
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("INSERT INTO rooms VALUES (?, ?)", ("ABC123", "not-json"))
    with pytest.raises(StorageError, match="preserve the database"):
        RoomStore(path).load_all()
    with closing(sqlite3.connect(path)) as connection, connection:
        assert connection.execute("SELECT payload FROM rooms").fetchone()[0] == "not-json"


@pytest.mark.parametrize("change", [
    {"act": 5},
    {"act": True},
    {"paused": "yes"},
    {"revision": -1},
    {"guests": {"guest": {"name": "Ada", "token": 42}}},
    {"revealed": ["missing-clue"]},
    {"revealed": ["glass", "glass"]},
    {"votes": {"unknown-guest": "margot"}},
    {"guests": {"guest": {"name": "Ada", "token": "secret"}}, "votes": {"guest": "unknown-suspect"}},
    {"clients": []},
])
def test_invalid_saved_room_fails_startup_without_overwriting_database(tmp_path, monkeypatch, change):
    path = tmp_path / "invalid.sqlite3"
    monkeypatch.setenv("MYSTERY_DB_PATH", str(path))
    record = Room("ABC123", "organizer-secret").record()
    record.update(change)
    store = RoomStore(path)
    store.save(record)
    with pytest.raises(StorageError, match="Invalid saved room"):
        with TestClient(app):
            pass
    assert store.load_all() == [record]


@pytest.mark.parametrize("pin", ["case_id", "case_version"])
def test_incompatible_case_is_rejected_with_recovery_message(tmp_path, monkeypatch, pin):
    path = tmp_path / "incompatible.sqlite3"
    monkeypatch.setenv("MYSTERY_DB_PATH", str(path))
    record = Room("ABC123", "organizer-secret").record()
    record[pin] = "another-case" if pin == "case_id" else record[pin] + 1
    store = RoomStore(path)
    store.save(record)
    with pytest.raises(StorageError, match="incompatible case version"):
        with TestClient(app):
            pass
    assert RoomStore(path).load_all() == [record]
