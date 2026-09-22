"""Deterministic PFZ geometry services for ORCA."""

from shapely.geometry import Point



def create_pfz_zone(latitude, longitude, radius_km):
    """Create an approximate circular PFZ geometry."""

    latitude_km = 111.0
    longitude_km = 111.0

    point = Point(longitude, latitude)

    radius_lat = radius_km / latitude_km
    radius_lon = radius_km / longitude_km

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
            "latitude": latitude,
            "longitude": longitude,
            "radius_km": radius_km,
            "zone_type": "Potential Fishing Zone",
        },
    }