"""Risk Agent - safety verdict, pure code logic, no LLM call.

This was already mostly rule-based (the hard safety rule that refuses to
say "safe" without usable data was always decided in code, not by the
LLM). The one thing removed here is the final LLM call that used to
phrase the verdict into prose - that's now done once, combined with
everything else, in viz_agent.py's single report-writing call.
"""

import re

WIND_SPEED_DANGER_KMH = 45
WAVE_HEIGHT_DANGER_M = 2.5


def _current_value(raw: dict, field: str):
    try:
        return raw["hourly"][field][0]
    except (KeyError, IndexError, TypeError):
        return None


def _data_is_usable(raw_source) -> bool:
    if not raw_source or not isinstance(raw_source, dict):
        return False
    bad_markers = ("error", "no match", "not configured", "not yet configured", "not available", "location_not_found")
    text_blob = str(raw_source).lower()
    return not any(marker in text_blob for marker in bad_markers)


def risk_agent(state: dict) -> dict:
    weather_raw = state.get("weather_data", {}).get("raw", {})
    ocean_raw = state.get("ocean_data", {}).get("raw", {})

    weather_usable = _data_is_usable(weather_raw)
    ocean_usable = _data_is_usable(ocean_raw)

    flags = []
    wind_speed = _current_value(weather_raw, "wind_speed_10m") if weather_usable else None
    if wind_speed and wind_speed >= WIND_SPEED_DANGER_KMH:
        flags.append(f"High wind speed (~{wind_speed} km/h)")

    wave_height = _current_value(ocean_raw, "wave_height") if ocean_usable else None
    if wave_height and wave_height >= WAVE_HEIGHT_DANGER_M:
        flags.append(f"High wave height (~{wave_height} m)")

    # HARD RULE, decided in code: no usable data means no "safe" verdict, ever.
    if not (weather_usable and ocean_usable):
        missing = [n for n, usable in [("weather", weather_usable), ("ocean", ocean_usable)] if not usable]
        return {"risk_data": {"flags": flags, "verdict": "inconclusive", "missing": missing}}

    verdict = "risk_flagged" if flags else "clear"
    return {"risk_data": {"flags": flags, "verdict": verdict, "missing": []}}
