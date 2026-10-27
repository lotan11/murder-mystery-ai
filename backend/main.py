from __future__ import annotations
import asyncio
import secrets
from dataclasses import dataclass, field
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .mystery import TITLE, SUSPECTS, EVIDENCE, SOLUTION
from .dialogue import DialogueProvider, MockDialogueProvider

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="Wobblebottom Mystery Prototype", version="0.1.0")
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
    dialogue: str = "Good evening. Welcome to Blackwood Manor. Keep your theories sharp and your fingerprints to yourself."
    clients: set = field(default_factory=set)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    def snapshot(self):
        return {"room_id": self.room_id, "title": TITLE, "act": self.act,
                "phase": ["Lobby", "The discovery", "The contradictions", "The accusation", "Case closed"][self.act],
                "paused": self.paused, "revision": self.revision,
                "guests": [{"id": k, "name": v["name"]} for k, v in self.guests.items()],
                "evidence": [e.copy() for e in EVIDENCE if e["id"] in self.revealed],
                "available_evidence": [{"id": e["id"], "title": e["title"], "act": e["act"]} for e in EVIDENCE if e["act"] == self.act and e["id"] not in self.revealed],
                "suspects": SUSPECTS, "dialogue": self.dialogue,
                "performance": {"emotion": "thoughtful", "gesture": "notes"},
                "votes": {s["id"]: list(self.votes.values()).count(s["id"]) for s in SUSPECTS},
                "solution": SOLUTION if self.act == 4 else None,
                "integrations": {"dialogue": "deterministic mock", "microphone": "not connected", "avatar": "procedural placeholder", "lip_sync": "not connected"}}

rooms: dict[str, Room] = {}

@app.get("/health")
def health():
    return {"ok": True, "storage": "in-memory", "dialogue": "deterministic mock"}

@app.post("/api/rooms", status_code=201)
def create_room():
    while True:
        room_id = secrets.token_hex(3).upper()
        if room_id not in rooms:
            break
    room = Room(room_id, secrets.token_urlsafe(32))
    rooms[room_id] = room
    return {"room_id": room_id, "organizer_token": room.organizer_token}

def get_room(room_id):
    room = rooms.get(room_id.upper())
    if room is None:
        raise HTTPException(404, "Room not found")
    return room

@app.get("/api/rooms/{room_id}/state")
def read_state(room_id: str):
    return get_room(room_id).snapshot()

async def broadcast(room):
    packet = {"type": "state", "data": room.snapshot()}
    for client in list(room.clients):
        try:
            await client.send_json(packet)
        except Exception:
            room.clients.discard(client)

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
        room.dialogue = "A fresh investigation. Try to look surprised this time."
        return
    if room.paused:
        raise ValueError("Resume the room before progressing the case.")
    if action == "start":
        if room.act != 0:
            raise ValueError("The case has already started.")
        room.act = 1
        room.dialogue = "Lord Blackwood is dead. The tea is cold, the guests are nervous, and I have missed pudding. Let us begin."
    elif action == "reveal":
        candidates = [e for e in EVIDENCE if e["act"] == room.act and e["id"] not in room.revealed]
        evidence_id = msg.get("evidence_id")
        clue = next((e for e in candidates if evidence_id is None or e["id"] == evidence_id), None)
        if clue is None:
            raise ValueError("That clue is unavailable in this act.")
        room.revealed.append(clue["id"])
        room.dialogue = f"{clue['title']}. {clue['description']} Do resist the urge to lick the evidence."
    elif action == "advance":
        if room.act not in (1, 2, 3):
            raise ValueError("There is no act to advance.")
        if any(e["act"] == room.act and e["id"] not in room.revealed for e in EVIDENCE):
            raise ValueError("Reveal every clue in this act before advancing.")
        room.act += 1
        room.dialogue = SOLUTION if room.act == 4 else "The plot thickens. Unlike the soup, it now has substance. Examine the next evidence."
    else:
        raise ValueError("Unknown organizer action.")

@app.websocket("/ws/{room_id}")
async def socket(ws: WebSocket, room_id: str, role: str = "tv", token: str = "", guest_token: str = ""):
    room = rooms.get(room_id.upper())
    if room is None or role not in ("tv", "guest", "organizer") or (role == "organizer" and not secrets.compare_digest(token, room.organizer_token)):
        await ws.close(code=1008)
        return
    await ws.accept()
    identity = next((k for k, g in room.guests.items() if guest_token and secrets.compare_digest(g["token"], guest_token)), None) if role == "guest" else None
    room.clients.add(ws)
    await ws.send_json({"type": "state", "data": room.snapshot()})
    if identity:
        await ws.send_json({"type": "joined", "guest_id": identity, "guest_token": room.guests[identity]["token"]})
    try:
        while True:
            try:
                msg = await ws.receive_json()
                if not isinstance(msg, dict):
                    raise ValueError("Expected an object command.")
                async with room.lock:
                    kind = msg.get("type")
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
                        else:
                            room.guests[identity]["name"] = name.strip()
                        await ws.send_json({"type": "joined", "guest_id": identity, "guest_token": room.guests[identity]["token"]})
                    elif kind == "control":
                        if role != "organizer":
                            raise ValueError("Organizer access required.")
                        control(room, msg)
                    elif kind in ("dialogue", "accuse"):
                        if role != "organizer" and not (role == "guest" and identity):
                            raise ValueError("Join as a guest before contributing.")
                        if room.paused:
                            raise ValueError("The investigation is paused.")
                        if kind == "dialogue":
                            text = msg.get("text")
                            if not isinstance(text, str) or not text.strip() or len(text) > 500:
                                raise ValueError("Enter a statement between 1 and 500 characters.")
                            room.dialogue = provider.respond(text, room.snapshot())
                        else:
                            if role != "guest" or room.act != 3:
                                raise ValueError("Joined guests may accuse during act three.")
                            suspect = msg.get("suspect")
                            if suspect not in {s["id"] for s in SUSPECTS}:
                                raise ValueError("Unknown suspect.")
                            room.votes[identity] = suspect
                    else:
                        raise ValueError("Unknown command.")
                    room.revision += 1
                    await broadcast(room)
            except (ValueError, TypeError) as exc:
                await ws.send_json({"type": "error", "message": str(exc)})
    except WebSocketDisconnect:
        pass
    finally:
        room.clients.discard(ws)

DIST = ROOT / "frontend" / "dist"
if DIST.exists():
    if (DIST / "assets").exists():
        app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")
    @app.get("/{path:path}")
    def frontend(path: str):
        if path.startswith(("api/", "ws/")):
            raise HTTPException(404, "Not found")
        return FileResponse(DIST / "index.html")
