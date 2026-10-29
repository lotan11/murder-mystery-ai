"""Small process-local immutable JSON cache; no audio or dialogue written to disk."""
from __future__ import annotations
from collections import OrderedDict
import json
import math
import time


class SpeechCache:
    """Fixed insertion TTL, checked lazily with a monotonic clock; hits do not extend it."""
    def __init__(self, max_entries=4, max_bytes=32 * 1024 * 1024, ttl=900.0, clock=time.monotonic):
        if type(max_entries) is not int or max_entries < 0 or type(max_bytes) is not int or max_bytes < 0:
            raise ValueError('Cache limits must be nonnegative integers')
        if type(ttl) not in (int, float) or not math.isfinite(ttl) or ttl < 0 or not callable(clock):
            raise ValueError('Cache TTL/clock is invalid')
        self.max_entries, self.max_bytes, self.ttl, self.clock = max_entries, max_bytes, ttl, clock
        self._entries = OrderedDict()
        self._bytes = 0

    def _expire(self, now):
        for key, (expires, encoded) in list(self._entries.items()):
            if expires <= now:
                self._entries.pop(key)
                self._bytes -= len(encoded)

    def get(self, key):
        self._expire(self.clock())
        entry = self._entries.get(key)
        if entry is None:
            return None
        self._entries.move_to_end(key)
        return json.loads(entry[1])

    def put(self, key, value):
        now = self.clock()
        self._expire(now)
        if not self.max_entries or not self.max_bytes or not self.ttl:
            return False
        encoded = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode('utf-8')
        if len(encoded) > self.max_bytes:
            return False
        previous = self._entries.pop(key, None)
        if previous is not None:
            self._bytes -= len(previous[1])
        while self._entries and (len(self._entries) >= self.max_entries or self._bytes + len(encoded) > self.max_bytes):
            _, (_, evicted) = self._entries.popitem(last=False)
            self._bytes -= len(evicted)
        self._entries[key] = (now + self.ttl, encoded)
        self._bytes += len(encoded)
        return True

    def info(self):
        """Non-sensitive inspection for validation; never exposes text, cache keys or clips."""
        self._expire(self.clock())
        return {'entries': len(self._entries), 'payload_bytes': self._bytes,
                'max_entries': self.max_entries, 'max_bytes': self.max_bytes, 'ttl_seconds': self.ttl}
