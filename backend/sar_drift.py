"""Deterministic SAR drift model for ORCA."""

from gis_service import distance_and_bearing


def predict_drift(
    latitude,
    longitude,
    current_speed_knots,
    current_direction_degrees,
    wind_speed_knots,
    wind_direction_degrees,
    hours,
    object_type="drifting_vessel",
):
    """Predict drift position using current, wind and uncertainty."""
    
    leeway_multiplier = 0.03
    if object_type == "person_in_water":
        leeway_multiplier = 0.01
    elif object_type == "life_raft":
        leeway_multiplier = 0.04

    current_distance_km = current_speed_knots * 1.852 * hours
    wind_distance_km = wind_speed_knots * 1.852 * hours * leeway_multiplier

    current_lat = latitude + (
        current_distance_km
        * __import__("math").cos(__import__("math").radians(current_direction_degrees))
        / 111.0
    )

    current_lon = longitude + (
        current_distance_km
        * __import__("math").sin(__import__("math").radians(current_direction_degrees))
        / (111.0 * __import__("math").cos(__import__("math").radians(latitude)))
    )

    wind_lat = (
        wind_distance_km
        * __import__("math").cos(__import__("math").radians(wind_direction_degrees))
        / 111.0
    )

    wind_lon = (
        wind_distance_km
        * __import__("math").sin(__import__("math").radians(wind_direction_degrees))
        / (111.0 * __import__("math").cos(__import__("math").radians(latitude)))
    )

    predicted_latitude = current_lat + wind_lat
    predicted_longitude = current_lon + wind_lon

    uncertainty_km = round(max(1.0, wind_distance_km * 2), 2)

    return {
        "predicted_latitude": round(predicted_latitude, 6),
        "predicted_longitude": round(predicted_longitude, 6),
        "uncertainty_km": uncertainty_km,
    }
