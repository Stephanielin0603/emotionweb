from __future__ import annotations
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from pathlib import Path

from db import init_db
from weather import get_24h_forecast
from emotions import list_emotions
from seasons import list_seasons
from fortune import list_fortunes, draw_fortune, get_fortune_by_id
from ritual import lock_state, get_locked_state

app = FastAPI(title="Emotion Weather Hub")

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/", response_class=HTMLResponse)
def home():
    return TEMPLATE_PATH.read_text(encoding="utf-8")

# ---------- STEP：資料清單 ----------
@app.get("/api/emotions")
def api_emotions():
    return {"items": list_emotions()}

@app.get("/api/seasons")
def api_seasons():
    return {"items": list_seasons()}

@app.get("/api/fortunes")
def api_fortunes():
    return {"items": list_fortunes()}

# ---------- STEP：天氣 ----------
@app.post("/api/weather")
async def api_weather(payload: dict):
    city = payload.get("city", "")
    api_key = payload.get("api_key", "")
    if not city:
        raise HTTPException(400, "city is required")
    try:
        data = await get_24h_forecast(city=city, api_key=api_key)
        return data
    except Exception as e:
        raise HTTPException(400, f"weather error: {e}")

# ---------- STEP：儀式 FSM ----------
@app.post("/api/ritual/lock")
def api_lock(payload: dict):
    user_id = payload.get("user_id")
    weather = payload.get("weather", "")
    emotion_id = payload.get("emotion_id", "")
    season_id = payload.get("season_id", "")

    if not user_id:
        raise HTTPException(400, "user_id is required")
    if not emotion_id or not season_id:
        raise HTTPException(400, "emotion_id and season_id are required")

    return lock_state(user_id=user_id, weather=weather, emotion_id=emotion_id, season_id=season_id)

@app.post("/api/ritual/draw")
def api_draw(payload: dict):
    """
    STEP 3：倒數完成後才呼叫，後端才抽籤 + 寫入紀錄
    """
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(400, "user_id is required")

    locked = get_locked_state(user_id)
    if not locked:
        raise HTTPException(400, "state not locked yet")

    season_id = locked.get("season_id")
    try:
        fortune = draw_fortune(user_id=user_id, cooldown_hours=24)
        quote = (fortune.get("quote_templates") or {}).get(season_id, "")
        return {
            "fortune": fortune,
            "quote": quote,
            "locked_state": locked
        }
    except Exception as e:
        raise HTTPException(400, f"draw error: {e}")

@app.get("/api/fortune/{fid}")
def api_fortune(fid: int, season_id: str = "winter"):
    f = get_fortune_by_id(fid)
    if not f:
        raise HTTPException(404, "fortune not found")
    quote = (f.get("quote_templates") or {}).get(season_id, "")
    return {"fortune": f, "quote": quote}
