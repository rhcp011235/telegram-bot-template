import sqlite3
from dataclasses import dataclass
from typing import Optional, Tuple
from datetime import datetime


VALID_ROLES = {"NORMAL", "VIP", "ADMIN"}


@dataclass
class User:
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    role: str
    created_at: str


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    username TEXT,
                    first_name TEXT,
                    role TEXT NOT NULL DEFAULT 'NORMAL',
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def upsert_user(self, telegram_id: int, username: Optional[str], first_name: Optional[str]) -> None:
        created_at = datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO users (telegram_id, username, first_name, role, created_at)
                VALUES (?, ?, ?, 'NORMAL', ?)
                ON CONFLICT(telegram_id) DO UPDATE SET
                    username=excluded.username,
                    first_name=excluded.first_name
                """,
                (telegram_id, username, first_name, created_at),
            )
            conn.commit()

    def get_user_role(self, telegram_id: int) -> Optional[str]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT role FROM users WHERE telegram_id = ?",
                (telegram_id,),
            ).fetchone()
            return row["role"] if row else None

    def set_role(self, telegram_id: int, role: str) -> bool:
        role = role.upper().strip()
        if role not in VALID_ROLES:
            raise ValueError(f"Invalid role: {role}. Must be one of: {sorted(VALID_ROLES)}")

        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE users SET role = ? WHERE telegram_id = ?",
                (role, telegram_id),
            )
            conn.commit()
            return cur.rowcount > 0

    def ensure_user_exists(self, telegram_id: int, username: Optional[str], first_name: Optional[str]) -> None:
        # If user doesn't exist, insert. If exists, update username/first_name.
        self.upsert_user(telegram_id, username, first_name)

    def list_users(self, limit: int = 50) -> list[Tuple[int, str, str]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT telegram_id, role, COALESCE(username,'') AS username FROM users ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [(int(r["telegram_id"]), str(r["role"]), str(r["username"])) for r in rows]
