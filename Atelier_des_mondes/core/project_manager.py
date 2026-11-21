"""Project manager."""

from __future__ import annotations

import json
import os
import shutil
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from core.database import Database


class ProjectManager:
    def __init__(self, db: Database, data_dir: str, logger, backup_manager):
        self.db = db
        self.data_dir = data_dir
        self.logger = logger
        self.backup = backup_manager
        self.projects_dir = os.path.join(data_dir, "projects")
        os.makedirs(self.projects_dir, exist_ok=True)
        self._current: Optional[str] = None

    def create(self, name: str, description: str = "") -> str:
        pid = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        self.db.execute(
            "INSERT INTO projects (id,name,description,created_at,modified_at,version,state) VALUES (?,?,?,?,?,?,?)",
            (pid, name, description, now, now, "1.0", "open"),
        )
        # create folder
        os.makedirs(os.path.join(self.projects_dir, pid), exist_ok=True)
        self.logger.info("project", f"Created project {pid}")
        return pid

    def open(self, pid: str) -> Optional[Dict[str, Any]]:
        row = self.db.fetchone("SELECT * FROM projects WHERE id=?", (pid,))
        if not row:
            return None
        self._current = pid
        return dict(row)

    def close(self):
        self._current = None

    def rename(self, pid: str, new_name: str):
        self.db.execute("UPDATE projects SET name=?, modified_at=? WHERE id=?",
                        (new_name, datetime.utcnow().isoformat(), pid))

    def duplicate(self, pid: str) -> str:
        row = self.db.fetchone("SELECT * FROM projects WHERE id=?", (pid,))
        if not row:
            raise ValueError("not found")
        new_id = self.create(row["name"] + " (copy)", row["description"])
        return new_id

    def archive(self, pid: str):
        self.db.execute("UPDATE projects SET state='archived', modified_at=? WHERE id=?",
                        (datetime.utcnow().isoformat(), pid))

    def delete(self, pid: str, confirm: bool = False):
        if not confirm:
            raise ValueError("confirmation required")
        self.db.execute("DELETE FROM documents WHERE project_id=?", (pid,))
        self.db.execute("DELETE FROM resources WHERE project_id=?", (pid,))
        self.db.execute("DELETE FROM versions WHERE project_id=?", (pid,))
        self.db.execute("DELETE FROM projects WHERE id=?", (pid,))
        # remove folder
        p = os.path.join(self.projects_dir, pid)
        if os.path.exists(p):
            shutil.rmtree(p, ignore_errors=True)
        if self._current == pid:
            self._current = None

    def list_projects(self) -> List[Dict[str, Any]]:
        rows = self.db.fetchall("SELECT * FROM projects")
        return [dict(r) for r in rows]

    def find(self, name: str) -> List[Dict[str, Any]]:
        rows = self.db.fetchall("SELECT * FROM projects WHERE name LIKE ?", (f"%{name}%",))
        return [dict(r) for r in rows]

    def verify_integrity(self, pid: str) -> bool:
        row = self.db.fetchone("SELECT * FROM projects WHERE id=?", (pid,))
        return row is not None

    def save_version(self, pid: str, snapshot: Dict[str, Any]) -> str:
        vid = str(uuid.uuid4())
        # count
        c = self.db.fetchone("SELECT COUNT(*) AS n FROM versions WHERE project_id=?", (pid,))
        n = (c["n"] if c else 0) + 1
        self.db.execute(
            "INSERT INTO versions (id,project_id,version_number,snapshot,created_at) VALUES (?,?,?,?,?)",
            (vid, pid, n, json.dumps(snapshot), datetime.utcnow().isoformat()),
        )
        self.db.execute("UPDATE projects SET modified_at=? WHERE id=?",
                        (datetime.utcnow().isoformat(), pid))
        return vid

    def list_versions(self, pid: str) -> List[Dict[str, Any]]:
        rows = self.db.fetchall("SELECT * FROM versions WHERE project_id=? ORDER BY version_number", (pid,))
        return [dict(r) for r in rows]

    def restore_version(self, pid: str, version_id: str) -> Optional[Dict[str, Any]]:
        row = self.db.fetchone("SELECT * FROM versions WHERE id=?", (version_id,))
        if not row:
            return None
        # preserve current as new version before restore
        self.backup.create_backup("pre_restore_version")
        return json.loads(row["snapshot"])

    def compare_versions(self, v1: str, v2: str) -> Dict[str, Any]:
        r1 = self.db.fetchone("SELECT * FROM versions WHERE id=?", (v1,))
        r2 = self.db.fetchone("SELECT * FROM versions WHERE id=?", (v2,))
        return {"v1": json.loads(r1["snapshot"]) if r1 else None,
                "v2": json.loads(r2["snapshot"]) if r2 else None}
