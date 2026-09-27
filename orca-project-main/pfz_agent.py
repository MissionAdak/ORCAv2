"""PFZ (Potential Fishing Zone) Agent - REAL real-time data, no LLM call.

Primary source: INCOIS's actual PFZ scraper (data_layer.get_incois_pfz) -
authoritative when it works, but currently unreliable (legacy server
session/500 issues, see debug history).

Real-time fallback: live satellite Sea Surface Temperature ANOMALY data
from NOAA CoastWatch (confirmed working - see debug session), used to
find temperature FRONTS (locations where the anomaly value changes
sharply between neighboring points). Fronts are a genuine, scientifically
established factor fish congregate around - cold/warm water boundaries
concentrate plankton and baitfish. This is real live data, computed
fresh from an actual satellite pass, not sample/fake data.

If both real sources fail (no internet, NOAA down, etc.) this returns
"not available" honestly - it does not fabricate data.
"""

import requests
from data_layer import get_incois_pfz, _geocode, _get_cached, _set_cached

SST_DATASET_URL = "https://coastwatch.noaa.gov/erddap/griddap/noaacrwsstanomalybaselineDaily.json"
CHLA_DATASET_URL = "https://coastwatch.noaa.gov/erddap/griddap/noaacwNPPVIIRSchlaDaily.json"
BOX_DEG = 0.3  # ~30km box around the query point, matching typical PFZ range


def _get_chlorophyll_context(lat, lon):
    """Fetches live chlorophyll-a data for the box around (lat, lon).
    Chlorophyll indicates plankton concentration - a real factor fish
    congregate around - but coverage is patchy (satellite ocean-color
    sensors can't see through cloud cover, common during monsoon season
    on India's west coast). Returns whatever real values ARE available
    as summary context; returns None if the whole box is cloud-blocked
    right now, which is a genuine data-availability fact, not an error."""
    cache_key = f"chla_{round(lat, 2)}_{round(lon, 2)}"
    cached = _get_cached("chla", cache_key)
    if cached is not None:
        return cached if cached != "NONE" else None

    lat_min, lat_max = lat - BOX_DEG, lat + BOX_DEG
    lon_min, lon_max = lon - BOX_DEG, lon + BOX_DEG

    url = (
        f"{CHLA_DATASET_URL}?chlor_a"
        f"[(last)][(0.0):(0.0)][({lat_min}):({lat_max})][({lon_min}):({lon_max})]"
    )

    try:
        resp = requests.get(url, timeout=20)
        data = resp.json()
        rows = data["table"]["rows"]  # [time, altitude, lat, lon, value]
        values = [r[4] for r in rows if r[4] is not None]
        if values:
            result = {
                "avg_chlor_a_mg_m3": round(sum(values) / len(values), 3),
                "max_chlor_a_mg_m3": round(max(values), 3),
                "valid_pixel_count": len(values),
                "total_pixel_count": len(rows),
            }
            _set_cached("chla", cache_key, result)
            return result
    except Exception:
        pass

    _set_cached("chla", cache_key, "NONE")
    return None


def _parse_distance_km(distance_str: str):
    try:
        parts = distance_str.split("-")
        nums = [float(p) for p in parts]
        return sum(nums) / len(nums)
    except (ValueError, AttributeError):
        return None


def _dms_to_decimal(dms_str: str):
    try:
        parts = dms_str.strip().split()
        degrees, minutes, seconds, direction = float(parts[0]), float(parts[1]), float(parts[2]), parts[3]
        decimal = degrees + minutes / 60 + seconds / 3600
        if direction in ("S", "W"):
            decimal = -decimal
        return decimal
    except (ValueError, IndexError, AttributeError):
        return None


def _get_sst_front_zones(lat, lon, top_n=5):
    """Queries live SST anomaly data in a box around (lat, lon), finds
    the grid points with the strongest local gradient (temperature
    fronts), and returns them as candidate fishing zones. Real data,
    computed fresh each call (cached 30 min via the normal cache)."""
    cache_key = f"sst_front_{round(lat, 2)}_{round(lon, 2)}"
    cached = _get_cached("sst_front", cache_key)
    if cached is not None:
        return cached

    lat_min, lat_max = lat - BOX_DEG, lat + BOX_DEG
    lon_min, lon_max = lon - BOX_DEG, lon + BOX_DEG

    url = (
        f"{SST_DATASET_URL}?sea_surface_temperature_anomaly"
        f"[(last)][({lat_min}):({lat_max})][({lon_min}):({lon_max})]"
    )

    try:
        resp = requests.get(url, timeout=20)
        data = resp.json()
        rows = data["table"]["rows"]  # [time, lat, lon, value]
    except Exception:
        _set_cached("sst_front", cache_key, [])
        return []

    # Build a grid: {(lat, lon): value}
    grid = {}
    for row in rows:
        _, glat, glon, val = row
        if val is not None:
            grid[(round(glat, 4), round(glon, 4))] = val

    if len(grid) < 4:
        _set_cached("sst_front", cache_key, [])
        return []

    # Figure out the actual grid spacing from the data itself (don't
    # assume a fixed value - different datasets have different resolutions).
    lats_sorted = sorted(set(k[0] for k in grid))
    lons_sorted = sorted(set(k[1] for k in grid))
    lat_step = round(lats_sorted[1] - lats_sorted[0], 4) if len(lats_sorted) > 1 else 0.05
    lon_step = round(lons_sorted[1] - lons_sorted[0], 4) if len(lons_sorted) > 1 else 0.05

    # For each point, compute the max difference to its immediate
    # neighbors - a simple, fast local gradient (front strength) measure.
    scored = []
    for (glat, glon), val in grid.items():
        neighbors = [
            grid.get((round(glat + lat_step, 4), glon)),
            grid.get((round(glat - lat_step, 4), glon)),
            grid.get((glat, round(glon + lon_step, 4))),
            grid.get((glat, round(glon - lon_step, 4))),
        ]
        diffs = [abs(val - n) for n in neighbors if n is not None]
        if diffs:
            scored.append({"lat": glat, "lon": glon, "value": val, "gradient": max(diffs)})

    scored.sort(key=lambda p: p["gradient"], reverse=True)
    top = scored[:top_n]
    _set_cached("sst_front", cache_key, top)
    return top


def pfz_agent(state: dict) -> dict:
    location = state.get("location", "unspecified location")

    # 1. Try the real INCOIS scraper first (authoritative when it works).
    raw = get_incois_pfz(location)
    landing_points = raw.get("landing_points", [])

    if landing_points:
        for point in landing_points:
            point["_distance_km_sort"] = _parse_distance_km(point.get("Distance (km)From-To", ""))
        ranked = sorted(
            [p for p in landing_points if p.get("_distance_km_sort") is not None],
            key=lambda p: p["_distance_km_sort"],
        )
        top_zones = [{
            "coast_from": p.get("From the coast of"), "direction": p.get("Direction"),
            "bearing_deg": p.get("Bearing (deg)"), "distance_km_range": p.get("Distance (km)From-To"),
            "depth_m_range": p.get("Depth (mtr)From-To"),
            "latitude": _dms_to_decimal(p.get("Latitude (dms)", "")),
            "longitude": _dms_to_decimal(p.get("Longitude (dms)", "")),
        } for p in ranked[:5]]
        coords_for_chla = _geocode(location)
        chla_context = _get_chlorophyll_context(*coords_for_chla[:2]) if coords_for_chla else None
        return {"pfz_data": {"raw": raw, "available": True, "is_sample_data": False,
                              "source": "INCOIS", "top_zones": top_zones,
                              "total_zones_found": len(landing_points),
                              "chlorophyll_context": chla_context}}

    # 2. INCOIS unavailable - fall back to REAL live SST front data.
    coords = _geocode(location)
    if coords:
        lat, lon, resolved_name = coords
        fronts = _get_sst_front_zones(lat, lon)
        chla_context = _get_chlorophyll_context(lat, lon)
        if fronts:
            top_zones = [{
                "coast_from": f"SST front near {resolved_name}",
                "direction": None, "bearing_deg": None,
                "distance_km_range": None, "depth_m_range": None,
                "latitude": f["lat"], "longitude": f["lon"],
                "sst_anomaly_c": f["value"], "gradient_c": round(f["gradient"], 2),
            } for f in fronts]
            return {"pfz_data": {"raw": raw, "available": True, "is_sample_data": False,
                                  "source": "Live NOAA SST anomaly fronts (temperature-based estimate)",
                                  "top_zones": top_zones, "total_zones_found": len(top_zones),
                                  "chlorophyll_context": chla_context}}

    # 3. Both real sources unavailable - no fake data, be honest.
    return {"pfz_data": {"raw": raw, "available": False, "is_sample_data": False, "top_zones": []}}
