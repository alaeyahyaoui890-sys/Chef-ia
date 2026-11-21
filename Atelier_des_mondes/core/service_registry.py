"""Service registry for inter-module service lookup."""

from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ServiceEntry:
    name: str
    version: str
    provider: str
    instance: Any
    capabilities: List[str]


class ServiceRegistry:
    def __init__(self, logger):
        self.logger = logger
        self._services: Dict[str, List[ServiceEntry]] = {}
        self._lock = threading.RLock()

    def register(self, name, instance, provider, version="1.0", capabilities=None):
        with self._lock:
            self._services.setdefault(name, []).append(
                ServiceEntry(name, version, provider, instance, capabilities or [])
            )
        self.logger.info("service_registry", f"Registered {name} v{version} by {provider}")

    def unregister_provider(self, provider):
        with self._lock:
            for name in list(self._services):
                self._services[name] = [s for s in self._services[name] if s.provider != provider]
                if not self._services[name]:
                    del self._services[name]

    def get(self, name, version=None):
        with self._lock:
            entries = self._services.get(name, [])
            if version:
                entries = [e for e in entries if e.version == version]
            if not entries:
                return None
            return entries[-1].instance

    def list_services(self):
        with self._lock:
            return {k: [(e.provider, e.version) for e in v] for k, v in self._services.items()}
