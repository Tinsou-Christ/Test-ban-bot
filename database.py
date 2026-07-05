"""
database.py
Gère toutes les interactions avec la base SQLite :
- utilisateurs (limite d'usage quotidienne)
- dossiers de preuves créés
- statistiques pour le panel admin
"""

import sqlite3
from datetime import datetime, date
from contextlib import contextmanager

DB_PATH = "bot_data.db"


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Crée les tables si elles n'existent pas encore."""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_seen TEXT,
                is_banned INTEGER DEFAULT 0
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS usage (
                user_id INTEGER,
                usage_date TEXT,
                count INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, usage_date)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS dossiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                target TEXT,
                description TEXT,
                created_at TEXT
            )
        """)


def register_user(user_id: int, username: str):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if not c.fetchone():
            c.execute(
                "INSERT INTO users (user_id, username, first_seen) VALUES (?, ?, ?)",
                (user_id, username, datetime.utcnow().isoformat())
            )


def is_banned(user_id: int) -> bool:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT is_banned FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        return bool(row and row["is_banned"])


def set_banned(user_id: int, banned: bool):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET is_banned = ? WHERE user_id = ?", (1 if banned else 0, user_id))


def get_today_count(user_id: int) -> int:
    today = date.today().isoformat()
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT count FROM usage WHERE user_id = ? AND usage_date = ?", (user_id, today))
        row = c.fetchone()
        return row["count"] if row else 0


def increment_usage(user_id: int):
    today = date.today().isoformat()
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT count FROM usage WHERE user_id = ? AND usage_date = ?", (user_id, today))
        row = c.fetchone()
        if row:
            c.execute(
                "UPDATE usage SET count = count + 1 WHERE user_id = ? AND usage_date = ?",
                (user_id, today)
            )
        else:
            c.execute(
                "INSERT INTO usage (user_id, usage_date, count) VALUES (?, ?, 1)",
                (user_id, today)
            )


def log_dossier(user_id: int, target: str, description: str):
    with get_conn() as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO dossiers (user_id, target, description, created_at) VALUES (?, ?, ?, ?)",
            (user_id, target, description, datetime.utcnow().isoformat())
        )


def count_users() -> int:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) as n FROM users")
        return c.fetchone()["n"]


def count_dossiers() -> int:
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) as n FROM dossiers")
        return c.fetchone()["n"]


def get_leaderboard(limit: int = 10):
    """Retourne les utilisateurs ayant créé le plus de dossiers."""
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT u.username, u.user_id, COUNT(d.id) as total
            FROM users u
            JOIN dossiers d ON u.user_id = d.user_id
            GROUP BY u.user_id
            ORDER BY total DESC
            LIMIT ?
        """, (limit,))
        return c.fetchall()


def get_all_users():
    with get_conn() as conn:
        c = conn.cursor()
        c.execute("SELECT user_id, username, first_seen, is_banned FROM users ORDER BY first_seen DESC")
        return c.fetchall()
