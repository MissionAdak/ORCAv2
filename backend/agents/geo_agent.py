"""Geospatial Agent - maritime boundary proximity check, pure Python math,
no LLM call (the phrasing happens in the one combined report call at the
end, in viz_agent.py). See weather_agent.py's docstring for why.

Uses REAL, treaty-sourced coordinates for the India-Sri Lanka maritime
boundary (Bay of Bengal segment only - see maritime_boundaries.geojson
for the important coverage caveat). This is a prototype/starting point,
NOT a certified navigational aid. Always verify against official Indian
Naval Hydrographic Office charts for real decisions.
"""

import json
import math
from data_layer import _geocode

BOUNDARY_FILE = "maritime_boundaries.geojson"
WARNING_DISTANCE_KM = 20

_boundaries_cache = None


def _load_boundaries():
    global _boundaries_cache
    if _boundaries_cache is None:
        with open(BOUNDARY_FILE, "r") as f:
            _boundaries_cache = json.load(f)["features"]
    return _boundaries_cache


def _closest_point_on_segment(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return ax, ay
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return ax + t * dx, ay + t * dy


def _degree_distance_km(lon1, lat1, lon2, lat2):
    avg_lat_rad = math.radians((lat1 + lat2) / 2)
    dx_km = (lon2 - lon1) * 111.0 * math.cos(avg_lat_rad)
    dy_km = (lat2 - lat1) * 111.0
    return math.sqrt(dx_km ** 2 + dy_km ** 2)


def _point_to_line_km(lon, lat, coords):
    min_dist = None
    for i in range(len(coords) - 1):
        ax, ay = coords[i]
        bx, by = coords[i + 1]
        cx, cy = _closest_point_on_segment(lon, lat, ax, ay, bx, by)
        d = _degree_distance_km(lon, lat, cx, cy)
        if min_dist is None or d < min_dist:
            min_dist = d
    return min_dist


def geo_agent(state: dict) -> dict:
    location = state.get("location", "unspecified location")

    coords = _geocode(location)
    if not coords:
        return {"geo_data": {"raw": None, "nearest_km": None, "nearest_boundary": None}}

    lat, lon, resolved_name = coords
    features = _load_boundaries()
    nearest_km = None
    nearest_name = None

    for feature in features:
        line_coords = feature["geometry"]["coordinates"]
        dist_km = _point_to_line_km(lon, lat, line_coords)
        if nearest_km is None or dist_km < nearest_km:
            nearest_km = dist_km
            nearest_name = feature["properties"]["name"]

    return {
        "geo_data": {
            "raw": {"resolved_name": resolved_name},
            "nearest_km": nearest_km,
            "nearest_boundary": nearest_name,
            "within_warning_distance": nearest_km is not None and nearest_km <= WARNING_DISTANCE_KM,
        }
    }
