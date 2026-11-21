"""SQLite database wrapper."""

from __future__ import annotations

import os
import sqlite3
from typing import Any, List, Tuple


class Database:
    def __init__(self, db_path: str):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        c = self.conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY)""")
        c.execute("""CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            created_at TEXT,
            modified_at TEXT,
            version TEXT,
            state TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            title TEXT,
            content TEXT,
            created_at TEXT,
            modified_at TEXT,
            FOREIGN KEY(project_id) REFERENCES projects(id)
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS resources (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            path TEXT,
            rtype TEXT,
            size INTEGER,
            sha256 TEXT
        )""")
        c.execute("""CREATE TABLE IF NOT EXISTS versions (
            id TEXT PRIMARY KEY,
            project_id TEXT,
            version_number INTEGER,
            snapshot TEXT,
            created_at TEXT
        )""")
        self.conn.commit()
        # ensure version row
        c.execute("SELECT COUNT(*) FROM schema_version")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO schema_version (version) VALUES (1)")
            self.conn.commit()

    def version(self) -> int:
        c = self.conn.cursor()
        c.execute("SELECT version FROM schema_version")
        return c.fetchone()[0]

    def set_version(self, v: int):
        c = self.conn.cursor()
        c.execute("UPDATE schema_version SET version=?", (v,))
        self.conn.commit()

    def execute(self, sql, params=()):
        c = self.conn.cursor()
        c.execute(sql, params)
        self.conn.commit()
        return c

    def fetchall(self, sql, params=()):
        c = self.conn.cursor()
        c.execute(sql, params)
        return c.fetchall()

    def fetchone(self, sql, params=()):
        c = self.conn.cursor()
        c.execute(sql, params)
        return c.fetchone()

    def close(self):
        self.conn.close()
