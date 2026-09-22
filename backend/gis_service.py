"""Deterministic GIS services for ORCA."""

import math
import geopandas as gpd
from shapely.geometry import Point, shape


EEZ_FILE = "india_eez.geojson"


def distance_and_bearing(lat1, lon1, lat2, lon2):
    """Return deterministic great-circle distance in km and initial bearing."""

    earth_radius_km = 6371.0088

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(delta_lambda / 2) ** 2
    )

    distance_km = 2 * earth_radius_km * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a),
    )

    y = math.sin(delta_lambda) * math.cos(phi2)

    x = (
        math.cos(phi1) * math.sin(phi2)
        - math.sin(phi1)
        * math.cos(phi2)
        * math.cos(delta_lambda)
    )

    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360

    return {
        "distance_km": round(distance_km, 3),
        "bearing_degrees": round(bearing, 2),
    }


def point_in_eez(latitude, longitude):
    """Check whether a coordinate falls inside India's EEZ geometry."""

    eez = gpd.read_file(EEZ_FILE).to_crs("EPSG:4326")

    point = Point(longitude, latitude)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "inside_eez": bool(eez.contains(point).any()),
    }


def geometry_intersection(geojson_a, geojson_b):
    """Return whether two GeoJSON geometries intersect."""

    geometry_a = shape(geojson_a)
    geometry_b = shape(geojson_b)

    intersection = geometry_a.intersection(geometry_b)

    return {
        "intersects": bool(geometry_a.intersects(geometry_b)),
        "intersection_geometry": intersection.__geo_interface__,
    }


def _normalize_geometry(geometry):
    """
    Convert either a GeoJSON Geometry or GeoJSON Feature
    into a GeoJSON Geometry dictionary.
    """

    if not isinstance(geometry, dict):
        raise ValueError("Geometry must be a JSON object.")

    geometry_type = geometry.get("type")

    if geometry_type == "Feature":
        geometry = geometry.get("geometry")

        if geometry is None:
            raise ValueError("GeoJSON Feature does not contain geometry.")

    if not isinstance(geometry, dict):
        raise ValueError("Invalid GeoJSON geometry.")

    if "type" not in geometry:
        raise ValueError("GeoJSON geometry must contain 'type'.")

    if "coordinates" not in geometry:
        raise ValueError("GeoJSON geometry must contain 'coordinates'.")

    return geometry


def hazard_zone_intersection(hazard_geometry, restricted_geometry):
    """
    Check whether a hazard geometry intersects a restricted zone.

    Supports both:
    - GeoJSON Geometry
    - GeoJSON Feature

    Returns deterministic geometric intersection information.
    """

    hazard_geometry = _normalize_geometry(hazard_geometry)
    restricted_geometry = _normalize_geometry(restricted_geometry)

    hazard = shape(hazard_geometry)
    restricted = shape(restricted_geometry)

    intersects = bool(hazard.intersects(restricted))

    intersection = hazard.intersection(restricted)

    return {
        "hazard_intersects_restricted": intersects,
        "intersection_geometry": intersection.__geo_interface__,
    }


def point_in_geofence(latitude, longitude, geofence_geometry):
    """Check whether a coordinate is inside a supplied geofence."""

    geofence_geometry = _normalize_geometry(geofence_geometry)

    geofence = shape(geofence_geometry)

    point = Point(longitude, latitude)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "inside_geofence": bool(geofence.contains(point)),
    }


def create_route_geometry(lat1, lon1, lat2, lon2):
    """Create deterministic straight-line GeoJSON route geometry."""

    return {
        "type": "LineString",
        "coordinates": [
            [lon1, lat1],
            [lon2, lat2],
        ],
    }