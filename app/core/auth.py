from __future__ import annotations

import bcrypt
from typing import Optional
from app.core.db import Database


def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def verify_password(password: str, hashed: bytes) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed)
    except Exception:
        return False


def ensure_bootstrap_admin(db: Database) -> None:
    # Create default roles
    db.execute(
        """
        INSERT OR IGNORE INTO roles (code, label)
        VALUES 
        ('admin', 'Administrateur'), 
        ('sales', 'Commercial'),
        ('stock', 'Stock'),
        ('account', 'Comptable');
        """
    )
    # Create default admin user (admin/admin) if none exists
    row = db.scalar("SELECT COUNT(1) FROM users;")
    if not row:
        pwd = hash_password("admin")
        db.execute(
            "INSERT INTO users (username, password_hash, role_code, is_active) VALUES (?, ?, ?, 1);",
            ("admin", pwd, "admin"),
        )


def authenticate(db: Database, username: str, password: str) -> Optional[dict]:
    rows = db.query("SELECT id, username, password_hash, role_code, is_active FROM users WHERE username = ?;", (username,))
    if not rows:
        return None
    row = rows[0]
    if not row["is_active"]:
        return None
    if verify_password(password, row["password_hash"]):
        return {
            "id": row["id"],
            "username": row["username"],
            "role": row["role_code"],
        }
    return None

