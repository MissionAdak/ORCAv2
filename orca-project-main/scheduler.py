"""
Data Polling Scheduler
------------------------
Runs continuously, polling wind + wave data for a fixed list of monitored
locations every 3 minutes and storing it in the database for the trend
dashboard. Deliberately does NOT call the LLM here - this is meant to run
24/7 in the background, and hitting a local Ollama model every 3 minutes
for multiple locations would be a heavy, mostly-pointless CPU load (raw
numbers don't need an LLM to be worth graphing).

Run this in its own terminal window, separate from orchestrator.py:
    python scheduler.py

Leave it running while you use the dashboard (dashboard.py) to watch
trends build up over time.
"""

import time
from datetime import datetime

from data_layer import get_open_meteo_weather, get_open_meteo_marine
import db
import push_to_backend

# Add/remove locations here - these are the ones the dashboard will have
# trend data for. Keep this list short-ish; each one is a couple of API
# calls per poll.
MONITORED_LOCATIONS = [
    "Kochi", "Chennai", "Mumbai", "Visakhapatnam", "Mangalore",
    "Goa", "Kolkata", "Puri", "Surat", "Port Blair",
]

POLL_INTERVAL_SECONDS = 3 * 60  # 3 minutes


def _extract_current_value(hourly_block: dict, field: str):
    """Pulls the first (current) hourly value for a field, if present."""
    try:
        return hourly_block["hourly"][field][0]
    except (KeyError, IndexError, TypeError):
        return None


def poll_once():
    for location in MONITORED_LOCATIONS:
        weather = get_open_meteo_weather(location)
        marine = get_open_meteo_marine(location)

        wind_speed = _extract_current_value(weather, "wind_speed_10m")
        rain_chance = None
        try:
            rain_chance = weather.get("daily", {}).get("precipitation_probability_max", [None])[0]
        except (AttributeError, IndexError):
            pass

        wave_height = _extract_current_value(marine, "wave_height")
        wave_period = _extract_current_value(marine, "wave_period")

        db.log_reading(location, wind_speed, wave_height, wave_period, rain_chance)
        push_to_backend.push_reading(location, wind_speed, wave_height, wave_period, rain_chance)

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Polled {len(MONITORED_LOCATIONS)} locations.")


if __name__ == "__main__":
    print(f"Starting data poller - checking {len(MONITORED_LOCATIONS)} locations every "
          f"{POLL_INTERVAL_SECONDS // 60} minutes. Press Ctrl+C to stop.\n")
    while True:
        try:
            poll_once()
        except Exception as e:
            print(f"Poll failed: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)
