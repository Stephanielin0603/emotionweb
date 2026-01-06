from __future__ import annotations
from typing import List, Dict
from pathlib import Path
import json

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "seasons.json"

def list_seasons() -> List[Dict]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
