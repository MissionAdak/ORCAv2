"""Probabilistic SAR particle drift model for ORCA."""

import math
import random


def simulate_particles(
    latitude,
    longitude,
    current_speed_knots,
    current_direction_degrees,
    wind_speed_knots,
    wind_direction_degrees,
    hours,
    particle_count=500,
):
    """
    Simulate multiple possible SAR drift trajectories.

    This is a probabilistic search-area estimate.
    It does NOT represent an exact survivor location.
    """

    particles = []

    for _ in range(particle_count):

        # Random uncertainty for each particle
        current_variation = random.uniform(-15, 15)
        wind_variation = random.uniform(-20, 20)

        current_direction = (
            current_direction_degrees + current_variation
        )

        wind_direction = (
            wind_direction_degrees + wind_variation
        )

        # Convert knots to km/h
        current_speed_kmh = current_speed_knots * 1.852
        wind_speed_kmh = wind_speed_knots * 1.852

        # Current movement
        current_distance = current_speed_kmh * hours

        current_lat = (
            current_distance
            * math.cos(math.radians(current_direction))
        )

        current_lon = (
            current_distance
            * math.sin(math.radians(current_direction))
        )

        # Wind influence
        wind_distance = wind_speed_kmh * 0.03 * hours

        wind_lat = (
            wind_distance
            * math.cos(math.radians(wind_direction))
        )

        wind_lon = (
            wind_distance
            * math.sin(math.radians(wind_direction))
        )

        # Convert km to degrees
        new_latitude = latitude + (
            (current_lat + wind_lat) / 111.0
        )

        longitude_km = 111.0 * math.cos(
            math.radians(latitude)
        )

        new_longitude = longitude + (
            (current_lon + wind_lon)
            / longitude_km
        )

        particles.append(
            {
                "latitude": round(new_latitude, 6),
                "longitude": round(new_longitude, 6),
            }
        )

    return particles