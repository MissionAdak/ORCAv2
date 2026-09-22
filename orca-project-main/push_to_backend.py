"""
Push helper - sends local results up to the hosted Django backend.
--------------------------------------------------------------------
Set BACKEND_URL below to your deployed Render URL once you have one
(e.g. "https://orca-backend.onrender.com"). Set API_KEY to match the
PUSH_API_KEY you set in Render's environment variables.

All pushes are wrapped in try/except and fail silently (just printing
a warning) so a flaky internet connection or a backend that's still
being set up never breaks your local orchestrator.py or scheduler.py
runs - they keep working locally either way.
"""

import requests

BACKEND_URL = "https://orca-backend-tt39.onrender.com"  # your real deployed Render URL
API_KEY = "5e79092756dc793455487a68e30d88af"  # must match PUSH_API_KEY in Render's environment variables

HEADERS = {"X-API-KEY": API_KEY}


def push_reading(location, wind_speed_kmh, wave_height_m, wave_period_s, rain_chance_pct):
    try:
        requests.post(
            f"{BACKEND_URL}/api/readings/",
            json={
                "location": location,
                "wind_speed_kmh": wind_speed_kmh,
                "wave_height_m": wave_height_m,
                "wave_period_s": wave_period_s,
                "rain_chance_pct": rain_chance_pct,
            },
            headers=HEADERS,
            timeout=10,
        )
    except Exception as e:
        print(f"[push_to_backend] Could not push reading (continuing locally): {e}")


def push_agent_run(query, location, agents_run, verdict, duration_ms, full_response="", pfz_zones=None, route_data=None):
    try:
        requests.post(
            f"{BACKEND_URL}/api/agent-runs/",
            json={
                "query": query,
                "location": location,
                "agents_run": ",".join(agents_run) if isinstance(agents_run, list) else agents_run,
                "verdict": verdict,
                "duration_ms": duration_ms,
                "full_response": full_response,
                "pfz_zones": pfz_zones or [],
                "route_data": route_data or {},
            },
            headers=HEADERS,
            timeout=10,
        )
    except Exception as e:
        print(f"[push_to_backend] Could not push agent run (continuing locally): {e}")
