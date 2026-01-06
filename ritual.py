from __future__ import annotations
from typing import Dict, Optional
import time
from db import get_conn

def lock_state(user_id: str, weather: str, emotion_id: str, season_id: str) -> Dict:
    """
    STEP 1：只鎖定狀態，不抽籤
    """
    now = int(time.time())
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
      INSERT INTO ritual_state(user_id, weather, emotion_id, season_id, locked_at)
      VALUES (?, ?, ?, ?, ?)
      ON CONFLICT(user_id) DO UPDATE SET
        weather=excluded.weather,
        emotion_id=excluded.emotion_id,
        season_id=excluded.season_id,
        locked_at=excluded.locked_at
    """, (user_id, weather, emotion_id, season_id, now))
    conn.commit()
    conn.close()

    return {
        "guide": "請把注意力放回此刻",
        "recommended_countdown_sec": 5,
        "locked_at": now
    }

def get_locked_state(user_id: str) -> Optional[Dict]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM ritual_state WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None
