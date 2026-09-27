"""Route Optimization Agent - pure Python, no LLM call.

Given the PFZ zones found by pfz_agent.py (which now provides clean
decimal latitude/longitude directly, whether from INCOIS or the live
SST-front fallback), computes the most efficient ORDER to visit them
from the fisherman's starting point, minimizing total straight-line
distance. Small Traveling Salesman Problem - brute force is instant
and optimal since pfz_agent caps zones at 5 (max 5! = 120 combinations).
"""

import itertools
import math
from data_layer import _geocode


def _distance_km(lat1, lon1, lat2, lon2):
    avg_lat_rad = math.radians((lat1 + lat2) / 2)
    dx_km = (lon2 - lon1) * 111.0 * math.cos(avg_lat_rad)
    dy_km = (lat2 - lat1) * 111.0
    return math.sqrt(dx_km ** 2 + dy_km ** 2)


def route_agent(state: dict) -> dict:
    location = state.get("location", "unspecified location")
    pfz_data = state.get("pfz_data", {})
    zones = pfz_data.get("top_zones", [])

    if not zones:
        return {"route_data": {"available": False, "waypoints": [], "total_distance_km": None}}

    start_coords = _geocode(location)
    if not start_coords:
        return {"route_data": {"available": False, "waypoints": [], "total_distance_km": None}}

    start_lat, start_lon, start_name = start_coords

    points = []
    for zone in zones:
        lat = zone.get("latitude")
        lon = zone.get("longitude")
        if lat is not None and lon is not None:
            points.append({"name": zone.get("coast_from", "Fishing zone"), "lat": lat, "lon": lon})

    if not points:
        return {"route_data": {"available": False, "waypoints": [], "total_distance_km": None}}

    best_order = None
    best_total = None
    for perm in itertools.permutations(points):
        total = 0.0
        prev_lat, prev_lon = start_lat, start_lon
        for p in perm:
            total += _distance_km(prev_lat, prev_lon, p["lat"], p["lon"])
            prev_lat, prev_lon = p["lat"], p["lon"]
        if best_total is None or total < best_total:
            best_total = total
            best_order = perm

    waypoints = [{"name": f"Start: {start_name}", "lat": start_lat, "lon": start_lon, "leg_distance_km": 0}]
    prev_lat, prev_lon = start_lat, start_lon
    for p in best_order:
        leg_km = _distance_km(prev_lat, prev_lon, p["lat"], p["lon"])
        waypoints.append({"name": p["name"], "lat": p["lat"], "lon": p["lon"], "leg_distance_km": round(leg_km, 1)})
        prev_lat, prev_lon = p["lat"], p["lon"]

    return {"route_data": {"available": True, "waypoints": waypoints, "total_distance_km": round(best_total, 1)}}
