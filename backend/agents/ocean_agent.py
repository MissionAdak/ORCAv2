"""Ocean Analytics Agent - wave/sea state data fetch only (no LLM call).
See weather_agent.py's docstring for why - one combined LLM call at the
end replaces the per-agent calls for speed."""

from data_layer import get_open_meteo_marine  # TEMPORARY: swap to get_incois_pfz once INCOIS scraping is finalized


def ocean_agent(state: dict) -> dict:
    location = state.get("location", "unspecified location")
    marine_data = get_open_meteo_marine(location)
    return {"ocean_data": {"raw": marine_data}}
