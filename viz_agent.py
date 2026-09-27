"""Visualization / Reporting Agent - maps, charts, advisories, explanations"""

import folium


def viz_agent(state: dict) -> dict:
    location = state.get("location", "unspecified location")

    # Default map center - replace with real geocoded lat/lon for `location`
    # once you wire up a geocoder (e.g. geopy with Nominatim, which is also free).
    lat, lon = 9.9312, 76.2673  # placeholder: Kochi, India

    m = folium.Map(location=[lat, lon], zoom_start=8)
    folium.Marker(
        [lat, lon],
        popup=location,
        tooltip="Query location",
    ).add_to(m)

    output_path = "orca_map.html"
    m.save(output_path)

    report_parts = []
    if "risk_data" in state:
        verdict_label = state["risk_data"].get("verdict", "unknown").upper()
        report_parts.append(f"SAFETY VERDICT [{verdict_label}]: " + state["risk_data"]["summary"])
    if "weather_data" in state:
        report_parts.append("WEATHER: " + state["weather_data"]["summary"])
    if "ocean_data" in state:
        report_parts.append("OCEAN: " + state["ocean_data"]["summary"])
    if "geo_data" in state:
        report_parts.append("GEO: " + state["geo_data"]["summary"])

    return {"response": "\n\n".join(report_parts) + f"\n\nMap saved to {output_path}"}
