from __future__ import annotations
from typing import Any, Dict, Optional
import httpx

OPENWEATHER_URL = "https://api.openweathermap.org/data/2.5/forecast"

async def get_24h_forecast(city: str, api_key: str, country_code: Optional[str] = None) -> Dict[str, Any]:
    """
    回傳未來 24 小時概覽（OpenWeatherMap 3hr forecast 切前 8 筆）
    """
    if not api_key:
        raise ValueError("Missing OpenWeatherMap API key")

    q = f"{city},{country_code}" if country_code else city
    params = {
        "q": q,
        "appid": api_key,
        "units": "metric",
        "lang": "zh_tw",
    }

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(OPENWEATHER_URL, params=params)
        r.raise_for_status()
        data = r.json()

    # list 是 3 小時一筆；24 小時 = 8 筆
    items = (data.get("list") or [])[:8]
    out = []
    for it in items:
        out.append({
            "dt": it.get("dt"),
            "time_text": it.get("dt_txt"),
            "temp_c": (it.get("main") or {}).get("temp"),
            "feels_like_c": (it.get("main") or {}).get("feels_like"),
            "humidity": (it.get("main") or {}).get("humidity"),
            "weather": ((it.get("weather") or [{}])[0]).get("description"),
            "wind_mps": (it.get("wind") or {}).get("speed"),
        })

    city_info = data.get("city") or {}
    return {
        "city": city_info.get("name", city),
        "country": city_info.get("country"),
        "timezone": city_info.get("timezone"),
        "items_24h": out,
    }
