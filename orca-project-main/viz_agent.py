"""Visualization / Reporting Agent - map + the ONE combined LLM call.

Speed optimization: instead of each agent (weather/ocean/geo/risk) making
its own LLM call to phrase its piece, all their raw data gets handed to
a SINGLE LLM call here that writes the whole fisherman-facing report at
once. This is the main fix for the 3.5-4.5 min/region runtime - fewer
LLM round-trips is the only real lever available on a local CPU model.
"""

import json
from langchain_ollama import ChatOllama
import folium
from data_layer import _geocode

import os

# Resource-level tuning:
# - num_predict caps how many tokens the model is allowed to generate.
#   Inference time scales almost linearly with output length, so this is
#   the single most direct lever for making each call faster - without
#   it, the model can ramble well past what 4 short sections need.
# - num_thread pins CPU thread usage to your actual core count. Ollama
#   usually auto-detects this reasonably, but being explicit avoids any
#   case where it under- or over-allocates threads on your specific machine.
# - num_ctx keeps the context window at a size that actually fits our
#   short prompts, rather than defaulting larger than necessary.
llm = ChatOllama(
    model="llama3.1:8b",
    num_predict=400,
    num_thread=os.cpu_count(),
    num_ctx=2048,
)


def _dms_to_decimal(dms_str: str):
    """Converts INCOIS's coordinate format (e.g. '13 34 45 N' or '92 44 8 E')
    into decimal degrees for plotting on the map. Returns None if the
    string doesn't parse as expected."""
    try:
        parts = dms_str.strip().split()
        degrees, minutes, seconds, direction = float(parts[0]), float(parts[1]), float(parts[2]), parts[3]
        decimal = degrees + minutes / 60 + seconds / 3600
        if direction in ("S", "W"):
            decimal = -decimal
        return decimal
    except (ValueError, IndexError, AttributeError):
        return None


def viz_agent(state: dict) -> dict:
    location = state.get("location", "unspecified location")

    coords = _geocode(location)
    if coords:
        lat, lon, resolved_name = coords
    else:
        lat, lon, resolved_name = 9.9312, 76.2673, location  # fallback: Kochi, India

    # --- Map: query location, boundary line, and PFZ zone markers ---
    m = folium.Map(location=[lat, lon], zoom_start=7)
    folium.Marker([lat, lon], popup=location, tooltip="Query location").add_to(m)
    try:
        with open("maritime_boundaries.geojson", "r") as f:
            features = json.load(f)["features"]
        for feature in features:
            line_coords = feature["geometry"]["coordinates"]
            folium_coords = [(pt[1], pt[0]) for pt in line_coords]
            folium.PolyLine(folium_coords, color="red", weight=2, dash_array="5,10",
                             tooltip=feature["properties"]["name"]).add_to(m)
    except Exception:
        pass

    pfz_data = state.get("pfz_data", {})
    for zone in pfz_data.get("top_zones", []):
        try:
            zone_lat = zone.get("latitude")
            zone_lon = zone.get("longitude")
            if zone_lat is not None and zone_lon is not None:
                folium.Marker(
                    [zone_lat, zone_lon],
                    popup=f"{zone.get('coast_from', 'PFZ')} - {zone.get('distance_km_range', '?')} km",
                    tooltip="Potential Fishing Zone",
                    icon=folium.Icon(color="green", icon="fish", prefix="fa"),
                ).add_to(m)
        except Exception:
            continue

    route_data = state.get("route_data", {})
    if route_data.get("available"):
        route_coords = [(wp["lat"], wp["lon"]) for wp in route_data.get("waypoints", [])]
        if len(route_coords) >= 2:
            folium.PolyLine(
                route_coords, color="blue", weight=3,
                tooltip=f"Optimized route - {route_data.get('total_distance_km')} km total",
            ).add_to(m)

    output_path = "orca_map.html"
    m.save(output_path)

    # --- The one combined LLM call ---
    risk_data = state.get("risk_data", {})
    geo_data = state.get("geo_data", {})

    # The safety verdict's "can we say it's safe" decision is still 100%
    # code-controlled (never left to the LLM) - we just ask it to phrase
    # whichever verdict was already decided.
    verdict = risk_data.get("verdict", "unknown")
    if verdict == "inconclusive":
        verdict_instruction = (
            f"The verdict MUST be reported as INCONCLUSIVE - do not say it's safe. "
            f"Missing/unusable data: {risk_data.get('missing', [])}. "
            f"Tell the fisherman to check IMD's official bulletins directly."
        )
    else:
        verdict_instruction = (
            f"The verdict is '{verdict}'. Risk flags found: {risk_data.get('flags') or 'none'}."
        )

    if pfz_data.get("available"):
        pfz_instruction = (
            f"Real INCOIS Potential Fishing Zone data found {pfz_data.get('total_zones_found')} "
            f"zones. Closest 5 (already sorted nearest-first): {pfz_data.get('top_zones')}. "
            f"Summarize the 2-3 closest/most practical zones by name and distance."
        )
    else:
        pfz_instruction = (
            "No PFZ data available for this sector right now - say fishing zone "
            "data isn't available rather than inventing zones."
        )

    if route_data.get("available"):
        route_instruction = (
            f"An optimized visiting order for the fishing zones was computed: "
            f"{route_data.get('waypoints')}. Total trip distance: "
            f"{route_data.get('total_distance_km')} km. Summarize the suggested "
            f"order (by name) and total distance in plain language."
        )
    else:
        route_instruction = "No route could be computed - say so rather than inventing one."

    prompt = (
        f"You are a maritime safety assistant writing a report for a fisherman "
        f"about {resolved_name}. Write SIX short sections using these exact "
        f"headers: SAFETY VERDICT, WEATHER, OCEAN, BOUNDARY CHECK, POTENTIAL FISHING ZONES, SUGGESTED ROUTE.\n\n"
        f"SAFETY VERDICT instruction: {verdict_instruction}\n\n"
        f"Weather raw data: {state.get('weather_data', {}).get('raw')}\n\n"
        f"Ocean raw data: {state.get('ocean_data', {}).get('raw')}\n\n"
        f"Boundary check: nearest mapped boundary is {geo_data.get('nearest_boundary')}, "
        f"approximately {geo_data.get('nearest_km')} km away. Note this only covers a "
        f"partial boundary (Bay of Bengal segment of India-Sri Lanka line) and is not "
        f"an official navigational chart.\n\n"
        f"POTENTIAL FISHING ZONES instruction: {pfz_instruction}\n\n"
        f"SUGGESTED ROUTE instruction: {route_instruction}\n\n"
        f"If any raw data shows an error or is missing, say that section's data isn't "
        f"available rather than inventing numbers. Keep each section to 2-3 sentences."
    )
    result = llm.invoke(prompt)

    return {"response": result.content + f"\n\nMap saved to {output_path}"}
