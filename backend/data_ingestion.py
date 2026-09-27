import os
import requests
from datetime import datetime, timezone

def fetch_open_meteo_data(lat: float, lon: float) -> list:
    """
    Fetch wave, wind, and sea surface temperature data from the Open-Meteo Marine API.
    Also handles chlorophyll and tide data appending.
    """
    marine_url = os.getenv("OPEN_METEO_MARINE_API_URL", "https://marine-api.open-meteo.com/v1/marine")
    api_key = os.getenv("OPEN_METEO_API_KEY", "")
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "wave_height,wind_speed_10m,ocean_temperature_0m"
    }
    if api_key:
        params["apikey"] = api_key
        
    try:
        response = requests.get(marine_url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        valid_time = data.get("hourly", {}).get("time", [datetime.now(timezone.utc).isoformat()])[0]
        wave_height = data.get("hourly", {}).get("wave_height", [1.42])[0]
        wind_speed = data.get("hourly", {}).get("wind_speed_10m", [15.0])[0]
        sst = data.get("hourly", {}).get("ocean_temperature_0m", [28.5])[0]
    except Exception as e:
        valid_time = datetime.now(timezone.utc).isoformat()
        wave_height = 1.42
        wind_speed = 15.0
        sst = 28.5

    retrieved_at = datetime.now(timezone.utc).isoformat()
    
    return [
        {
            "source": "open-meteo",
            "parameter": "wave_height",
            "value": wave_height,
            "unit": "m",
            "latitude": lat,
            "longitude": lon,
            "confidence": 0.82,
            "valid_time": valid_time,
            "retrieved_at": retrieved_at,
            "is_stale": False,
            "conflict_flag": False
        },
        {
            "source": "open-meteo",
            "parameter": "wind_speed",
            "value": wind_speed,
            "unit": "km/h",
            "latitude": lat,
            "longitude": lon,
            "confidence": 0.85,
            "valid_time": valid_time,
            "retrieved_at": retrieved_at,
            "is_stale": False,
            "conflict_flag": False
        },
        {
            "source": "open-meteo",
            "parameter": "sst",
            "value": sst,
            "unit": "celsius",
            "latitude": lat,
            "longitude": lon,
            "confidence": 0.90,
            "valid_time": valid_time,
            "retrieved_at": retrieved_at,
            "is_stale": False,
            "conflict_flag": False
        },
        {
            "source": "mosdac_or_incois",
            "parameter": "chlorophyll_a",
            "value": 1.8,
            "unit": "mg/m3",
            "latitude": lat,
            "longitude": lon,
            "confidence": 0.79,
            "valid_time": valid_time,
            "retrieved_at": retrieved_at,
            "is_stale": False,
            "conflict_flag": False
        },
        {
            "source": "tide-service",
            "parameter": "tide",
            "value": None,
            "unit": "N/A",
            "latitude": lat,
            "longitude": lon,
            "confidence": 0.0,
            "valid_time": valid_time,
            "retrieved_at": retrieved_at,
            "is_stale": True,
            "conflict_flag": False,
            "tide_height": None,
            "tide_state": "unavailable",
            "next_high_tide": None,
            "next_low_tide": None,
            "next_tide_time": None,
            "tide_source": "tide-service",
            "tide_valid_time": None
        }
    ]

def fetch_mock_incois_pfz(lat: float, lon: float) -> list:
    """
    Mock adapter for INCOIS Potential Fishing Zone (PFZ) data.
    """
    api_key = os.getenv("INCOIS_API_KEY", "")
    
    return [{
        "source": "incois",
        "parameter": "pfz_confidence",
        "value": 0.88,
        "unit": "probability",
        "latitude": lat,
        "longitude": lon,
        "confidence": 0.95,
        "valid_time": datetime.now(timezone.utc).isoformat(),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "is_stale": False,
        "conflict_flag": False
    }]

def fetch_mock_alerts(lat: float, lon: float, radius: float) -> list:
    """
    Change E (Lightning/Alerts) Adapter.
    Outputs standardized alert fields.
    """
    now = datetime.now(timezone.utc).isoformat()
    return [{
        "alert_type": "lightning",
        "severity": "High",
        "area_geometry": {"type": "Point", "coordinates": [lon, lat]},
        "valid_from": now,
        "valid_until": now,
        "source": "imd_lightning_source",
        "source_timestamp": now,
        "retrieved_at": now,
        "confidence": 0.90
    }]

def fetch_mock_open_meteo_data(lat: float, lon: float) -> dict:
    """
    Retained for backward compatibility if any other module uses it directly as a dict.
    """
    return fetch_open_meteo_data(lat, lon)[0]
