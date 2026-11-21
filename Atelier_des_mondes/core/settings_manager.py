"""Centralized settings manager."""

from __future__ import annotations

import json
import os
from typing import Any, Dict


DEFAULTS = {
    "language": "fr",
    "theme": "default",
    "backup_interval_minutes": 5,
    "memory_limit_mb": 4096,
    "log_level": "INFO",
    "allowed_engines": [],
}


class SettingsManager:
    def __init__(self, settings_dir: str, logger):
        self.settings_dir = settings_dir
        os.makedirs(settings_dir, exist_ok=True)
        self.logger = logger
        self._path = os.path.join(settings_dir, "settings.json")
        self._data: Dict[str, Any] = dict(DEFAULTS)
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    self._data.update(data)
            except Exception as e:
                self.logger.warning("settings", f"Invalid settings, using defaults: {e}")
                self._data = dict(DEFAULTS)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        # basic validation: type check against defaults
        if key in DEFAULTS and type(value) is not type(DEFAULTS[key]) and DEFAULTS[key] is not None:
            self.logger.warning("settings", f"Type mismatch for {key}")
            return False
        self._data[key] = value
        self._save()
        return True

    def all(self):
        return dict(self._data)

    def _save(self):
        tmp = self._path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, self._path)

    def reset(self):
        self._data = dict(DEFAULTS)
        self._save()
