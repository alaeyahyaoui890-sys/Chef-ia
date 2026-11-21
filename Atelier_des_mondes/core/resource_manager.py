"""Resource manager: centralized local file access and metadata."""

from __future__ import annotations

import hashlib
import os
import threading
from typing import Any, Dict, Optional


class ResourceManager:
    def __init__(self, base_dir: str, logger):
        self.base_dir = os.path.abspath(base_dir)
        self.logger = logger
        self._meta: Dict[str, Dict[str, Any]] = {}
        self._cache: Dict[str, Any] = {}
        self._lock = threading.RLock()
        os.makedirs(self.base_dir, exist_ok=True)

    def _safe_path(self, path: str) -> str:
        ap = os.path.abspath(path)
        if not (ap == self.base_dir or ap.startswith(self.base_dir + os.sep)):
            raise PermissionError(f"Access outside allowed directory: {path}")
        return ap

    def exists(self, path: str) -> bool:
        try:
            return os.path.exists(self._safe_path(path))
        except Exception:
            return False

    def read_bytes(self, path: str) -> bytes:
        p = self._safe_path(path)
        if not os.path.exists(p):
            raise FileNotFoundError(p)
        with open(p, "rb") as f:
            return f.read()

    def write_bytes(self, path: str, data: bytes):
        p = self._safe_path(path)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        tmp = p + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, p)
        self._hash(p)

    def delete(self, path: str):
        p = self._safe_path(path)
        if os.path.exists(p):
            os.remove(p)
            self._meta.pop(p, None)

    def _hash(self, path: str):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        self._meta[path] = {"size": os.path.getsize(path), "sha256": h.hexdigest(), "path": path}

    def metadata(self, path: str) -> Dict[str, Any]:
        p = self._safe_path(path)
        if p not in self._meta and os.path.exists(p):
            self._hash(p)
        return self._meta.get(p, {})

    def temp_file(self, name: str) -> str:
        d = os.path.join(self.base_dir, "temporary")
        os.makedirs(d, exist_ok=True)
        return os.path.join(d, name)

    def cleanup_temp(self):
        d = os.path.join(self.base_dir, "temporary")
        if os.path.exists(d):
            for f in os.listdir(d):
                try:
                    os.remove(os.path.join(d, f))
                except Exception:
                    pass
