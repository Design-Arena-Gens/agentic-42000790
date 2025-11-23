from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence


class Database:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")

    @property
    def conn(self) -> sqlite3.Connection:
        return self._conn

    def execute(self, sql: str, params: Optional[Sequence[Any]] = None) -> sqlite3.Cursor:
        cur = self._conn.cursor()
        cur.execute(sql, params or [])
        self._conn.commit()
        return cur

    def executemany(self, sql: str, seq_of_params: Iterable[Sequence[Any]]) -> sqlite3.Cursor:
        cur = self._conn.cursor()
        cur.executemany(sql, seq_of_params)
        self._conn.commit()
        return cur

    def query(self, sql: str, params: Optional[Sequence[Any]] = None) -> list[sqlite3.Row]:
        cur = self._conn.cursor()
        cur.execute(sql, params or [])
        rows = cur.fetchall()
        return rows

    def scalar(self, sql: str, params: Optional[Sequence[Any]] = None) -> Any:
        row = self.query(sql, params)
        if not row:
            return None
        return row[0][0]

