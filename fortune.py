from __future__ import annotations
from typing import Dict, List, Optional
from pathlib import Path
import json, time, random

from db import get_conn

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "fortunes.json"

def _load_fortunes() -> List[Dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def list_fortunes() -> List[Dict]:
    # 給前端做「24 張卡片點選」
    return _load_fortunes()

def get_fortune_by_id(fid: int) -> Optional[Dict]:
    for f in _load_fortunes():
        if int(f["id"]) == int(fid):
            return f
    return None

def draw_fortune(user_id: str, cooldown_hours: int = 24) -> Dict:
    """
    從「未抽過」池子抽；若 24 支都抽過就重置（刪除該 user 的 draw_log）
    """
    fortunes = _load_fortunes()
    if not fortunes:
        raise ValueError("No fortunes configured")

    now = int(time.time())
    cutoff = now - cooldown_hours * 3600

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
      SELECT fortune_id FROM draw_log
      WHERE user_id = ? AND drawn_at >= ?
    """, (user_id, cutoff))
    recent = {int(r["fortune_id"]) for r in cur.fetchall()}

    all_ids = [int(f["id"]) for f in fortunes]
    pool = [fid for fid in all_ids if fid not in recent]

    if not pool:
        # 代表在 cooldown 規則下「都抽過了」，重置
        cur.execute("DELETE FROM draw_log WHERE user_id = ?", (user_id,))
        conn.commit()
        pool = all_ids[:]

    chosen_id = random.choice(pool)

    cur.execute("""
      INSERT INTO draw_log(user_id, fortune_id, drawn_at)
      VALUES (?, ?, ?)
    """, (user_id, chosen_id, now))
    conn.commit()
    conn.close()

    chosen = get_fortune_by_id(chosen_id)
    if not chosen:
        raise ValueError("Chosen fortune missing from data")
    return chosen
