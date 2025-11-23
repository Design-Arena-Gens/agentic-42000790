from __future__ import annotations

from typing import Any, Optional
from app.core.db import Database


class AppSettings:
    def __init__(self, db: Database) -> None:
        self.db = db

    def ensure_defaults(self) -> None:
        defaults = {
            "vat_rate": "20.0",
            "currency": "EUR",
            "company_logo_path": "",
            "invoice_seq": "INV-000000",
            "quote_seq": "QTE-000000",
            "delivery_seq": "BL-000000",
        }
        for key, value in defaults.items():
            self.db.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?);",
                (key, value),
            )

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        row = self.db.query("SELECT value FROM settings WHERE key = ?;", (key,))
        if not row:
            return default
        return row[0]["value"]

    def set(self, key: str, value: str) -> None:
        self.db.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value;",
            (key, value),
        )

