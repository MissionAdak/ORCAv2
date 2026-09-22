"""
Data Integration Layer
-----------------------
IMD and INCOIS both segment India's coast by STATE/region, not by city
(e.g. "Kerala Coast", "South Tamil Nadu coast"). CITY_TO_STATE_KEYWORD
translates common port cities to the right keyword for matching.

IMD: Calling seabulletin / coastalbulletin WITHOUT an `id` param returns
bulletins for ALL regions in one response, which we filter locally.

INCOIS: The PFZ page is session-based (confirmed from its actual page
source and direct testing): loading TextData?secid=SEC0XX sets the
sector in your session, then a plain GET to formattedForecast.action
on THE SAME session returns the raw data table HTML - no sector param
needed on that second call, since it reads from session state.

SECID_MAP below follows INCOIS's own dropdown order (confirmed with two
real data points: SEC012=ANDAMAN from the page source, SEC013=NICOBAR
from direct testing - both matching their position in the dropdown
list exactly, so SEC001-SEC014 follow that same fixed order). Tamil
Nadu and Andhra Pradesh are each split into North/South sectors by
INCOIS, so those keywords fetch both and combine the results.

MOSDAC: Mostly per-product download links, some requiring a free
account. Left as future work - INCOIS is the more practical source.
"""

import sqlite3
import json
import time
import requests

DB_PATH = "orca_cache.db"
CACHE_TTL_SECONDS = 60 * 30  # 30 minutes - tune as needed

# City -> state/region keyword, used for IMD's "Layer" field matching.
CITY_TO_STATE_KEYWORD = {
    "kochi": "kerala", "cochin": "kerala", "kollam": "kerala",
    "kozhikode": "kerala", "calicut": "kerala", "kannur": "kerala",
    "alappuzha": "kerala", "thiruvananthapuram": "kerala",
    "mangalore": "karnataka", "mangaluru": "karnataka", "karwar": "karnataka",
    "udupi": "karnataka",
    "mumbai": "maharashtra", "ratnagiri": "maharashtra", "sindhudurg": "maharashtra",
    "panaji": "goa", "goa": "goa", "vasco": "goa",
    "surat": "gujarat", "porbandar": "gujarat", "veraval": "gujarat",
    "jamnagar": "gujarat", "okha": "gujarat", "dwarka": "gujarat",
    "chennai": "tamil nadu", "mahabalipuram": "tamil nadu",
    "rameswaram": "tamil nadu", "tuticorin": "tamil nadu", "thoothukudi": "tamil nadu",
    "kanyakumari": "tamil nadu", "nagapattinam": "tamil nadu",
    "visakhapatnam": "andhra", "vizag": "andhra", "kakinada": "andhra",
    "nellore": "andhra", "machilipatnam": "andhra",
    "puri": "odisha", "paradip": "odisha", "gopalpur": "odisha",
    "kolkata": "west bengal", "digha": "west bengal", "diamond harbour": "west bengal",
    "port blair": "andaman",
}

# INCOIS secid per sector - follows the dropdown's fixed display order.
# Confirmed: SEC012=ANDAMAN (page source), SEC013=NICOBAR (direct test).
SECID_MAP = {
    "gujarat": ["SEC001"],
    "maharashtra": ["SEC002"],
    "goa": ["SEC003"],
    "karnataka": ["SEC004"],
    "kerala": ["SEC005"],
    "tamil nadu": ["SEC006", "SEC007"],   # South + North Tamil Nadu
    "andhra": ["SEC008", "SEC009"],       # South + North Andhra Pradesh
    "odisha": ["SEC010"],
    "west bengal": ["SEC011"],
    "andaman": ["SEC012"],
    "nicobar": ["SEC013"],
    "lakshadweep": ["SEC014"],
}


def _init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            source TEXT,
            key TEXT,
            payload TEXT,
            fetched_at REAL,
            PRIMARY KEY (source, key)
        )
    """)
    conn.commit()
    conn.close()


def _get_cached(source: str, key: str):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT payload, fetched_at FROM cache WHERE source=? AND key=?",
        (source, key),
    ).fetchone()
    conn.close()
    if row:
        payload, fetched_at = row
        if time.time() - fetched_at < CACHE_TTL_SECONDS:
            return json.loads(payload)
    return None


def _set_cached(source: str, key: str, payload):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO cache (source, key, payload, fetched_at) VALUES (?, ?, ?, ?)",
        (source, key, json.dumps(payload), time.time()),
    )
    conn.commit()
    conn.close()


_init_db()


def _to_state_keyword(location: str) -> str:
    return CITY_TO_STATE_KEYWORD.get(location.lower().strip(), location.lower().strip())


def _fetch_all_sea_bulletins():
    cached = _get_cached("imd_sea_all", "all")
    if cached:
        return cached
    try:
        resp = requests.get("https://api.imd.gov.in/api/v1/seabulletin", timeout=15)
        data = resp.json()
    except Exception as e:
        data = {"error": str(e)}
    _set_cached("imd_sea_all", "all", data)
    return data


def _fetch_all_coastal_bulletins():
    cached = _get_cached("imd_coastal_all", "all")
    if cached:
        return cached
    try:
        resp = requests.get("https://api.imd.gov.in/api/v1/coastalbulletin", timeout=15)
        data = resp.json()
    except Exception as e:
        data = {"error": str(e)}
    _set_cached("imd_coastal_all", "all", data)
    return data


def _filter_by_layer(bulletins, keyword: str):
    if not isinstance(bulletins, list):
        return []
    kw = keyword.lower()
    return [b for b in bulletins if kw in b.get("Layer", "").lower()]


def _geocode(location: str):
    """Free, keyless geocoding via Open-Meteo. Returns (lat, lon, resolved_name) or None.

    Retries a couple times with a short delay - multiple agents (weather,
    ocean, geo, pfz) can all fire their own geocode request for the same
    location at nearly the same instant (they run in parallel), and a
    transient network blip or momentary rate-limit can make one of them
    fail while the others succeed. This makes a single flaky attempt not
    silently kill an entire section of the report."""
    cached = _get_cached("geocode", location)
    if cached:
        return tuple(cached) if cached != "NONE" else None

    import time as _time
    last_error = None
    for attempt in range(3):
        try:
            resp = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": location, "count": 5, "language": "en", "format": "json"},
                timeout=10,
            )
            results = resp.json().get("results") or []

            chosen = next((r for r in results if r.get("country_code") == "IN"), None)
            if not chosen and results:
                chosen = results[0]

            if chosen:
                coords = (chosen["latitude"], chosen["longitude"], chosen.get("name", location))
                _set_cached("geocode", location, list(coords))
                return coords
            break  # got a real (empty) response, not an error - no point retrying
        except Exception as e:
            last_error = e
            _time.sleep(0.5 * (attempt + 1))  # brief backoff before retrying

    _set_cached("geocode", location, "NONE")
    return None


def get_open_meteo_weather(location: str) -> dict:
    """TEMPORARY stand-in for IMD while waiting on API access approval.
    Free, keyless wind/weather forecast via Open-Meteo. Swap back to
    get_imd_weather() once your IMD account/key is ready - just change
    the import in weather_agent.py, nothing else needs to change."""
    cached = _get_cached("open_meteo_weather", location)
    if cached:
        return cached

    coords = _geocode(location)
    if not coords:
        data = {"error": "location_not_found", "note": f"Could not geocode '{location}'."}
        _set_cached("open_meteo_weather", location, data)
        return data

    lat, lon, resolved_name = coords
    try:
        resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "hourly": "wind_speed_10m,wind_direction_10m,precipitation",
                "daily": "wind_speed_10m_max,precipitation_probability_max",
                "timezone": "auto",
                "forecast_days": 3,
            },
            timeout=10,
        )
        data = resp.json()
        data["resolved_location"] = resolved_name
        data["source"] = "Open-Meteo (temporary stand-in for IMD)"
    except Exception as e:
        data = {"error": str(e)}

    _set_cached("open_meteo_weather", location, data)
    return data


def get_open_meteo_marine(location: str) -> dict:
    """TEMPORARY stand-in for INCOIS while waiting on IMD/INCOIS access.
    Free, keyless wave/marine forecast via Open-Meteo's Marine API.
    Swap back to get_incois_pfz() later if you still want PFZ-specific
    fishing zone data - Open-Meteo doesn't provide that, only sea state."""
    cached = _get_cached("open_meteo_marine", location)
    if cached:
        return cached

    coords = _geocode(location)
    if not coords:
        data = {"error": "location_not_found", "note": f"Could not geocode '{location}'."}
        _set_cached("open_meteo_marine", location, data)
        return data

    lat, lon, resolved_name = coords
    try:
        resp = requests.get(
            "https://marine-api.open-meteo.com/v1/marine",
            params={
                "latitude": lat,
                "longitude": lon,
                "hourly": "wave_height,wave_direction,wave_period",
                "timezone": "auto",
                "forecast_days": 3,
            },
            timeout=10,
        )
        data = resp.json()
        data["resolved_location"] = resolved_name
        data["source"] = "Open-Meteo Marine (temporary stand-in for INCOIS)"
    except Exception as e:
        data = {"error": str(e)}

    _set_cached("open_meteo_marine", location, data)
    return data


def get_imd_weather(location: str) -> dict:
    """Fetch sea area + coastal bulletins relevant to a location (city or
    state name - cities are translated to their state/region automatically)."""
    cached = _get_cached("imd_filtered", location)
    if cached:
        return cached

    keyword = _to_state_keyword(location)

    all_sea = _fetch_all_sea_bulletins()
    all_coastal = _fetch_all_coastal_bulletins()

    matched_sea = _filter_by_layer(all_sea, keyword)
    matched_coastal = _filter_by_layer(all_coastal, keyword)

    result = {
        "matched_keyword": keyword,
        "sea_bulletins": matched_sea if matched_sea else "no match",
        "coastal_bulletins": matched_coastal if matched_coastal else "no match",
    }
    if not matched_sea and not matched_coastal:
        result["note"] = f"No bulletins matched keyword '{keyword}'."

    _set_cached("imd_filtered", location, result)
    return result


def _fetch_one_sector(session, secid: str):
    """Fetch and parse the PFZ table for a single secid, using the given
    session (which must already have cookies from a prior request to
    this domain, or will get them from the first call here).

    Adds Referer and X-Requested-With headers - a real browser sends
    these automatically for this kind of AJAX call (the page's own
    formatter() JS function fires an XMLHttpRequest), and INCOIS's
    server may be checking for them before returning real data."""
    from bs4 import BeautifulSoup

    referer_url = f"https://incois.gov.in/MarineFisheries/TextData?secid={secid}"
    ajax_headers = {"Referer": referer_url, "X-Requested-With": "XMLHttpRequest"}

    session.get(
        "https://incois.gov.in/MarineFisheries/TextData",
        params={"secid": secid},
        headers=ajax_headers,
        timeout=15,
    )
    resp = session.get(
        "https://incois.gov.in/MarineFisheries/formattedForecast.action",
        params={"distanceformat": "km", "depthformat": "metre", "latlongformat": "dms"},
        headers=ajax_headers,
        timeout=15,
    )

    # Debug visibility: what did we actually get back? Printed only when
    # parsing fails, so normal successful runs stay quiet.
    soup = BeautifulSoup(resp.text, "html.parser")
    rows = []
    table = soup.find("table")
    if table:
        trs = table.find_all("tr")
        headers = [th.get_text(strip=True) for th in trs[0].find_all("th")] if trs else []
        for tr in trs[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if cells and headers and len(cells) == len(headers):
                rows.append(dict(zip(headers, cells)))

    if not rows:
        print(f"[_fetch_one_sector debug] secid={secid} status={resp.status_code} "
              f"response_length={len(resp.text)} table_found={table is not None}")
        print(f"[_fetch_one_sector debug] first 500 chars of response:\n{resp.text[:500]}")

    return rows


def get_incois_pfz(location: str) -> dict:
    """Real INCOIS PFZ scraper using the confirmed session-based flow:
    1. GET TextData?secid=SEC0XX to set the sector in session
    2. GET formattedForecast.action on the SAME session to get the table
    3. Parse the table rows with BeautifulSoup
    States split into North/South sectors (Tamil Nadu, Andhra Pradesh)
    fetch both and combine.
    """
    keyword = _to_state_keyword(location)
    secids = SECID_MAP.get(keyword)

    if not secids:
        return {
            "sector_keyword": keyword,
            "note": f"No secid mapped for '{keyword}' yet. Add it to SECID_MAP in data_layer.py.",
        }

    cached = _get_cached("incois", keyword)
    if cached:
        return cached

    try:
        session = requests.Session()
        session.headers.update({"User-Agent": "Mozilla/5.0 (ORCA fisherman assistant)"})

        all_rows = []
        for secid in secids:
            rows = _fetch_one_sector(session, secid)
            for r in rows:
                r["_secid"] = secid
            all_rows.extend(rows)

        data = {"sector": keyword, "secids": secids, "landing_points": all_rows} if all_rows else {
            "sector": keyword,
            "secids": secids,
            "note": "No table rows parsed - INCOIS's page structure may have changed, or this sector has no current advisory.",
        }
    except Exception as e:
        data = {"error": str(e), "note": "INCOIS scrape failed."}

    _set_cached("incois", keyword, data)
    return data


def get_mosdac_eo(location: str) -> dict:
    """MOSDAC (ISRO) - mostly per-product download links, some needing a
    free account login. Treat as optional/future work."""
    return {
        "note": (
            "MOSDAC does not offer a simple query API. Free products are "
            "listed at https://www.mosdac.gov.in/open-data with per-product "
            "download links; some require a free MOSDAC account."
        )
    }


def get_gis_boundaries(location: str) -> dict:
    """Real maritime boundary check: geocodes the location, then checks its
    distance to India's international maritime boundary lines with Pakistan
    and Sri Lanka - the two boundaries Indian fishermen most commonly and
    dangerously drift across. Source: VLIZ Marine Regions (marineregions.org),
    a free, citable, academically-maintained maritime boundaries database
    (CC-BY 4.0). line_id 3556 = India-Pakistan, line_ids 1306 and 1311 =
    India-Sri Lanka (two treaty segments, Gulf of Mannar + Bay of Bengal)."""
    import math

    coords = _geocode(location)
    if not coords:
        return {"error": "location_not_found", "note": f"Could not geocode '{location}'."}
    lat, lon, resolved_name = coords

    boundary_line_ids = {
        "India-Pakistan maritime boundary": [3556],
        "India-Sri Lanka maritime boundary": [1306, 1311],
    }

    def fetch_boundary_points(line_id: int):
        cache_key = f"boundary_{line_id}"
        cached = _get_cached("boundary", cache_key)
        if cached:
            return cached
        try:
            resp = requests.get(
                "https://geo.vliz.be/geoserver/wfs",
                params={
                    "request": "getfeature",
                    "service": "wfs",
                    "version": "1.1.0",
                    "typename": "MarineRegions:eez_boundaries",
                    "outputFormat": "application/json",
                    "filter": (
                        f"<Filter><PropertyIsEqualTo>"
                        f"<PropertyName>line_id</PropertyName>"
                        f"<Literal>{line_id}</Literal>"
                        f"</PropertyIsEqualTo></Filter>"
                    ),
                },
                timeout=20,
            )
            geojson = resp.json()
            points = []
            for feature in geojson.get("features", []):
                geom = feature.get("geometry", {})
                coords_list = geom.get("coordinates", [])
                # MultiLineString: list of lines, each a list of [lon, lat] points
                for line in coords_list:
                    points.extend(line)
            _set_cached("boundary", cache_key, points)
            return points
        except Exception:
            return []

    def haversine_km(lat1, lon1, lat2, lon2):
        R = 6371.0
        p1, p2 = math.radians(lat1), math.radians(lat2)
        dp = math.radians(lat2 - lat1)
        dl = math.radians(lon2 - lon1)
        a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
        return 2 * R * math.asin(math.sqrt(a))

    WARNING_THRESHOLD_KM = 30  # flag if within this distance of the line

    results = {"resolved_location": resolved_name, "boundaries_checked": []}
    for boundary_name, line_ids in boundary_line_ids.items():
        all_points = []
        for lid in line_ids:
            all_points.extend(fetch_boundary_points(lid))

        if not all_points:
            results["boundaries_checked"].append({
                "boundary": boundary_name,
                "note": "Could not fetch boundary line data.",
            })
            continue

        min_dist = min(haversine_km(lat, lon, p[1], p[0]) for p in all_points)
        results["boundaries_checked"].append({
            "boundary": boundary_name,
            "distance_km": round(min_dist, 1),
            "warning": min_dist <= WARNING_THRESHOLD_KM,
        })

    results["source"] = "VLIZ Marine Regions (marineregions.org), CC-BY 4.0"
    return results
