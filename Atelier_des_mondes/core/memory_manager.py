"""Memory manager: track usage, lazy loading hints."""

from __future__ import annotations

import sys
from typing import Any, Dict


class MemoryManager:
    def __init__(self, logger, limit_mb: int = 4096):
        self.logger = logger
        self.limit_mb = limit_mb
        self._loaded: Dict[str, Any] = {}

    def track(self, name: str, obj: Any):
        self._loaded[name] = obj

    def unload(self, name: str):
        if name in self._loaded:
            del self._loaded[name]

    def usage_mb(self) -> float:
        return sys.getsizeof(self._loaded) / (1024 * 1024)

    def can_load(self, estimated_mb: float = 0) -> bool:
        return self.usage_mb() + estimated_mb < self.limit_mb
