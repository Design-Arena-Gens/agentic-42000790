from __future__ import annotations

from pathlib import Path
from typing import List

from app.core.db import Database
from app.core.logger import get_logger


class MigrationManager:
    def __init__(self, db: Database, migrations_dir: Path) -> None:
        self.db = db
        self.migrations_dir = Path(migrations_dir)
        self.logger = get_logger(__name__)
        self._ensure_schema_table()

    def _ensure_schema_table(self) -> None:
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL UNIQUE,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            """
        )

    def applied_versions(self) -> set[str]:
        rows = self.db.query("SELECT version FROM schema_migrations ORDER BY version;")
        return {r["version"] for r in rows}

    def available_migrations(self) -> List[Path]:
        if not self.migrations_dir.exists():
            return []
        return sorted(self.migrations_dir.glob("*.sql"))

    def apply_pending_migrations(self) -> None:
        applied = self.applied_versions()
        for sql_file in self.available_migrations():
            version = sql_file.stem
            if version in applied:
                continue
            sql = sql_file.read_text(encoding="utf-8")
            self.logger.info(f"Applying migration {version}")
            self.db.conn.executescript(sql)
            self.db.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
            self.logger.info(f"Applied migration {version}")

