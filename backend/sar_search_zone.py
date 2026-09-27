"""SAR search-zone generation for ORCA."""

from shapely.geometry import Point
import math


def create_search_zone(latitude, longitude, radius_km):
    """
    Create an approximate circular SAR search zone.

    Risk assessment is handled separately by the ORCA
    Environmental Risk Engine in risk_engine.py.
    """

    latitude_km = 111.0

    longitude_km = 111.0 * math.cos(
        math.radians(latitude)
    )

    # Prevent division by zero near the poles
    if abs(longitude_km) < 0.000001:
        longitude_km = 0.000001

    radius_lat = radius_km / latitude_km
    radius_lon = radius_km / longitude_km

    point = Point(longitude, latitude)

    zone = Point(
        point.x / radius_lon,
        point.y / radius_lat,
    ).buffer(1.0, resolution=32)

    coordinates = [
        [
            (
                round(x * radius_lon, 6),
                round(y * radius_lat, 6),
            )
            for x, y in zone.exterior.coords
        ]
    ]

    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": coordinates,
        },
        "properties": {
            "radius_km": radius_km,
        },
    }