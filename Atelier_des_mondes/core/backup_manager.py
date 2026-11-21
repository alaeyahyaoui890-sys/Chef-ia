"""Backup and recovery manager."""

from __future__ import annotations

import json
import os
import shutil
import sqlite3
from datetime import datetime
from typing import List, Optional


class BackupManager:
    def __init__(self, data_dir: str, db: "Database", logger):
        self.data_dir = data_dir
        self.db = db
        self.logger = logger
        self.backup_dir = os.path.join(data_dir, "backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, label: str = "auto") -> str:
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        name = f"backup_{label}_{ts}"
        dest = os.path.join(self.backup_dir, name)
        os.makedirs(dest, exist_ok=True)
        # copy db
        src_db = self.db.db_path
        shutil.copy2(src_db, os.path.join(dest, "app.db"))
        # atomic write marker
        with open(os.path.join(dest, "manifest.json"), "w") as f:
            json.dump({"label": label, "created": ts}, f)
        self.logger.info("backup", f"Created backup {name}")
        return dest

    def list_backups(self) -> List[str]:
        if not os.path.exists(self.backup_dir):
            return []
        return sorted(os.listdir(self.backup_dir))

    def restore(self, backup_name: str) -> bool:
        src = os.path.join(self.backup_dir, backup_name, "app.db")
        if not os.path.exists(src):
            return False
        # backup current first
        self.create_backup("pre_restore")
        tmp = self.db.db_path + ".restore"
        shutil.copy2(src, tmp)
        self.db.close()
        os.replace(tmp, self.db.db_path)
        # reopen
        self.db.conn = sqlite3.connect(self.db.db_path, check_same_thread=False)
        self.db.conn.row_factory = sqlite3.Row
        self.logger.info("backup", f"Restored {backup_name}")
        return True

    def detect_abnormal(self) -> bool:
        # simple: check for leftover tmp
        return os.path.exists(self.db.db_path + ".tmp")
