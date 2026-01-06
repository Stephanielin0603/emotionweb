from __future__ import annotations
from typing import List, Dict
from pathlib import Path
import json

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "emotions.json"

def list_emotions() -> List[Dict]:
    """
    給前端顯示的情緒清單：id / label / icon
    """
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)