"""
Data Integration Layer
-----------------------
One wrapper function per external source (IMD, INCOIS, MOSDAC, GIS).
Each checks a local SQLite cache first before hitting the real endpoint.
"""

import sqlite3
import json
import time
import requests
from network_manager import request_with_retry

DB_PATH = "orca_cache.db"
CACHE_TTL_SECONDS = 60 * 30  # 30 minutes


LOCATION_ID_MAP = {
    # Add real IMD ids here when available.
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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS sos_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload TEXT NOT NULL,
            created_at REAL NOT NULL,
            synced INTEGER DEFAULT 0
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


def _get_stale_cached(source: str, key: str):
    """Return the latest cached value even when it has expired."""
    conn = sqlite3.connect(DB_PATH)

    row = conn.execute(
        "SELECT payload, fetched_at FROM cache WHERE source=? AND key=?",
        (source, key),
    ).fetchone()

    conn.close()

    if not row:
        return None

    payload, fetched_at = row

    return {
        "data": json.loads(payload),
        "fetched_at": fetched_at,
        "stale": time.time() - fetched_at >= CACHE_TTL_SECONDS,
    }


def _set_cached(source: str, key: str, payload: dict):
    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        INSERT OR REPLACE INTO cache
        (source, key, payload, fetched_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            source,
            key,
            json.dumps(payload),
            time.time(),
        ),
    )

    conn.commit()
    conn.close()


def get_imd_weather(location: str) -> dict:
    """Fetch sea area + coastal bulletin from IMD."""

    cached = _get_cached("imd", location)

    if cached:
        return {
            "data": cached,
            "cache_status": "fresh",
        }

    ids = LOCATION_ID_MAP.get(location.lower())

    if not ids:
        stale_cached = _get_stale_cached("imd", location)

        if stale_cached:
            return {
                "data": stale_cached["data"],
                "cache_status": "stale",
                "fetched_at": stale_cached["fetched_at"],
            }

        data = {
            "error": "no_id_mapped",
            "note": (
                f"No IMD id configured for '{location}' yet. "
                "Add it to LOCATION_ID_MAP in data_layer.py."
            ),
            "cache_status": "unavailable",
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
        sea.raise_for_status()
        result["sea_bulletin"] = sea.json()

    except Exception as e:
        result["sea_bulletin_error"] = str(e)

    try:
        coastal = requests.get(
            "https://api.imd.gov.in/api/v1/coastalbulletin",
            timeout=10,
        )
        coastal.raise_for_status()
        result["coastal_bulletin"] = coastal.json()

    except Exception as e:
        result["coastal_bulletin_error"] = str(e)

    try:
        port = requests.get(
            "https://api.imd.gov.in/api/v1/portwarning",
            params={"id": ids.get("port_id")},
            timeout=10,
        )
        port.raise_for_status()
        result["port_warning"] = port.json()

    except Exception as e:
        result["port_warning_error"] = str(e)

    _set_cached("imd", location, result)

    return {
        "data": result,
        "cache_status": "fresh",
    }


def get_incois_pfz(location: str) -> dict:
    """Scrape INCOIS Potential Fishing Zone bulletin."""

    cached = _get_cached("incois", location)

    if cached:
        return {
            "data": cached,
            "cache_status": "fresh",
        }

    try:
        from bs4 import BeautifulSoup

        resp = requests.get(
            "https://incois.gov.in/MarineFisheries/TextDataHome",
            params={
                "mfid": 1,
                "request_locale": "en",
            },
            timeout=10,
        )

        resp.raise_for_status()

        soup = BeautifulSoup(
            resp.text,
            "html.parser",
        )

        text_content = soup.get_text(
            separator=" ",
            strip=True,
        )

        data = {
            "raw_text_snippet": text_content[:2000],
            "note": (
                "Adjust the BeautifulSoup selector to target "
                "the specific advisory table/text for your region."
            ),
        }

    except Exception as e:
        stale_cached = _get_stale_cached("incois", location)

        if stale_cached:
            return {
                "data": stale_cached["data"],
                "cache_status": "stale",
                "fetched_at": stale_cached["fetched_at"],
            }

        data = {
            "error": str(e),
            "note": "INCOIS scrape failed.",
            "cache_status": "unavailable",
        }

    _set_cached("incois", location, data)

    return data


def get_mosdac_eo(location: str) -> dict:
    """Return MOSDAC ocean/earth-observation information."""

    cached = _get_cached("mosdac", location)

    if cached:
        return {
            "data": cached,
            "cache_status": "fresh",
        }

    data = {
        "note": (
            "MOSDAC does not offer a simple query API. "
            "Consider relying on IMD + INCOIS initially."
        )
    }

    _set_cached("mosdac", location, data)

    return {
        "data": data,
        "cache_status": "fresh",
    }


def get_gis_boundaries(location: str) -> dict:
    """Load India's EEZ boundary from the local GeoJSON file."""

    cache_key = f"india_eez:{location}"

    cached = _get_cached("gis", cache_key)

    if cached:
        return {
            "data": cached,
            "cache_status": "fresh",
        }

    try:
        import geopandas as gpd

        eez = gpd.read_file(
            "india_eez.geojson"
        ).to_crs("EPSG:4326")

        data = {
            "location": location,
            "boundary_type": "India EEZ",
            "features": len(eez),
            "crs": str(eez.crs),
            "bounds": eez.total_bounds.tolist(),
            "status": "loaded",
        }

    except Exception as e:
        stale_cached = _get_stale_cached("gis", cache_key)

        if stale_cached:
            return {
                "data": stale_cached["data"],
                "cache_status": "stale",
                "fetched_at": stale_cached["fetched_at"],
            }

        data = {
            "location": location,
            "status": "error",
            "error": str(e),
        }

    _set_cached("gis", cache_key, data)

    return data


# -------------------------------------------------------------------
# OFFLINE SOS FALLBACK QUEUE
# -------------------------------------------------------------------

def queue_sos_event(payload: dict) -> int:
    """Store an SOS event locally until it can be synchronized."""

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.execute(
        """
        INSERT INTO sos_queue
        (payload, created_at, synced)
        VALUES (?, ?, 0)
        """,
        (
            json.dumps(payload),
            time.time(),
        ),
    )

    conn.commit()

    event_id = cursor.lastrowid

    conn.close()

    return event_id


def get_unsynced_sos_events() -> list:
    """Return SOS events waiting to be synchronized."""

    conn = sqlite3.connect(DB_PATH)

    rows = conn.execute(
        """
        SELECT id, payload, created_at
        FROM sos_queue
        WHERE synced=0
        ORDER BY id
        """
    ).fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "payload": json.loads(row[1]),
            "created_at": row[2],
        }
        for row in rows
    ]


def mark_sos_event_synced(event_id: int):
    """Mark an SOS event as successfully synchronized."""

    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        "UPDATE sos_queue SET synced=1 WHERE id=?",
        (event_id,),
    )

    conn.commit()
    conn.close()


def sync_sos_events(sync_url: str = "http://127.0.0.1:8000/api/sar/create", timeout: int = 10) -> dict:
    """Send queued offline SOS events to the SAR backend."""
    pending_events = get_unsynced_sos_events()

    if not pending_events:
        return {
            "success": True,
            "synced": 0,
            "remaining": 0,
        }

    synced_count = 0

    for event in pending_events:
        try:
            response = request_with_retry(
                "POST",
                sync_url,
                timeout=timeout,
                json=event["payload"],
            )

            if response.ok:
                mark_sos_event_synced(event["id"])
                synced_count += 1

        except requests.RequestException:
            # Keep the event queued if the backend is unavailable.
            break

    remaining = len(get_unsynced_sos_events())

    return {
        "success": remaining == 0,
        "synced": synced_count,
        "remaining": remaining,
    }