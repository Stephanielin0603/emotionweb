from __future__ import annotations
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "app.db"

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ritual_state (
      user_id TEXT PRIMARY KEY,
      weather TEXT,
      emotion_id TEXT,
      season_id TEXT,
      locked_at INTEGER
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS draw_log (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT NOT NULL,
      fortune_id INTEGER NOT NULL,
      drawn_at INTEGER NOT NULL
    )
    """)
    conn.commit()
    conn.close()
