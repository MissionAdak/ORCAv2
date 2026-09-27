"""PFZ (Potential Fishing Zone) Agent - offline dataset, no LLM call, no
live network dependency.

Uses a static local dataset (pfz_offline_dataset.json) containing REAL
data we captured directly from INCOIS's live PFZ page earlier (Andaman
sector - a genuine government dataset, not fabricated). We switched to
this after repeated, unpredictable live-source failures (INCOIS's legacy
server session/500 errors, satellite chlorophyll blocked by monsoon
cloud cover) made live PFZ data too unreliable for demo purposes.

Honesty note: this is real data, but it's a historical snapshot from one
specific sector (Andaman), not live, and not necessarily geographically
matched to every query location. It's clearly labeled as such via
"is_live": False and "source" in the output, so nothing downstream
mistakes it for a real-time, location-specific reading.
"""

import json
import os

_DATASET_PATH = os.path.join(os.path.dirname(__file__), "pfz_offline_dataset.json")
_cached_dataset = None


def _load_dataset():
    global _cached_dataset
    if _cached_dataset is None:
        with open(_DATASET_PATH, "r") as f:
            _cached_dataset = json.load(f)
    return _cached_dataset


def _parse_distance_km(distance_range: str):
    try:
        parts = distance_range.split("-")
        nums = [float(p) for p in parts]
        return sum(nums) / len(nums)
    except (ValueError, AttributeError):
        return None


def pfz_agent(state: dict) -> dict:
    location = state.get("location", "unspecified location")

    all_zones = _load_dataset()
    ranked = sorted(all_zones, key=lambda z: _parse_distance_km(z["distance_km_range"]) or 9999)
    top_zones = ranked[:5]

    return {
        "pfz_data": {
            "available": True,
            "is_live": False,
            "source": "Cached INCOIS dataset (Andaman sector snapshot, captured earlier - not live, not location-specific)",
            "top_zones": top_zones,
            "total_zones_found": len(all_zones),
            "note": (
                f"This is a real government dataset captured earlier, not a live "
                f"reading for '{location}' specifically. Live INCOIS/satellite "
                f"sourcing was unreliable during testing (server errors, cloud "
                f"cover) - swap back to live sourcing once that's resolved."
            ),
        }
    }
