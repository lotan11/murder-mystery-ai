from __future__ import annotations
import asyncio
import copy
import os
from contextlib import asynccontextmanager
import json
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .mystery import CASE_ID, CASE_VERSION, TITLE, SUSPECTS, EVIDENCE, SOLUTION, NARRATION
from .dialogue import DialogueProvider, MockDialogueProvider
from .storage import RoomStore, StorageError
from .characters import CHARACTERS
from .ai_dialogue import load_config, OpenAIPlanner, PlannerError
from .audition import router as audition_router
from .casting import router as casting_router
from .local_speech import LocalSpeechRenderer, create_router as local_speech_router
from .scholar_speech import ScholarSpeechRenderer, create_router as scholar_speech_router

ROOT = Path(__file__).resolve().parents[1]
@asynccontextmanager
async def lifespan(app: FastAPI):
    store = RoomStore(os.environ.get("MYSTERY_DB_PATH", str(ROOT / "data" / "mystery.sqlite3")))
    records = store.load_all()
    restored = {record["room_id"]: Room.from_record(record) for record in records}
    # Validate every record before committing an additive schema migration.
    legacy = [restored[record["room_id"]].record() for record in records if record["schema_version"] in (1, 2)]
    if legacy:
        store.save_many(legacy)
    rooms.clear()
    rooms.update(restored)
    app.state.room_store = store
    app.state.planner_config = load_config()
    app.state.planner = OpenAIPlanner(app.state.planner_config)
    app.state.planner_tasks = set()
    app.state.local_speech = LocalSpeechRenderer()
    app.state.scholar_speech = ScholarSpeechRenderer()
    try:
        yield
    finally:
        tasks = list(app.state.planner_tasks)
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


app = FastAPI(title="Wobblebottom Mystery Prototype", version="0.4.0", lifespan=lifespan)
app.include_router(audition_router)
app.include_router(casting_router)
provider: DialogueProvider = MockDialogueProvider()

@dataclass
class Room:
    room_id: str
    organizer_token: str
    act: int = 0
    paused: bool = False
    revision: int = 0
    guests: dict = field(default_factory=dict)
    revealed: list = field(default_factory=list)
    votes: dict = field(default_factory=dict)
    assignments: dict = field(default_factory=dict)
    introductions: dict = field(default_factory=dict)
    rationales: dict = field(default_factory=dict)
    ai_calls: int = 0
    dialogue_source: str = "scripted"
    dialogue_reason: str = "initial"
    ai_busy: bool = False
    ai_request_id: str | None = None
    dialogue: str = NARRATION["welcome"]
    clients: set = field(default_factory=set)
    guest_clients: dict = field(default_factory=dict)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def record(self):
        # An explicit whitelist prevents accidental serialization of live sockets/locks.
        return copy.deepcopy({"schema_version": 3, "case_id": CASE_ID, "case_version": CASE_VERSION, "room_id": self.room_id,
                              "organizer_token": self.organizer_token, "act": self.act,
                              "paused": self.paused, "revision": self.revision,
                              "guests": self.guests, "revealed": self.revealed,
                              "votes": self.votes, "dialogue": self.dialogue,
                              "assignments": self.assignments, "introductions": self.introductions, "rationales": self.rationales,
                              "ai_calls": self.ai_calls, "dialogue_source": self.dialogue_source, "dialogue_reason": self.dialogue_reason})

    @classmethod
    def from_record(cls, record):
        if record.get("case_id") != CASE_ID or record.get("case_version") != CASE_VERSION:
            raise StorageError("Saved room uses an incompatible case version. Preserve the database and restore the matching case or explicitly start with a new database.")
        record = copy.deepcopy(record)
        legacy_fields = {"room_id", "organizer_token", "act", "paused", "revision", "guests", "revealed", "votes", "dialogue", "schema_version", "case_id", "case_version"}
        if record.get("schema_version") == 1 and set(record) == legacy_fields:
            record["schema_version"] = 2
            guests = record.get("guests")
            record["assignments"] = {guest_id: ("ada", "felix", "margot")[index] if index < 3 else "investigator"
                                     for index, guest_id in enumerate(guests)} if isinstance(guests, dict) else {}
            record["introductions"] = {}
            record["rationales"] = {guest_id: "" for guest_id in record.get("votes", {})} if isinstance(record.get("votes"), dict) else {}
        v2_fields = legacy_fields | {"assignments", "introductions", "rationales"}
        if record.get("schema_version") == 2 and set(record) == v2_fields:
            record.update(schema_version=3, ai_calls=0, dialogue_source="scripted", dialogue_reason="initial")
        fields = {"ai_calls", "dialogue_source", "dialogue_reason", "assignments", "introductions", "rationales", "room_id", "organizer_token", "act", "paused", "revision", "guests", "revealed", "votes", "dialogue"}
        metadata = {"schema_version", "case_id", "case_version"}
        known_clues = {clue["id"] for clue in EVIDENCE}
        known_suspects = {suspect["id"] for suspect in SUSPECTS}
        integer = lambda value: type(value) is int
        text = lambda value: isinstance(value, str) and bool(value)
        valid = (
            set(record) == fields | metadata
            and integer(record["schema_version"]) and record["schema_version"] == 3
            and integer(record["case_version"])
            and text(record["room_id"]) and len(record["room_id"]) == 6
            and all(character in "0123456789ABCDEF" for character in record["room_id"])
            and text(record["organizer_token"]) and record["organizer_token"].isascii()
            and integer(record["act"]) and 0 <= record["act"] <= 4
            and type(record["paused"]) is bool
            and integer(record["revision"]) and record["revision"] >= 0
            and integer(record["ai_calls"]) and record["ai_calls"] >= 0
            and record["dialogue_source"] in ("scripted", "model", "fallback")
            and isinstance(record["dialogue_reason"], str) and record["dialogue_reason"] in DIALOGUE_REASONS
            and isinstance(record["dialogue"], str)
            and isinstance(record["guests"], dict) and len(record["guests"]) <= 24
            and all(text(guest_id) and isinstance(guest, dict)
                    and set(guest) == {"name", "token"}
                    and text(guest["name"]) and len(guest["name"]) <= 40
                    and text(guest["token"]) and guest["token"].isascii()
                    for guest_id, guest in record["guests"].items())
            and isinstance(record["revealed"], list)
            and all(isinstance(clue, str) and clue in known_clues for clue in record["revealed"])
            and len(set(record["revealed"])) == len(record["revealed"])
            and isinstance(record["votes"], dict)
            and all(guest_id in record["guests"] and isinstance(suspect, str) and suspect in known_suspects
                    for guest_id, suspect in record["votes"].items())
            and isinstance(record["assignments"], dict) and set(record["assignments"]) == set(record["guests"])
            and all(isinstance(role, str) and role in CHARACTERS for role in record["assignments"].values())
            and all(list(record["assignments"].values()).count(role) <= 1 for role in ("ada", "felix", "margot"))
            and isinstance(record["introductions"], dict)
            and all(guest_id in record["guests"] and isinstance(intro, str) and 1 <= len(intro.strip()) <= 240
                    for guest_id, intro in record["introductions"].items())
            and isinstance(record["rationales"], dict) and set(record["rationales"]) == set(record["votes"])
            and all(isinstance(reason, str) and len(reason) <= 300 for reason in record["rationales"].values())
        )
        if not valid:
            raise StorageError("Invalid saved room record. Preserve the database for recovery; no saved data was discarded.")
        restored = cls(**{key: copy.deepcopy(record[key]) for key in fields})
        return restored

    def restore(self, record):
        for key, value in record.items():
            if key not in {"schema_version", "case_id", "case_version"}:
                setattr(self, key, copy.deepcopy(value))

    def next_character(self):
        return next((role for role in ("ada", "felix", "margot") if role not in self.assignments.values()), "investigator")

    def private_snapshot(self, guest_id):
        if guest_id not in self.guests:
            raise ValueError("Unknown guest identity.")
        return {"guest_id": guest_id, "character": copy.deepcopy(CHARACTERS[self.assignments[guest_id]]),
                "introduction_submitted": guest_id in self.introductions,
                "own_vote": {"suspect": self.votes[guest_id], "rationale": self.rationales.get(guest_id, "")} if guest_id in self.votes else None}

    def dialogue_meta(self):
        config = app.state.planner_config if hasattr(app.state, "planner_config") else load_config()
        reason = config.reason if self.dialogue_reason == "initial" else self.dialogue_reason
        if config.enabled and self.ai_calls >= config.max_calls and reason == "ready":
            reason = "budget_exhausted"
        return {"provider": config.provider if config.provider in ("scripted", "openai") else "scripted", "source": self.dialogue_source,
                "reason": reason,
                "calls_used": self.ai_calls, "calls_limit": config.max_calls,
                "available": config.enabled and self.ai_calls < config.max_calls,
                "busy": self.ai_busy}

    def snapshot(self):
        return {"room_id": self.room_id, "title": TITLE, "act": self.act,
                "phase": ["Lobby", "The discovery", "The contradictions", "The accusation", "Case closed"][self.act],
                "paused": self.paused, "revision": self.revision,
                "guests": [{"id": k, "name": v["name"], "character_id": self.assignments[k],
                            "character_name": CHARACTERS[self.assignments[k]]["name"], "introduced": k in self.introductions}
                           for k, v in self.guests.items()],
                "introductions": [{"guest_id": k, "name": self.guests[k]["name"],
                                   "character_name": CHARACTERS[self.assignments[k]]["name"], "text": intro}
                                  for k, intro in self.introductions.items()],
                "accusations": [{"guest_id": k, "name": self.guests[k]["name"], "suspect": suspect,
                                 "rationale": self.rationales.get(k, "")} for k, suspect in self.votes.items()] if self.act == 4 else [],
                "evidence": [e.copy() for e in EVIDENCE if e["id"] in self.revealed],
                "available_evidence": [{"id": e["id"], "title": e["title"], "act": e["act"]} for e in EVIDENCE if e["act"] == self.act and e["id"] not in self.revealed],
                "suspects": SUSPECTS, "dialogue": self.dialogue, "dialogue_meta": self.dialogue_meta(),
                "performance": {"emotion": "thoughtful", "gesture": "notes"},
                "votes": {s["id"]: list(self.votes.values()).count(s["id"]) for s in SUSPECTS},
                "solution": SOLUTION if self.act == 4 else None,
                "integrations": {"dialogue": "optional OpenAI planner" if self.dialogue_meta()["provider"] == "openai" and app.state.planner_config.enabled else "deterministic mock", "microphone": "not connected", "avatar": "procedural placeholder", "lip_sync": "not connected"}}

rooms: dict[str, Room] = {}

def token_matches(candidate: str, expected: str) -> bool:
    # compare_digest's string form rejects non-ASCII user input.
    return secrets.compare_digest(candidate.encode("utf-8"), expected.encode("utf-8"))

@app.get("/health")
def health():
    config = app.state.planner_config
    return {"ok": True, "storage": "sqlite", "dialogue": config.provider if config.provider in ("scripted", "openai") else "scripted",
            "ai_enabled": config.enabled, "ai_reason": config.reason, "ai_calls_limit": config.max_calls}

@app.post("/api/rooms", status_code=201)
async def create_room():
    while True:
        room_id = secrets.token_hex(3).upper()
        if room_id not in rooms:
            break
    room = Room(room_id, secrets.token_urlsafe(32))
    try:
        app.state.room_store.save(room.record())
    except StorageError as exc:
        raise HTTPException(503, "Room storage is unavailable. Try again after restoring storage.") from exc
    rooms[room_id] = room
    return {"room_id": room_id, "organizer_token": room.organizer_token}

def get_room(room_id):
    room = rooms.get(room_id.upper())
    if room is None:
        raise HTTPException(404, "Room not found")
    return room

app.include_router(local_speech_router(get_room))
app.include_router(scholar_speech_router(get_room))

@app.get("/api/rooms/{room_id}/state")
async def read_state(room_id: str):
    return get_room(room_id).snapshot()

async def broadcast(room):
    packet = {"type": "state", "data": room.snapshot()}
    for client in list(room.clients):
        try:
            await client.send_json(packet)
            identity = room.guest_clients.get(client)
            if identity:
                await client.send_json({"type": "private", "data": room.private_snapshot(identity)})
        except Exception:
            room.clients.discard(client)
            room.guest_clients.pop(client, None)

def control(room, msg):
    action = msg.get("action")
    if action == "pause":
        room.paused = True
        return
    if action == "resume":
        room.paused = False
        return
    if action == "reset":
        room.act = 0
        room.paused = False
        room.revealed.clear()
        room.votes.clear()
        room.rationales.clear()
        room.introductions.clear()
        room.dialogue_source = "scripted"
        room.dialogue_reason = "reset"
        room.dialogue = NARRATION["reset"]
        return
    if room.paused:
        raise ValueError("Resume the room before progressing the case.")
    if action == "assign":
        if room.act != 0:
            raise ValueError("Characters can only be assigned in the lobby.")
        guest_id, character_id = msg.get("guest_id"), msg.get("character_id")
        if not isinstance(guest_id, str) or guest_id not in room.guests:
            raise ValueError("Choose a joined guest.")
        if not isinstance(character_id, str) or character_id not in CHARACTERS:
            raise ValueError("Unknown character.")
        if character_id != "investigator" and any(k != guest_id and role == character_id for k, role in room.assignments.items()):
            raise ValueError("That character is already assigned. Free it before assigning it again.")
        room.assignments[guest_id] = character_id
        room.introductions.pop(guest_id, None)
    elif action == "start":
        if room.act != 0:
            raise ValueError("The case has already started.")
        room.dialogue_source, room.dialogue_reason = "scripted", "case_event"
        room.act = 1
        room.dialogue = NARRATION["start"]
    elif action == "reveal":
        candidates = [e for e in EVIDENCE if e["act"] == room.act and e["id"] not in room.revealed]
        evidence_id = msg.get("evidence_id")
        clue = next((e for e in candidates if evidence_id is None or e["id"] == evidence_id), None)
        if clue is None:
            raise ValueError("That clue is unavailable in this act.")
        room.dialogue_source, room.dialogue_reason = "scripted", "case_event"
        room.revealed.append(clue["id"])
        room.dialogue = f"{clue['title']}. {clue['description']}"
    elif action == "advance":
        if room.act not in (1, 2, 3):
            raise ValueError("There is no act to advance.")
        if any(e["act"] == room.act and e["id"] not in room.revealed for e in EVIDENCE):
            raise ValueError("Reveal every clue in this act before advancing.")
        room.dialogue_source, room.dialogue_reason = "scripted", "case_event"
        room.act += 1
        room.dialogue = SOLUTION if room.act == 4 else NARRATION["advance"]
    else:
        raise ValueError("Unknown organizer action.")

DIALOGUE_REASONS = {
    "initial", "ready", "scripted_default", "missing_paid_consent", "missing_api_key", "missing_model",
    "invalid_configuration", "scripted_policy", "budget_exhausted", "busy", "case_event", "reset",
    "timeout", "provider_error", "refused", "invalid_plan",
}


def public_planner_context(room):
    """Explicit allowlist: never forward the full room, user roster, cards or introductions."""
    snapshot = room.snapshot()
    return {"act": snapshot["act"], "evidence": [
        {key: clue[key] for key in ("id", "title", "description", "summary", "act") if key in clue}
        for clue in snapshot["evidence"]
    ], "suspects": [{key: suspect[key] for key in ("id", "name", "description")} for suspect in SUSPECTS]}


def scripted_policy(text, room):
    lower = text.casefold()
    return room.act not in (1, 2, 3) or not room.revealed or any(term in lower for term in (
        "hint", "help", "recap", "summary", "summarise", "summarize", "what do we know", "so far",
        "ignore", "system prompt", "hidden", "unrevealed", "spoiler", "killer", "murderer", "who did", "culprit", "solution",
    ))


async def finish_planner(room, ws, text, context, revision, act, request_id):
    """Network awaits never hold the room lock; late answers cannot overwrite newer play."""
    dialogue = None
    source, reason = "model", "ready"
    try:
        result = await asyncio.wait_for(app.state.planner.respond(text, context), timeout=app.state.planner_config.timeout_seconds)
        if not isinstance(result.dialogue, str) or not result.dialogue.strip() or len(result.dialogue) > 700:
            raise PlannerError("invalid_plan")
        dialogue = result.dialogue
    except asyncio.CancelledError:
        # The reserved attempt remains durable even when the server is stopped.
        raise
    except TimeoutError:
        source, reason = "fallback", "timeout"
    except PlannerError as exc:
        source = "fallback"
        reason = exc.reason if exc.reason in {"timeout", "provider_error", "refused", "invalid_plan"} else "provider_error"
    except Exception:
        source, reason = "fallback", "provider_error"
    async with room.lock:
        if room.ai_request_id != request_id:
            return
        room.ai_busy = False
        room.ai_request_id = None
        if room.revision != revision or room.act != act or room.paused:
            if ws in room.clients:
                try:
                    await ws.send_json({"type": "error", "message": "The room changed while the detective was considering that question. The late answer was discarded; ask again when ready."})
                except Exception:
                    room.clients.discard(ws)
            await broadcast(room)
            return
        before = room.record()
        room.dialogue = dialogue if source == "model" else provider.respond(text, room.snapshot())
        room.dialogue_source, room.dialogue_reason = source, reason
        room.revision += 1
        try:
            app.state.room_store.save(room.record())
        except StorageError:
            room.restore(before)
            if ws in room.clients:
                try:
                    await ws.send_json({"type": "error", "message": "The detective's answer could not be saved. The reserved attempt remains recorded; no answer was applied."})
                except Exception:
                    room.clients.discard(ws)
        await broadcast(room)


async def handle_dialogue(room, ws, role, identity, msg):
    async with room.lock:
        if role != "organizer" and not (role == "guest" and identity):
            raise ValueError("Join as a guest before contributing.")
        if role == "guest" and "guest_id" in msg:
            raise ValueError("Guest identity is bound to the connection, not a command field.")
        if room.paused:
            raise ValueError("The investigation is paused.")
        text = msg.get("text")
        if not isinstance(text, str) or not text.strip() or len(text) > 500:
            raise ValueError("Enter a statement between 1 and 500 characters.")
        config = app.state.planner_config
        before = room.record()
        reason = (config.reason if not config.enabled else
                  "scripted_policy" if scripted_policy(text, room) else
                  "busy" if room.ai_busy else
                  "budget_exhausted" if room.ai_calls >= config.max_calls else None)
        if reason == "busy":
            await ws.send_json({"type": "error", "message": "The detective is still considering the current question. Wait for that answer before submitting another."})
            return
        if reason is not None:
            room.dialogue = provider.respond(text, room.snapshot())
            room.dialogue_source = "fallback" if reason in {"busy", "budget_exhausted"} else "scripted"
            room.dialogue_reason = reason
            room.revision += 1
            try:
                app.state.room_store.save(room.record())
            except StorageError:
                room.restore(before)
                raise ValueError("Room changes could not be saved. No changes were applied; try again after restoring storage.")
            await broadcast(room)
            return
        room.ai_calls += 1
        room.revision += 1
        try:
            app.state.room_store.save(room.record())
        except StorageError:
            room.restore(before)
            raise ValueError("The AI attempt could not be reserved. No provider request was sent.")
        request_id = secrets.token_hex(12)
        room.ai_request_id, room.ai_busy = request_id, True
        context = public_planner_context(room)
        revision, act = room.revision, room.act
        await broadcast(room)
        task = asyncio.create_task(finish_planner(room, ws, text, context, revision, act, request_id))
        app.state.planner_tasks.add(task)
        task.add_done_callback(app.state.planner_tasks.discard)


@app.websocket("/ws/{room_id}")
async def socket(ws: WebSocket, room_id: str, role: str = "tv", token: str = "", guest_token: str = ""):
    room = rooms.get(room_id.upper())
    if room is None or role not in ("tv", "guest", "organizer") or (role == "organizer" and not token_matches(token, room.organizer_token)):
        await ws.close(code=1008)
        return
    await ws.accept()
    identity = next((k for k, g in room.guests.items() if guest_token and token_matches(guest_token, g["token"])), None) if role == "guest" else None
    room.clients.add(ws)
    if identity:
        room.guest_clients[ws] = identity
    try:
        await ws.send_json({"type": "state", "data": room.snapshot()})
        if identity:
            await ws.send_json({"type": "joined", "guest_id": identity, "guest_token": room.guests[identity]["token"]})
            await ws.send_json({"type": "private", "data": room.private_snapshot(identity)})
        while True:
            try:
                packet = await ws.receive()
                if packet["type"] == "websocket.disconnect":
                    raise WebSocketDisconnect(packet.get("code", 1000))
                if packet.get("text") is None:
                    raise ValueError("Send commands as JSON text, not binary data.")
                msg = json.loads(packet["text"])
                if not isinstance(msg, dict):
                    raise ValueError("Expected an object command.")
                if msg.get("type") == "dialogue":
                    await handle_dialogue(room, ws, role, identity, msg)
                    continue
                async with room.lock:
                    before = room.record()
                    previous_identity = identity
                    joined_packet = None
                    kind = msg.get("type")
                    if role == "guest" and "guest_id" in msg:
                        raise ValueError("Guest identity is bound to the connection, not a command field.")
                    if kind == "join":
                        if role != "guest":
                            raise ValueError("Only guest screens can join.")
                        name = msg.get("name")
                        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 40:
                            raise ValueError("Enter a name between 1 and 40 characters.")
                        if identity is None:
                            if len(room.guests) >= 24:
                                raise ValueError("This prototype supports 24 guests per room.")
                            identity = secrets.token_hex(8)
                            room.guests[identity] = {"name": name.strip(), "token": secrets.token_urlsafe(24)}
                            room.assignments[identity] = room.next_character()
                        else:
                            room.guests[identity]["name"] = name.strip()
                        joined_packet = {"type": "joined", "guest_id": identity, "guest_token": room.guests[identity]["token"]}
                    elif kind == "introduce":
                        if role != "guest" or not identity:
                            raise ValueError("Join as a guest before introducing yourself.")
                        if room.paused or room.act not in (0, 1):
                            raise ValueError("Introductions are open in the lobby and act one while unpaused.")
                        text = msg.get("text")
                        if not isinstance(text, str) or not 1 <= len(text.strip()) <= 240:
                            raise ValueError("Enter an introduction between 1 and 240 characters.")
                        room.introductions[identity] = text.strip()
                    elif kind == "control":
                        if role != "organizer":
                            raise ValueError("Organizer access required.")
                        control(room, msg)
                    elif kind == "accuse":
                        if role != "organizer" and not (role == "guest" and identity):
                            raise ValueError("Join as a guest before contributing.")
                        if room.paused:
                            raise ValueError("The investigation is paused.")
                        if role != "guest" or room.act != 3:
                            raise ValueError("Joined guests may accuse during act three.")
                        suspect = msg.get("suspect")
                        if suspect not in {s["id"] for s in SUSPECTS}:
                            raise ValueError("Unknown suspect.")
                        rationale = msg.get("rationale", "")
                        if not isinstance(rationale, str) or len(rationale) > 300:
                            raise ValueError("Keep your accusation reason within 300 characters.")
                        room.votes[identity] = suspect
                        room.rationales[identity] = rationale.strip()
                    else:
                        raise ValueError("Unknown command.")
                    room.revision += 1
                    try:
                        app.state.room_store.save(room.record())
                    except StorageError:
                        room.restore(before)
                        identity = previous_identity
                        raise ValueError("Room changes could not be saved. No changes were applied; try again after restoring storage.")
                    if joined_packet:
                        room.guest_clients[ws] = identity
                        await ws.send_json(joined_packet)
                    await broadcast(room)
            except (ValueError, TypeError) as exc:
                await ws.send_json({"type": "error", "message": str(exc)})
    except WebSocketDisconnect:
        pass
    finally:
        room.clients.discard(ws)
        room.guest_clients.pop(ws, None)

DIST = ROOT / "frontend" / "dist"
if DIST.exists():
    if (DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")
    if (DIST / "audition").exists():
        app.mount("/audition", StaticFiles(directory=DIST / "audition"), name="audition-assets")
    if (DIST / "casting").exists():
        app.mount("/casting", StaticFiles(directory=DIST / "casting"), name="casting-assets")
    if (DIST / "character-lab").exists():
        app.mount("/character-lab", StaticFiles(directory=DIST / "character-lab"), name="character-lab-assets")
    @app.get("/{path:path}")
    def frontend(path: str):
        if path.startswith(("api/", "ws/")):
            raise HTTPException(404, "Not found")
        return FileResponse(DIST / "index.html")
