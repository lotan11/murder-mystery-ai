"""Durable room records; no browser projections, sockets, or asyncio locks belong here."""
from __future__ import annotations

import json
from contextlib import closing
import sqlite3
from pathlib import Path


class StorageError(RuntimeError):
    """A room could not be safely read or committed."""


class RoomStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with closing(self._connect()) as connection, connection:
                connection.execute(
                    "CREATE TABLE IF NOT EXISTS rooms (room_id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
                )
        except (OSError, sqlite3.Error) as exc:
            raise StorageError("Cannot initialize room storage.") from exc

    def _connect(self):
        return sqlite3.connect(self.path, timeout=3)

    def load_all(self) -> list[dict]:
        try:
            with closing(self._connect()) as connection, connection:
                rows = connection.execute("SELECT room_id, payload FROM rooms ORDER BY room_id").fetchall()
            records = [json.loads(row[1]) for row in rows]
            if not all(isinstance(record, dict) and record.get("schema_version") == 1
                       and record.get("room_id") == row[0] for row, record in zip(rows, records)):
                raise ValueError("Unsupported room record.")
            return records
        except (sqlite3.Error, ValueError, TypeError) as exc:
            raise StorageError("Cannot read saved rooms; preserve the database for recovery.") from exc

    def save(self, record: dict) -> None:
        try:
            payload = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
            with closing(self._connect()) as connection, connection:
                connection.execute(
                    "INSERT INTO rooms (room_id, payload) VALUES (?, ?) "
                    "ON CONFLICT(room_id) DO UPDATE SET payload = excluded.payload",
                    (record["room_id"], payload),
                )
        except (sqlite3.Error, ValueError, TypeError, KeyError) as exc:
            raise StorageError("Room changes could not be saved.") from exc
