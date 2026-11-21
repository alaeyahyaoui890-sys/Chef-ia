"""Shared execution context provided to modules."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from typing import Any, Callable, Dict


@dataclass
class KernelContext:
    kernel: Any
    logger: Any
    settings: Any
    resources: Any
    events: Any
    services: Any
    tasks: Any
    storage: Any
    project_manager: Any
    backup: Any
    _lock: threading.RLock = field(default_factory=threading.RLock, repr=False)

    def get_service(self, name: str, version: str | None = None):
        return self.kernel.services.get(name, version)

    def publish(self, name: str, payload: Any = None, version: str = "1.0"):
        return self.kernel.events.publish(name, payload, version=version)
