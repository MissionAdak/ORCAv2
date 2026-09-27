"""Nearest rescue facility service for ORCA GIS/SAR."""

from math import radians, sin, cos, sqrt, atan2


# Sample rescue facilities for the ORCA prototype.
# These can later be replaced with real OSM/official facility data.
RESCUE_FACILITIES = [
    {
        "name": "Mumbai Coastal Rescue Station",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "type": "Coast Guard / Rescue",
    },
    {
        "name": "Mumbai Port Rescue Facility",
        "latitude": 18.9500,
        "longitude": 72.8400,
        "type": "Marine Rescue",
    },
    {
        "name": "Juhu Coastal Rescue Point",
        "latitude": 19.0988,
        "longitude": 72.8260,
        "type": "Coastal Rescue",
    },
]


def calculate_distance_km(lat1, lon1, lat2, lon2):
    """Calculate distance between two coordinates using Haversine formula."""

    earth_radius_km = 6371.0

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1_rad)
        * cos(lat2_rad)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return earth_radius_km * c


def find_nearest_rescue_facility(latitude, longitude):
    """Find the nearest rescue facility to a given coordinate."""

    nearest = None
    shortest_distance = float("inf")

    for facility in RESCUE_FACILITIES:

        distance = calculate_distance_km(
            latitude,
            longitude,
            facility["latitude"],
            facility["longitude"],
        )

        if distance < shortest_distance:
            shortest_distance = distance
            nearest = facility.copy()

    return {
        "facility": nearest,
        "distance_km": round(shortest_distance, 2),
    }