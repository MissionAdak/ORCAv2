"""
Database layer for ORCA's monitoring dashboard.
--------------------------------------------------
Two tables in the same SQLite file already used for caching:

`readings`   - raw wind/wave numbers polled periodically (no LLM involved),
               used to power the trend charts (day/week/month/year).

`agent_runs` - one row per actual orchestrator invocation (i.e. every time
               someone runs a real query through the LLM pipeline), used
               to power the "agent usage" view - which agents ran, what
               verdict came out, how long it took.
"""

import sqlite3
import time
from datetime import datetime

DB_PATH = "orca_cache.db"  # same file as data_layer.py's cache - one DB for the project


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            location TEXT,
            wind_speed_kmh REAL,
            wave_height_m REAL,
            wave_period_s REAL,
            rain_chance_pct REAL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            query TEXT,
            location TEXT,
            agents_run TEXT,
            verdict TEXT,
            duration_ms REAL
        )
    """)
    conn.commit()
    conn.close()


def log_reading(location: str, wind_speed_kmh, wave_height_m, wave_period_s, rain_chance_pct):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO readings (timestamp, location, wind_speed_kmh, wave_height_m, wave_period_s, rain_chance_pct) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (time.time(), location, wind_speed_kmh, wave_height_m, wave_period_s, rain_chance_pct),
    )
    conn.commit()
    conn.close()


def log_agent_run(query: str, location: str, agents_run: list, verdict: str, duration_ms: float):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO agent_runs (timestamp, query, location, agents_run, verdict, duration_ms) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (time.time(), query, location, ",".join(agents_run), verdict, duration_ms),
    )
    conn.commit()
    conn.close()


def get_readings(location: str = None, since_ts: float = None):
    """Returns a list of dict rows. Filters are optional."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    query = "SELECT * FROM readings WHERE 1=1"
    params = []
    if location:
        query += " AND location = ?"
        params.append(location)
    if since_ts:
        query += " AND timestamp >= ?"
        params.append(since_ts)
    query += " ORDER BY timestamp ASC"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_agent_runs(limit: int = 200):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM agent_runs ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_distinct_locations():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT DISTINCT location FROM readings").fetchall()
    conn.close()
    return [r[0] for r in rows]


init_db()
