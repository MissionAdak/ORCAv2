"""Weather Agent - wind/rain data fetch only (no LLM call here anymore).

Speed optimization: this used to make its own LLM call to phrase a
summary. That meant 5 separate LLM round-trips per query (route + weather
+ ocean + geo + risk), which is what made each region take 3.5-4.5 min on
a local CPU model. Now this just fetches and returns raw numbers; ONE
combined LLM call at the end (in viz_agent.py) writes the whole report
from all the raw data at once.
"""

from data_layer import get_open_meteo_weather  # TEMPORARY: swap to get_imd_weather once IMD access is ready


def weather_agent(state: dict) -> dict:
    location = state.get("location", "unspecified location")
    raw_data = get_open_meteo_weather(location)
    return {"weather_data": {"raw": raw_data}}
