"""
Data Integration Layer
-----------------------
One wrapper function per external source (IMD, INCOIS, MOSDAC, GIS).
Each checks a local SQLite cache first before hitting the real endpoint.

IMD: Real, free, no-key public JSON API. Endpoints below are correct as
of the IMD API reference (https://api.imd.gov.in/public/api_reference.html).
You DO need the right numeric/code `id` for your target sea area, coast,
or port - IMD's IDs aren't plain city names. See LOCATION_ID_MAP below;
you'll need to fill in the correct ids for the regions you care about by
checking IMD's visualize pages (e.g. https://mausam.imd.gov.in/responsive/
marine_forecast.php) and reading the id parameter from the network request
that page makes in your browser's dev tools (F12 -> Network tab).

INCOIS: No clean JSON API for PFZ advisories - they're published as
text/HTML bulletins. This uses a basic scraper as a starting point;
you'll likely need to adjust the parsing once you inspect the actual
page structure for your region.

MOSDAC: Mostly per-product download links, some requiring a free account.
Left as a placeholder - practically, INCOIS's PFZ bulletin is the more
usable ocean-conditions source for this kind of assistant.
"""

import sqlite3
import json
import time
import requests

DB_PATH = "orca_cache.db"
CACHE_TTL_SECONDS = 60 * 30  # 30 minutes - tune as needed

# Fill these in with real IMD ids for the regions you care about.
# Find them by opening https://mausam.imd.gov.in/responsive/marine_forecast.php
# (or coastal_forecast.php / port-warning.php), selecting your region, and
# reading the `id` param IMD's own frontend sends (browser dev tools -> Network).
LOCATION_ID_MAP = {
    # "kochi": {"seabulletin_id": "REPLACE_ME", "coastal_id": "REPLACE_ME", "port_id": "REPLACE_ME"},
    # "chennai": {"seabulletin_id": "REPLACE_ME", "coastal_id": "REPLACE_ME", "port_id": "REPLACE_ME"},
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


def _set_cached(source: str, key: str, payload: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO cache (source, key, payload, fetched_at) VALUES (?, ?, ?, ?)",
        (source, key, json.dumps(payload), time.time()),
    )
    conn.commit()
    conn.close()


_init_db()


def get_imd_weather(location: str) -> dict:
    """Fetch sea area + coastal bulletin from IMD for a location."""
    cached = _get_cached("imd", location)
    if cached:
        return cached

    ids = LOCATION_ID_MAP.get(location.lower())
    if not ids:
        data = {
            "error": "no_id_mapped",
            "note": f"No IMD id configured for '{location}' yet. Add it to LOCATION_ID_MAP in data_layer.py.",
        }
        _set_cached("imd", location, data)
        return data

    result = {}
    try:
        sea = requests.get(
            "https://api.imd.gov.in/api/v1/seabulletin",
            params={"id": ids.get("seabulletin_id")},
            timeout=10,
        )
        result["sea_bulletin"] = sea.json()
    except Exception as e:
        result["sea_bulletin_error"] = str(e)

    try:
        coastal = requests.get(
            "https://api.imd.gov.in/api/v1/coastalbulletin",
            timeout=10,
        )
        result["coastal_bulletin"] = coastal.json()
    except Exception as e:
        result["coastal_bulletin_error"] = str(e)

    try:
        port = requests.get(
            "https://api.imd.gov.in/api/v1/portwarning",
            params={"id": ids.get("port_id")},
            timeout=10,
        )
        result["port_warning"] = port.json()
    except Exception as e:
        result["port_warning_error"] = str(e)

    _set_cached("imd", location, result)
    return result


def get_incois_pfz(location: str) -> dict:
    """Scrape INCOIS's Potential Fishing Zone text bulletin.
    This is a starting-point scraper - inspect the actual page HTML for
    your region and adjust the parsing (BeautifulSoup selectors) to match."""
    cached = _get_cached("incois", location)
    if cached:
        return cached

    try:
        from bs4 import BeautifulSoup  # pip install beautifulsoup4

        resp = requests.get(
            "https://incois.gov.in/MarineFisheries/TextDataHome",
            params={"mfid": 1, "request_locale": "en"},
            timeout=10,
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        # PLACEHOLDER PARSING - inspect the real page structure and replace
        # this with the actual selector for the advisory text/table you need.
        text_content = soup.get_text(separator=" ", strip=True)
        data = {"raw_text_snippet": text_content[:2000], "note": "Adjust the BeautifulSoup selector to target the specific advisory table/text for your region."}
    except Exception as e:
        data = {"error": str(e), "note": "INCOIS scrape failed - check that beautifulsoup4 is installed and the page structure hasn't changed."}

    _set_cached("incois", location, data)
    return data


def get_mosdac_eo(location: str) -> dict:
    """MOSDAC (ISRO) ocean/earth-observation products.
    MOSDAC is mostly per-product download links rather than a query API,
    and some products need a free account login. For a lightweight
    assistant, INCOIS's PFZ bulletin (above) is the more practical source -
    treat this as optional/future work."""
    cached = _get_cached("mosdac", location)
    if cached:
        return cached

    data = {
        "note": (
            "MOSDAC does not offer a simple query API. Free products are "
            "listed at https://www.mosdac.gov.in/open-data with per-product "
            "download links; some require a free MOSDAC account. Consider "
            "skipping this source initially and relying on IMD + INCOIS."
        )
    }
    _set_cached("mosdac", location, data)
    return data


def get_gis_boundaries(location: str) -> dict:
    """Fetch GIS boundary/geofencing data for a location."""
    cached = _get_cached("gis", location)
    if cached:
        return cached

    # For real geofencing, load a local shapefile/GeoJSON with geopandas
    # instead of hitting a remote endpoint - maritime boundary data is
    # typically static. India's EEZ/maritime boundary shapefiles are
    # available from public GIS data portals (e.g. Bhuvan, marineregions.org).
    data = {"note": "Load boundary polygons locally via geopandas.read_file('boundaries.geojson')"}

    _set_cached("gis", location, data)
    return data
