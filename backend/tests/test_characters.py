"""Private player projection, delivery, lifecycle and compatible room migrations."""
import copy
import json
from contextlib import ExitStack

import pytest
from fastapi.testclient import TestClient

from backend.characters import CHARACTERS
from backend.main import Room, app, rooms
from backend.storage import RoomStore, StorageError


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("MYSTERY_DB_PATH", str(tmp_path / "characters.sqlite3"))
    rooms.clear()
    with TestClient(app) as active:
        yield active


def create(client):
    return client.post("/api/rooms").json()


def guest_url(room, token=""):
    return f"/ws/{room['room_id']}?role=guest&guest_token={token}"


def host_url(room):
    return f"/ws/{room['room_id']}?role=organizer&token={room['organizer_token']}"


def join(ws, name):
    assert ws.receive_json()["type"] == "state"
    ws.send_json({"type": "join", "name": name})
    identity = ws.receive_json()
    assert identity["type"] == "joined"
    state = ws.receive_json()
    private = ws.receive_json()
    assert state["type"] == "state" and private["type"] == "private"
    assert private["data"]["guest_id"] == identity["guest_id"]
    return identity, state["data"], private["data"]


def restore(ws, identity):
    assert ws.receive_json()["type"] == "state"
    assert ws.receive_json()["guest_id"] == identity["guest_id"]
    private = ws.receive_json()
    assert private["type"] == "private"
    return private["data"]


def host_action(host, action, guests=(), tv=None, **extra):
    host.send_json({"type": "control", "action": action, **extra})
    state = host.receive_json()
    assert state["type"] == "state", state
    for guest, identity in guests:
        assert guest.receive_json() == state
        packet = guest.receive_json()
        assert packet["type"] == "private" and packet["data"]["guest_id"] == identity["guest_id"]
        public_guest = next(item for item in state["data"]["guests"] if item["id"] == identity["guest_id"])
        assert packet["data"]["character"] == CHARACTERS[public_guest["character_id"]]
    if tv is not None:
        assert tv.receive_json() == state
    return state["data"]


def test_first_three_characters_are_exclusive_then_investigators(client):
    room = create(client)
    collected = []
    for name in ("One", "Two", "Three", "Four", "Five"):
        with client.websocket_connect(guest_url(room)) as guest:
            _, state, private = join(guest, name)
            collected.append(private["character"]["id"])
            assert private["character"] == CHARACTERS[collected[-1]]
            for other_id, other in CHARACTERS.items():
                if other_id != collected[-1]:
                    assert other["private_brief"] not in json.dumps(private)
    assert collected == ["ada", "felix", "margot", "investigator", "investigator"]
    public = json.dumps(client.get(f"/api/rooms/{room['room_id']}/state").json())
    for character in CHARACTERS.values():
        assert character["private_brief"] not in public
        for objective in character["objectives"]:
            assert objective not in public
    assert "private_brief" not in public and "guest_token" not in public
    assert state["introductions"] == [] and state["accusations"] == []


def test_private_delivery_identity_and_host_assignment_boundaries(client):
    room = create(client)
    identities = []
    for name in ("Alice", "Bob"):
        with client.websocket_connect(guest_url(room)) as guest:
            identities.append(join(guest, name)[0])
    with ExitStack() as stack:
        host = stack.enter_context(client.websocket_connect(host_url(room)))
        tv = stack.enter_context(client.websocket_connect(f"/ws/{room['room_id']}?role=tv&guest_token={identities[0]['guest_token']}"))
        assert host.receive_json()["type"] == tv.receive_json()["type"] == "state"
        guests = []
        for identity in identities:
            guest = stack.enter_context(client.websocket_connect(guest_url(room, identity["guest_token"])))
            private = restore(guest, identity)
            guests.append((guest, identity))
            assert private["character"]["id"] == ("ada" if identity == identities[0] else "felix")
        first, second = guests[0][0], guests[1][0]
        first.send_json({"type": "introduce", "guest_id": identities[1]["guest_id"], "text": "Forged"})
        assert first.receive_json()["type"] == "error"
        first.send_json({"type": "control", "action": "assign", "guest_id": identities[1]["guest_id"], "character_id": "margot"})
        assert first.receive_json()["type"] == "error"
        host.send_json({"type": "control", "action": "assign", "guest_id": identities[1]["guest_id"], "character_id": "ada"})
        assert host.receive_json()["type"] == "error"
        state = host_action(host, "assign", guests, tv, guest_id=identities[1]["guest_id"], character_id="margot")
        assert state["guests"][1]["character_id"] == "margot"
        assert "private_brief" not in json.dumps(state)
        host_action(host, "pause", guests, tv)
        host.send_json({"type": "control", "action": "assign", "guest_id": identities[0]["guest_id"], "character_id": "investigator"})
        assert host.receive_json()["type"] == "error"
        host_action(host, "resume", guests, tv)
        host_action(host, "start", guests, tv)
        host.send_json({"type": "control", "action": "assign", "guest_id": identities[0]["guest_id"], "character_id": "investigator"})
        assert host.receive_json()["type"] == "error"
        assert client.get(f"/api/rooms/{room['room_id']}/state").json()["introductions"] == []


def test_introduction_is_deliberate_public_text_and_pause_gated(client):
    room = create(client)
    with client.websocket_connect(guest_url(room)) as guest:
        identity, _, _ = join(guest, "Introducer")
        for text in ("", " " * 4, "x" * 241, {"text": "bad"}):
            guest.send_json({"type": "introduce", "text": text})
            assert guest.receive_json()["type"] == "error"
        guest.send_json({"type": "introduce", "text": "I am Ada. I want a fair hearing."})
        state = guest.receive_json()["data"]
        private = guest.receive_json()["data"]
        assert private["introduction_submitted"] is True
        assert state["introductions"][0]["text"] == "I am Ada. I want a fair hearing."
        assert state["guests"][0]["introduced"] is True
        assert private["character"]["private_brief"] not in json.dumps(state)
    with client.websocket_connect(host_url(room)) as host:
        host.receive_json()
        host_action(host, "pause")
    with client.websocket_connect(guest_url(room, identity["guest_token"])) as guest:
        restore(guest, identity)
        guest.send_json({"type": "introduce", "text": "Replacement"})
        assert guest.receive_json()["type"] == "error"


def test_accusation_reason_private_until_resolution_and_reset_clears_participation(client):
    room = create(client)
    with client.websocket_connect(guest_url(room)) as guest:
        identity, _, initial_private = join(guest, "Reasoned guest")
    with client.websocket_connect(guest_url(room)) as other:
        other_identity, _, _ = join(other, "Other guest")
    with client.websocket_connect(host_url(room)) as host:
        host.receive_json()
        host_action(host, "start")
        for _ in (1, 2):
            host_action(host, "reveal"); host_action(host, "reveal"); host_action(host, "advance")
    with client.websocket_connect(guest_url(room, identity["guest_token"])) as guest:
        restore(guest, identity)
        guest.send_json({"type": "accuse", "suspect": "margot", "rationale": "Private rationale marker: access plus delivery."})
        public = guest.receive_json()["data"]
        private = guest.receive_json()["data"]
        assert public["accusations"] == []
        assert "Private rationale marker" not in json.dumps(public)
        assert private["own_vote"] == {"suspect": "margot", "rationale": "Private rationale marker: access plus delivery."}
        for rationale in ("x" * 301, {"spoof": "reason"}):
            guest.send_json({"type": "accuse", "suspect": "ada", "rationale": rationale})
            assert guest.receive_json()["type"] == "error"
        assert client.get(f"/api/rooms/{room['room_id']}/state").json() == public
    with client.websocket_connect(guest_url(room, other_identity["guest_token"])) as other:
        other_private = restore(other, other_identity)
        assert other_private["own_vote"] is None
        assert "Private rationale marker" not in json.dumps(other_private)
    with client.websocket_connect(host_url(room)) as host:
        host.receive_json()
        host_action(host, "reveal")
        final = host_action(host, "advance")
        assert final["accusations"][0]["rationale"].startswith("Private rationale marker")
        reset = host_action(host, "reset")
        assert reset["introductions"] == [] and reset["accusations"] == []
        assert reset["guests"][0]["character_id"] == initial_private["character"]["id"]
    with client.websocket_connect(guest_url(room, identity["guest_token"])) as guest:
        private = restore(guest, identity)
        assert private["own_vote"] is None and not private["introduction_submitted"]


def test_legacy_schema_migration_preserves_m1_room_and_commits_current_schema(tmp_path, monkeypatch):
    path = tmp_path / "legacy.sqlite3"
    monkeypatch.setenv("MYSTERY_DB_PATH", str(path))
    legacy = Room("ABC123", "old-host", act=3, paused=True, revision=42,
                  guests={"g1": {"name": "First", "token": "old-guest"}, "g2": {"name": "Second", "token": "second-token"}},
                  votes={"g1": "margot"}, revealed=["glass", "clock", "ledger", "alibi"]).record()
    legacy["schema_version"] = 1
    legacy.pop("listener")
    for field in ("assignments", "introductions", "rationales", "ai_calls", "dialogue_source", "dialogue_reason"):
        legacy.pop(field)
    RoomStore(path).save(legacy)
    with TestClient(app) as client:
        public = client.get("/api/rooms/ABC123/state").json()
        assert public["act"] == 3 and public["paused"] and public["revision"] == 42
        assert public["votes"]["margot"] == 1 and len(public["evidence"]) == 4
        assert [guest["character_id"] for guest in public["guests"]] == ["ada", "felix"]
        room = {"room_id": "ABC123", "organizer_token": "old-host"}
        identity = {"guest_id": "g1", "guest_token": "old-guest"}
        with client.websocket_connect(guest_url(room, "old-guest")) as guest:
            private = restore(guest, identity)
            assert private["character"]["id"] == "ada"
            assert private["own_vote"] == {"suspect": "margot", "rationale": ""}
    stored = RoomStore(path).load_all()[0]
    assert stored["schema_version"] == 4 and stored["revision"] == 42
    with TestClient(app) as client:
        assert client.get("/api/rooms/ABC123/state").json() == public


def test_private_mutation_rolls_back_when_storage_fails(client, monkeypatch):
    room = create(client)
    with client.websocket_connect(guest_url(room)) as guest:
        identity, public, private = join(guest, "Durable character")
        def fail(_):
            raise StorageError("disk full")
        monkeypatch.setattr(app.state.room_store, "save", fail)
        guest.send_json({"type": "introduce", "text": "Not committed"})
        assert guest.receive_json()["type"] == "error"
        assert client.get(f"/api/rooms/{room['room_id']}/state").json() == public
        assert rooms[room["room_id"]].private_snapshot(identity["guest_id"]) == private
    with client.websocket_connect(host_url(room)) as host:
        host.receive_json()
        host.send_json({"type": "control", "action": "assign", "guest_id": identity["guest_id"], "character_id": "margot"})
        assert host.receive_json()["type"] == "error"
        assert rooms[room["room_id"]].private_snapshot(identity["guest_id"]) == private


def test_restart_restores_private_card_intro_and_rationale(tmp_path, monkeypatch):
    path = tmp_path / "restart.sqlite3"
    monkeypatch.setenv("MYSTERY_DB_PATH", str(path))
    with TestClient(app) as client:
        room = create(client)
        with client.websocket_connect(guest_url(room)) as guest:
            identity, _, _ = join(guest, "Returning character")
            guest.send_json({"type": "introduce", "text": "A deliberate public greeting."})
            guest.receive_json(); guest.receive_json()
        with client.websocket_connect(host_url(room)) as host:
            host.receive_json()
            host_action(host, "start")
            for _ in (1, 2):
                host_action(host, "reveal"); host_action(host, "reveal"); host_action(host, "advance")
        with client.websocket_connect(guest_url(room, identity["guest_token"])) as guest:
            restore(guest, identity)
            guest.send_json({"type": "accuse", "suspect": "felix", "rationale": "My private reasoning."})
            public = guest.receive_json()["data"]
            private = guest.receive_json()["data"]
    rooms.clear()
    with TestClient(app) as restarted:
        assert restarted.get(f"/api/rooms/{room['room_id']}/state").json() == public
        with restarted.websocket_connect(guest_url(room, identity["guest_token"])) as guest:
            assert restore(guest, identity) == private


@pytest.mark.parametrize("change", [
    {"assignments": {"g": "missing-role"}},
    {"assignments": {}},
    {"introductions": {"other": "Not this guest"}},
    {"introductions": {"g": "x" * 241}},
    {"rationales": {"g": "Orphan reason"}},
])
def test_invalid_private_fields_fail_without_changing_saved_record(tmp_path, monkeypatch, change):
    path = tmp_path / "invalid-private.sqlite3"
    monkeypatch.setenv("MYSTERY_DB_PATH", str(path))
    record = Room("ABC123", "host", guests={"g": {"name": "Alice", "token": "guest"}}, assignments={"g": "ada"}).record()
    record.update(change)
    RoomStore(path).save(record)
    with pytest.raises(StorageError, match="Invalid saved room"):
        with TestClient(app):
            pass
    assert RoomStore(path).load_all() == [record]


def test_invalid_legacy_record_prevents_all_startup_migration_writes(tmp_path, monkeypatch):
    path = tmp_path / "atomic-migration.sqlite3"
    monkeypatch.setenv("MYSTERY_DB_PATH", str(path))
    records = []
    for room_id in ("ABC123", "DEF456"):
        record = Room(room_id, "host").record()
        record["schema_version"] = 1
        for field in ("assignments", "introductions", "rationales", "ai_calls", "dialogue_source", "dialogue_reason"):
            record.pop(field)
        records.append(record)
    records[1]["act"] = 99
    store = RoomStore(path)
    store.save_many(records)
    with pytest.raises(StorageError, match="Invalid saved room"):
        with TestClient(app):
            pass
    assert store.load_all() == records



def test_dialogue_provider_receives_public_facts_not_private_card(client, monkeypatch):
    room = create(client)
    observed = []
    class InspectProvider:
        def respond(self, text, state):
            observed.append(copy.deepcopy(state))
            return "A public answer."
    monkeypatch.setattr("backend.main.provider", InspectProvider())
    with client.websocket_connect(guest_url(room)) as guest:
        _, _, private = join(guest, "Private speaker")
        guest.send_json({"type": "dialogue", "text": "What about Ada?"})
        assert guest.receive_json()["data"]["dialogue"] == "A public answer."
        guest.receive_json()
    assert private["character"]["private_brief"] not in json.dumps(observed)
    assert "objectives" not in json.dumps(observed)


def test_save_many_database_error_rolls_back_the_entire_batch(tmp_path):
    store = RoomStore(tmp_path / "batch.sqlite3")
    initial = {"schema_version": 1, "room_id": "ABC123", "dialogue": "Before"}
    store.save(initial)
    with pytest.raises(StorageError):
        store.save_many([
            {**initial, "dialogue": "Must not commit"},
            {"schema_version": 1, "room_id": {"invalid": "SQL parameter"}, "dialogue": "Broken"},
        ])
    assert store.load_all() == [initial]
