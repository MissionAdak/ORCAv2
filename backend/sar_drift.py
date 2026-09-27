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
):
    """Predict drift position using current, wind and uncertainty."""

    current_distance_km = current_speed_knots * 1.852 * hours
    wind_distance_km = wind_speed_knots * 1.852 * hours * 0.03

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
