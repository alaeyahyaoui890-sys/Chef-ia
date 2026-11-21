"""Central event bus."""

from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List


@dataclass
class Event:
    event_id: str
    name: str
    version: str
    timestamp: str
    payload: Any = None


class EventBus:
    def __init__(self, logger):
        self.logger = logger
        self._subs: Dict[str, List[Callable]] = {}
        self._lock = threading.RLock()

    def subscribe(self, event_name: str, callback: Callable) -> str:
        with self._lock:
            self._subs.setdefault(event_name, []).append(callback)
        return str(uuid.uuid4())

    def unsubscribe(self, event_name: str, callback: Callable):
        with self._lock:
            if event_name in self._subs:
                self._subs[event_name] = [c for c in self._subs[event_name] if c is not callback]

    def publish(self, name: str, payload: Any = None, version: str = "1.0") -> Event:
        ev = Event(str(uuid.uuid4()), name, version, datetime.utcnow().isoformat(), payload)
        with self._lock:
            subs = list(self._subs.get(name, []))
            # wildcard
            subs += list(self._subs.get("*", []))
        for cb in subs:
            try:
                cb(ev)
            except Exception as e:
                self.logger.error("event_bus", f"Subscriber error on {name}: {e}")
        return ev
