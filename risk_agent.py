"""Risk Agent - safety, cyclone, lightning

Mostly rule-based (cheap, deterministic, no LLM needed for the logic
itself). Critically: whether the verdict is allowed to say "safe" is
decided IN CODE, not by the LLM. An LLM asked to "say inconclusive if
data's missing" will sometimes ignore that and invent a reassuring
answer anyway - unacceptable for a safety tool. So we check for missing/
errored data first and hard-block the "safe" verdict before the LLM
ever gets a chance to phrase one.
"""

from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.1:8b")

# Tune these thresholds to real safety guidance for your use case.
WIND_SPEED_DANGER_KMH = 45
WAVE_HEIGHT_DANGER_M = 2.5


def _extract_number(text: str, keyword: str) -> float | None:
    """Very naive helper to pull a number near a keyword out of free text.
    Replace with real structured-field parsing once your data sources
    return structured JSON instead of bulletin text."""
    import re
    match = re.search(rf"{keyword}[^\d]*(\d+(\.\d+)?)", text, re.IGNORECASE)
    return float(match.group(1)) if match else None


def _data_is_usable(raw_source: dict) -> bool:
    """Returns False if a data source came back empty, errored, or with
    a 'not configured / no match' note instead of real values."""
    if not raw_source:
        return False
    if not isinstance(raw_source, dict):
        return True  # e.g. a populated list from IMD - treat as usable
    bad_markers = ("error", "no match", "not configured", "not yet configured", "not available")
    text_blob = str(raw_source).lower()
    return not any(marker in text_blob for marker in bad_markers)


def risk_agent(state: dict) -> dict:
    weather_block = state.get("weather_data", {})
    ocean_block = state.get("ocean_data", {})

    weather_summary = weather_block.get("summary", "")
    ocean_summary = ocean_block.get("summary", "")

    weather_usable = _data_is_usable(weather_block.get("raw", weather_block))
    ocean_usable = _data_is_usable(ocean_block.get("raw", ocean_block))

    flags = []
    if weather_usable:
        wind_speed = _extract_number(weather_summary, "wind")
        if wind_speed and wind_speed >= WIND_SPEED_DANGER_KMH:
            flags.append(f"High wind speed detected (~{wind_speed} km/h)")

    if ocean_usable:
        wave_height = _extract_number(ocean_summary, "wave")
        if wave_height and wave_height >= WAVE_HEIGHT_DANGER_M:
            flags.append(f"High wave height detected (~{wave_height} m)")

    # HARD RULE, decided in code, not by the LLM: if we don't have usable
    # weather AND ocean data, the verdict CANNOT be "safe". Full stop.
    if not (weather_usable and ocean_usable):
        missing = []
        if not weather_usable:
            missing.append("weather")
        if not ocean_usable:
            missing.append("ocean")

        verdict = (
            f"INCONCLUSIVE - cannot verify safety. Missing or unavailable data: {', '.join(missing)}. "
            f"Do not treat this as a 'safe to go out' confirmation. Check IMD's official bulletins "
            f"directly (mausam.imd.gov.in) before deciding."
        )
        return {"risk_data": {"flags": flags, "verdict": "inconclusive", "summary": verdict}}

    # Only reach here if both sources returned real, usable data.
    prompt = (
        f"You are a maritime safety assistant. Risk flags detected: {flags if flags else 'none'}\n"
        f"Weather summary: {weather_summary}\n"
        f"Ocean summary: {ocean_summary}\n"
        f"Write a short, direct safety verdict for a fisherman: is it safe to go out, and why, "
        f"based only on the data given above."
    )
    result = llm.invoke(prompt)

    verdict = "risk_flagged" if flags else "clear"
    return {"risk_data": {"flags": flags, "verdict": verdict, "summary": result.content}}
