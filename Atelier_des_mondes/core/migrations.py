"""Data migration system."""

from __future__ import annotations

from typing import Callable, Dict, List


class MigrationManager:
    def __init__(self, db, logger):
        self.db = db
        self.logger = logger
        self._migrations: Dict[int, Callable] = {}

    def register(self, version: int, func: Callable):
        self._migrations[version] = func

    def migrate_to(self, target: int):
        current = self.db.version()
        if current >= target:
            return True
        for v in range(current + 1, target + 1):
            if v not in self._migrations:
                self.logger.warning("migrations", f"No migration for version {v}")
                # bump anyway
                self.db.set_version(v)
                continue
            try:
                self._migrations[v](self.db)
                self.db.set_version(v)
                self.logger.info("migrations", f"Migrated to {v}")
            except Exception as e:
                self.logger.error("migrations", f"Migration {v} failed: {e}")
                return False
        return True

    def latest(self) -> int:
        return max(self._migrations.keys()) if self._migrations else self.db.version()
