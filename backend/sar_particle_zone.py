"""Create prioritized SAR search zones from particle drift."""

from shapely.geometry import MultiPoint


def create_particle_search_zone(particles):
    """
    Convert SAR particle positions into a probabilistic search area.

    The result is an estimate of where drift particles may concentrate.
    It is NOT an exact survivor location.
    """

    if not particles:
        return {
            "error": "No particles provided"
        }

    points = [
        (
            particle["longitude"],
            particle["latitude"],
        )
        for particle in particles
    ]

    hull = MultiPoint(points).convex_hull

    return {
        "type": "Feature",
        "geometry": hull.__geo_interface__,
        "properties": {
            "particle_count": len(particles),
            "probability": 1.0,
            "risk_score": None,
            "risk_level": None,
            "priority": None,
            "recommended_action": None,
            "estimate_type": "Probabilistic Search-Area Estimate",
            "warning": (
                "This search zone represents possible drift positions "
                "and is not an exact survivor location."
            ),
        },
    }