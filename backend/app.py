from fastapi import APIRouter
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import sqlite3
import json
from datetime import datetime, timezone

from risk_engine import calculate_risk_score

from gis_service import (
    distance_and_bearing,
    geometry_intersection,
    point_in_eez,
    hazard_zone_intersection,
    point_in_geofence,
    create_route_geometry,
)

from sar_drift import predict_drift
from sar_search_zone import create_search_zone
from sar_particle_model import simulate_particles
from sar_particle_zone import create_particle_search_zone
from pfz_service import create_pfz_zone
from rescue_service import find_nearest_rescue_facility


app = APIRouter()


# ============================================================
# Database Helpers
# ============================================================

def get_connection():
    """Create a connection to the ORCA SQLite database."""
    return sqlite3.connect("orca_cache.db")


def ensure_sar_evidence_metadata():
    """
    Add SAR evidence metadata columns if they do not already exist.

    This keeps existing evidence records safe while allowing the
    new source timestamp and confidence fields.
    """

    conn = get_connection()

    columns = conn.execute(
        "PRAGMA table_info(sar_evidence)"
    ).fetchall()

    existing_columns = {
        column[1]
        for column in columns
    }

    if "source_timestamp" not in existing_columns:
        conn.execute(
            """
            ALTER TABLE sar_evidence
            ADD COLUMN source_timestamp TEXT
            """
        )

    if "confidence" not in existing_columns:
        conn.execute(
            """
            ALTER TABLE sar_evidence
            ADD COLUMN confidence REAL
            """
        )

    conn.commit()
    conn.close()


@app.on_event("startup")
def startup_database_setup():
    """Prepare database metadata required by the SAR evidence system."""
    ensure_sar_evidence_metadata()


# ============================================================
# Request Models
# ============================================================

class DistanceRequest(BaseModel):
    lat1: float
    lon1: float
    lat2: float
    lon2: float


class IntersectionRequest(BaseModel):
    geometry_a: dict
    geometry_b: dict


class HazardZoneRequest(BaseModel):
    hazard_geometry: dict
    restricted_geometry: dict


class GeofenceRequest(BaseModel):
    latitude: float
    longitude: float
    geofence_geometry: dict


class SARCreateRequest(BaseModel):
    last_known_lat: float
    last_known_lon: float
    object_type: str
    people_count: int


class PFZRequest(BaseModel):
    latitude: float
    longitude: float
    radius_km: float = 5.0


class SARDiftRequest(BaseModel):
    incident_id: int
    current_speed_knots: float
    current_direction_degrees: float
    wind_speed_knots: float
    wind_direction_degrees: float
    hours: float


class SARLocationRequest(BaseModel):
    incident_id: int
    latitude: float
    longitude: float


class SAREvidenceRequest(BaseModel):
    incident_id: int
    evidence_type: str
    description: str
    source: str
    source_timestamp: str | None = None
    confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
    )


class RiskRequest(BaseModel):
    wave_score: float
    wind_score: float
    weather_score: float
    current_score: float
    geofence_score: float
    alert_score: float


class SARParticleRequest(BaseModel):
    incident_id: int
    current_speed_knots: float
    current_direction_degrees: float
    wind_speed_knots: float
    wind_direction_degrees: float
    hours: float
    particle_count: int = 500


class RescueRouteHazardRequest(BaseModel):
    incident_id: int
    hazard_geometry: dict
    restricted_geometry: dict


# ============================================================
# GIS Endpoints
# ============================================================

@app.post("/api/geospatial/distance")
def calculate_distance(request: DistanceRequest):

    return distance_and_bearing(
        request.lat1,
        request.lon1,
        request.lat2,
        request.lon2,
    )


@app.post("/api/geospatial/intersection")
def calculate_intersection(request: IntersectionRequest):

    return geometry_intersection(
        request.geometry_a,
        request.geometry_b,
    )


@app.post("/api/geospatial/hazard-intersection")
def calculate_hazard_intersection(request: HazardZoneRequest):

    return hazard_zone_intersection(
        request.hazard_geometry,
        request.restricted_geometry,
    )


@app.post("/api/geospatial/geofence")
def check_geofence(request: GeofenceRequest):

    return point_in_geofence(
        request.latitude,
        request.longitude,
        request.geofence_geometry,
    )


@app.post("/api/geospatial/eez")
def check_eez(request: SARCreateRequest):

    return point_in_eez(
        request.last_known_lat,
        request.last_known_lon,
    )


@app.post("/api/geospatial/pfz")
def create_pfz(request: PFZRequest):

    return create_pfz_zone(
        request.latitude,
        request.longitude,
        request.radius_km,
    )


# ============================================================
# Route Analysis
# ============================================================

@app.post("/api/route/analyze")
def analyze_route(request: DistanceRequest):

    result = distance_and_bearing(
        request.lat1,
        request.lon1,
        request.lat2,
        request.lon2,
    )

    route_geometry = create_route_geometry(
        request.lat1,
        request.lon1,
        request.lat2,
        request.lon2,
    )

    return {
        "route": {
            "start": {
                "latitude": request.lat1,
                "longitude": request.lon1,
            },
            "end": {
                "latitude": request.lat2,
                "longitude": request.lon2,
            },
        },
        "route_geometry": route_geometry,
        "distance_km": result["distance_km"],
        "bearing_degrees": result["bearing_degrees"],
        "status": "route analyzed",
    }


# ============================================================
# SAR Incident
# ============================================================

@app.post("/api/sar/create")
def create_sar_incident(request: SARCreateRequest):

    conn = get_connection()

    cursor = conn.execute(
        """
        INSERT INTO sar_incidents
        (
            status,
            last_known_latitude,
            last_known_longitude,
            object_type,
            people_count
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            "active",
            request.last_known_lat,
            request.last_known_lon,
            request.object_type,
            request.people_count,
        ),
    )

    incident_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "incident_id": incident_id,
        "status": "active",
        "last_known_latitude": request.last_known_lat,
        "last_known_longitude": request.last_known_lon,
        "object_type": request.object_type,
        "people_count": request.people_count,
    }


# ============================================================
# SAR Drift Prediction
# ============================================================

@app.post("/api/sar/predict-drift")
def predict_sar_drift(request: SARDiftRequest):

    conn = get_connection()

    incident = conn.execute(
        """
        SELECT
            last_known_latitude,
            last_known_longitude,
            object_type
        FROM sar_incidents
        WHERE id = ?
        """,
        (request.incident_id,),
    ).fetchone()

    if incident is None:
        conn.close()

        return {
            "error": "SAR incident not found"
        }

    latitude, longitude, object_type = incident

    prediction = predict_drift(
        latitude,
        longitude,
        request.current_speed_knots,
        request.current_direction_degrees,
        request.wind_speed_knots,
        request.wind_direction_degrees,
        request.hours,
        object_type
    )

    conn.execute(
        """
        INSERT INTO sar_predictions
        (
            incident_id,
            predicted_latitude,
            predicted_longitude,
            uncertainty_km
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            request.incident_id,
            prediction["predicted_latitude"],
            prediction["predicted_longitude"],
            prediction["uncertainty_km"],
        ),
    )

    conn.commit()
    conn.close()

    return {
        "incident_id": request.incident_id,
        "prediction": prediction,
        "estimate_type": "Probabilistic Search-Area Estimate",
        "warning": (
            "The prediction is an estimate based on supplied "
            "environmental inputs and is not an exact survivor location."
        ),
    }


# ============================================================
# SAR Location History
# ============================================================

@app.post("/api/sar/location")
def add_sar_location(request: SARLocationRequest):

    conn = get_connection()

    incident = conn.execute(
        """
        SELECT id
        FROM sar_incidents
        WHERE id = ?
        """,
        (request.incident_id,),
    ).fetchone()

    if incident is None:
        conn.close()

        return {
            "error": "SAR incident not found"
        }

    conn.execute(
        """
        INSERT INTO sar_location_history
        (
            incident_id,
            latitude,
            longitude
        )
        VALUES (?, ?, ?)
        """,
        (
            request.incident_id,
            request.latitude,
            request.longitude,
        ),
    )

    conn.execute(
        """
        UPDATE sar_incidents
        SET
            last_known_latitude = ?,
            last_known_longitude = ?
        WHERE id = ?
        """,
        (
            request.latitude,
            request.longitude,
            request.incident_id,
        ),
    )

    conn.commit()
    conn.close()

    return {
        "incident_id": request.incident_id,
        "latitude": request.latitude,
        "longitude": request.longitude,
        "status": "location recorded",
    }


# ============================================================
# SAR Search Zone Generation + Risk Engine
# ============================================================

@app.post("/api/sar/{incident_id}/search-zones")
def generate_search_zone(
    incident_id: int,
    risk_request: RiskRequest,
):

    conn = get_connection()

    prediction = conn.execute(
        """
        SELECT
            predicted_latitude,
            predicted_longitude,
            uncertainty_km
        FROM sar_predictions
        WHERE incident_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (incident_id,),
    ).fetchone()

    if prediction is None:
        conn.close()

        return {
            "error": "No SAR prediction found"
        }

    latitude, longitude, uncertainty_km = prediction

    zone = create_search_zone(
        latitude,
        longitude,
        uncertainty_km,
    )

    risk = calculate_risk_score(
        risk_request.wave_score,
        risk_request.wind_score,
        risk_request.weather_score,
        risk_request.current_score,
        risk_request.geofence_score,
        risk_request.alert_score,
    )

    zone["properties"]["risk_score"] = risk["risk_score"]
    zone["properties"]["risk_level"] = risk["risk_level"]
    zone["properties"]["recommended_action"] = risk["recommended_action"]

    if risk["risk_level"] == "HIGH":
        zone["properties"]["priority"] = "HIGH"

    elif risk["risk_level"] == "MODERATE":
        zone["properties"]["priority"] = "MEDIUM"

    else:
        zone["properties"]["priority"] = "LOW"

    conn.execute(
        """
        INSERT INTO sar_search_zones
        (
            incident_id,
            geometry,
            probability,
            risk_score,
            priority,
            recommended_action
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            incident_id,
            json.dumps(zone["geometry"]),
            1.0,
            zone["properties"]["risk_score"],
            zone["properties"]["priority"],
            zone["properties"]["recommended_action"],
        ),
    )

    conn.commit()
    conn.close()

    return {
        "incident_id": incident_id,
        "search_zone": zone,
        "risk": risk,
    }


# ============================================================
# SAR Particle Simulation
# ============================================================

@app.post("/api/sar/{incident_id}/particle-drift")
def particle_drift(request: SARParticleRequest):

    conn = get_connection()

    incident = conn.execute(
        """
        SELECT
            last_known_latitude,
            last_known_longitude
        FROM sar_incidents
        WHERE id = ?
        """,
        (request.incident_id,),
    ).fetchone()

    conn.close()

    if incident is None:
        return {
            "error": "SAR incident not found"
        }

    latitude, longitude = incident

    particles = simulate_particles(
        latitude,
        longitude,
        request.current_speed_knots,
        request.current_direction_degrees,
        request.wind_speed_knots,
        request.wind_direction_degrees,
        request.hours,
        request.particle_count,
    )

    return {
        "incident_id": request.incident_id,
        "particle_count": len(particles),
        "estimate_type": "Probabilistic Search-Area Estimate",
        "warning": (
            "Particles represent possible drift positions, "
            "not an exact survivor location."
        ),
        "particles": particles,
    }


# ============================================================
# SAR Particle Search Zone
# ============================================================

@app.post("/api/sar/{incident_id}/particle-zone")
def particle_search_zone(request: SARParticleRequest):

    conn = get_connection()

    incident = conn.execute(
        """
        SELECT
            last_known_latitude,
            last_known_longitude
        FROM sar_incidents
        WHERE id = ?
        """,
        (request.incident_id,),
    ).fetchone()

    if incident is None:
        conn.close()

        return {
            "error": "SAR incident not found"
        }

    latitude, longitude = incident

    particles = simulate_particles(
        latitude,
        longitude,
        request.current_speed_knots,
        request.current_direction_degrees,
        request.wind_speed_knots,
        request.wind_direction_degrees,
        request.hours,
        request.particle_count,
    )

    zone = create_particle_search_zone(particles)

    if "geometry" in zone:

        conn.execute(
            """
            INSERT INTO sar_search_zones
            (
                incident_id,
                geometry
            )
            VALUES (?, ?)
            """,
            (
                request.incident_id,
                json.dumps(zone["geometry"]),
            ),
        )

        conn.commit()

    conn.close()

    return {
        "incident_id": request.incident_id,
        "particle_count": len(particles),
        "estimate_type": "Probabilistic Search-Area Estimate",
        "search_zone": zone,
        "saved_to_sar_database": True,
    }


# ============================================================
# SAR Search Zone → India EEZ Check
# ============================================================

@app.get("/api/sar/{incident_id}/check-eez")
def check_sar_zone_eez(incident_id: int):

    conn = get_connection()

    zone = conn.execute(
        """
        SELECT
            id,
            geometry
        FROM sar_search_zones
        WHERE incident_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (incident_id,),
    ).fetchone()

    conn.close()

    if zone is None:
        return {
            "error": "No SAR search zone found"
        }

    zone_id, zone_geometry = zone

    with open(
        "india_eez.geojson",
        "r",
        encoding="utf-8",
    ) as file:
        eez = json.load(file)

    result = geometry_intersection(
        json.loads(zone_geometry),
        eez["features"][0]["geometry"],
    )

    return {
        "incident_id": incident_id,
        "zone_id": zone_id,
        "intersects_eez": result["intersects"],
    }


# ============================================================
# Get SAR Incident
# ============================================================

@app.get("/api/sar/{incident_id}")
def get_sar_incident(incident_id: int):

    conn = get_connection()

    incident = conn.execute(
        """
        SELECT
            id,
            status,
            last_known_latitude,
            last_known_longitude,
            created_at
        FROM sar_incidents
        WHERE id = ?
        """,
        (incident_id,),
    ).fetchone()

    conn.close()

    if incident is None:
        return {
            "error": "SAR incident not found"
        }

    return {
        "incident_id": incident[0],
        "status": incident[1],
        "last_known_latitude": incident[2],
        "last_known_longitude": incident[3],
        "created_at": incident[4],
    }


# ============================================================
# SAR Nearest Rescue Facility
# ============================================================

@app.post("/api/sar/{incident_id}/nearest-rescue")
def nearest_rescue(incident_id: int):

    conn = get_connection()

    incident = conn.execute(
        """
        SELECT
            last_known_latitude,
            last_known_longitude
        FROM sar_incidents
        WHERE id = ?
        """,
        (incident_id,),
    ).fetchone()

    conn.close()

    if incident is None:
        return {
            "error": "SAR incident not found"
        }

    latitude, longitude = incident

    result = find_nearest_rescue_facility(
        latitude,
        longitude,
    )

    return {
        "incident_id": incident_id,
        "last_known_position": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "nearest_rescue_facility": result,
    }


# ============================================================
# SAR Rescue Route
# ============================================================

@app.post("/api/sar/{incident_id}/rescue-route")
def sar_rescue_route(incident_id: int):

    conn = get_connection()

    incident = conn.execute(
        """
        SELECT
            last_known_latitude,
            last_known_longitude
        FROM sar_incidents
        WHERE id = ?
        """,
        (incident_id,),
    ).fetchone()

    conn.close()

    if incident is None:
        return {
            "error": "SAR incident not found"
        }

    start_latitude, start_longitude = incident

    rescue = find_nearest_rescue_facility(
        start_latitude,
        start_longitude,
    )

    facility = rescue["facility"]

    route_result = distance_and_bearing(
        start_latitude,
        start_longitude,
        facility["latitude"],
        facility["longitude"],
    )

    route_geometry = create_route_geometry(
        start_latitude,
        start_longitude,
        facility["latitude"],
        facility["longitude"],
    )

    return {
        "incident_id": incident_id,
        "start": {
            "latitude": start_latitude,
            "longitude": start_longitude,
        },
        "rescue_facility": facility,
        "distance_km": route_result["distance_km"],
        "bearing_degrees": route_result["bearing_degrees"],
        "route_geometry": route_geometry,
        "status": "rescue route analyzed",
    }


# ============================================================
# SAR Rescue Route Hazard Check
# ============================================================

@app.post("/api/sar/{incident_id}/rescue-route/hazard-check")
def rescue_route_hazard_check(
    incident_id: int,
    request: RescueRouteHazardRequest,
):

    conn = get_connection()

    incident = conn.execute(
        """
        SELECT
            last_known_latitude,
            last_known_longitude
        FROM sar_incidents
        WHERE id = ?
        """,
        (incident_id,),
    ).fetchone()

    conn.close()

    if incident is None:
        return {
            "error": "SAR incident not found"
        }

    start_latitude, start_longitude = incident

    rescue = find_nearest_rescue_facility(
        start_latitude,
        start_longitude,
    )

    facility = rescue["facility"]

    route_geometry = create_route_geometry(
        start_latitude,
        start_longitude,
        facility["latitude"],
        facility["longitude"],
    )

    hazard_result = hazard_zone_intersection(
        route_geometry,
        request.restricted_geometry,
    )

    return {
        "incident_id": incident_id,
        "route": route_geometry,
        "rescue_facility": facility,
        "hazard_check": hazard_result,
        "status": "rescue route hazard analysis completed",
    }


# ============================================================
# Get SAR Search Zones
# ============================================================

@app.get("/api/sar/{incident_id}/search-zones")
def get_search_zones(incident_id: int):

    conn = get_connection()

    zones = conn.execute(
        """
        SELECT
            id,
            geometry,
            probability,
            risk_score,
            priority,
            recommended_action,
            created_at
        FROM sar_search_zones
        WHERE incident_id = ?
        ORDER BY id DESC
        """,
        (incident_id,),
    ).fetchall()

    conn.close()

    return {
        "incident_id": incident_id,
        "count": len(zones),
        "search_zones": [
            {
                "zone_id": zone[0],
                "geometry": json.loads(zone[1]),
                "probability": zone[2],
                "risk_score": zone[3],
                "priority": zone[4],
                "recommended_action": zone[5],
                "created_at": zone[6],
            }
            for zone in zones
        ],
    }


# ============================================================
# Add SAR Evidence
# ============================================================

@app.post("/api/sar/evidence")
def add_sar_evidence(request: SAREvidenceRequest):

    conn = get_connection()

    incident = conn.execute(
        """
        SELECT id
        FROM sar_incidents
        WHERE id = ?
        """,
        (request.incident_id,),
    ).fetchone()

    if incident is None:
        conn.close()

        return {
            "error": "SAR incident not found"
        }

    source_timestamp = request.source_timestamp

    if source_timestamp is None:
        source_timestamp = datetime.now(
            timezone.utc
        ).isoformat()

    cursor = conn.execute(
        """
        INSERT INTO sar_evidence
        (
            incident_id,
            evidence_type,
            description,
            source,
            source_timestamp,
            confidence
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            request.incident_id,
            request.evidence_type,
            request.description,
            request.source,
            source_timestamp,
            request.confidence,
        ),
    )

    evidence_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return {
        "evidence_id": evidence_id,
        "incident_id": request.incident_id,
        "evidence_type": request.evidence_type,
        "description": request.description,
        "source": request.source,
        "source_timestamp": source_timestamp,
        "confidence": request.confidence,
        "status": "evidence recorded",
    }


# ============================================================
# Get SAR Evidence
# ============================================================

@app.get("/api/sar/{incident_id}/evidence")
def get_sar_evidence(incident_id: int):

    conn = get_connection()

    evidence = conn.execute(
        """
        SELECT
            id,
            evidence_type,
            description,
            source,
            source_timestamp,
            confidence,
            created_at
        FROM sar_evidence
        WHERE incident_id = ?
        ORDER BY id DESC
        """,
        (incident_id,),
    ).fetchall()

    conn.close()

    return {
        "incident_id": incident_id,
        "count": len(evidence),
        "evidence": [
            {
                "evidence_id": item[0],
                "evidence_type": item[1],
                "description": item[2],
                "source": item[3],
                "source_timestamp": item[4],
                "confidence": item[5],
                "created_at": item[6],
            }
            for item in evidence
        ],
    }


# ============================================================
# SAR Mission Package
# ============================================================

class MissionPackageRequest(BaseModel):
    restricted_geometry: dict | None = None


@app.post("/api/sar/{incident_id}/mission-package")
def sar_mission_package(
    incident_id: int,
    request: MissionPackageRequest | None = None,
):
    """Build one operational SAR package from the current incident state."""

    conn = get_connection()

    incident = conn.execute(
        """
        SELECT
            id,
            status,
            last_known_latitude,
            last_known_longitude,
            created_at
        FROM sar_incidents
        WHERE id = ?
        """,
        (incident_id,),
    ).fetchone()

    if incident is None:
        conn.close()
        return {"error": "SAR incident not found"}

    zone_rows = conn.execute(
        """
        SELECT
            id,
            geometry,
            probability,
            risk_score,
            priority,
            recommended_action,
            created_at
        FROM sar_search_zones
        WHERE incident_id = ?
        ORDER BY
            CASE priority
                WHEN 'HIGH' THEN 1
                WHEN 'MEDIUM' THEN 2
                WHEN 'LOW' THEN 3
                ELSE 4
            END,
            probability DESC,
            risk_score DESC,
            id ASC
        """,
        (incident_id,),
    ).fetchall()

    evidence_rows = conn.execute(
        """
        SELECT
            id,
            evidence_type,
            description,
            source,
            source_timestamp,
            confidence,
            created_at
        FROM sar_evidence
        WHERE incident_id = ?
        ORDER BY id DESC
        """,
        (incident_id,),
    ).fetchall()

    conn.close()

    start_latitude = incident[2]
    start_longitude = incident[3]

    rescue = find_nearest_rescue_facility(
        start_latitude,
        start_longitude,
    )

    facility = rescue["facility"]

    route_result = distance_and_bearing(
        start_latitude,
        start_longitude,
        facility["latitude"],
        facility["longitude"],
    )

    route_geometry = create_route_geometry(
        start_latitude,
        start_longitude,
        facility["latitude"],
        facility["longitude"],
    )

    if request is not None and request.restricted_geometry is not None:
        hazard_check = hazard_zone_intersection(
            route_geometry,
            request.restricted_geometry,
        )
    else:
        hazard_check = {
            "status": "not_requested",
            "intersects": None,
            "message": (
                "Provide restricted_geometry to run the rescue-route "
                "hazard check."
            ),
        }

    zones = []

    for rank, zone in enumerate(zone_rows, start=1):
        probability = zone[2]
        risk_score = zone[3]

        probability_weighted_risk = None

        if probability is not None and risk_score is not None:
            probability_weighted_risk = round(
                float(probability) * float(risk_score),
                6,
            )

        zones.append(
            {
                "rank": rank,
                "zone_id": zone[0],
                "geometry": json.loads(zone[1]),
                "probability": probability,
                "risk_score": risk_score,
                "priority": zone[4],
                "recommended_action": zone[5],
                "probability_weighted_risk": probability_weighted_risk,
                "created_at": zone[6],
            }
        )

    evidence = [
        {
            "evidence_id": item[0],
            "evidence_type": item[1],
            "description": item[2],
            "source": item[3],
            "source_timestamp": item[4],
            "confidence": item[5],
            "created_at": item[6],
        }
        for item in evidence_rows
    ]

    return {
        "incident": {
            "incident_id": incident[0],
            "status": incident[1],
            "last_known_latitude": incident[2],
            "last_known_longitude": incident[3],
            "created_at": incident[4],
        },
        "search_zones": {
            "count": len(zones),
            "zones": zones,
            "prioritization": (
                "Zones are ordered by operational priority, then "
                "probability and risk score. Probability-weighted risk "
                "is a planning metric, not an exact survivor-location "
                "probability."
            ),
        },
        "rescue": {
            "nearest_rescue_facility": facility,
            "distance_km": route_result["distance_km"],
            "bearing_degrees": route_result["bearing_degrees"],
            "route_geometry": route_geometry,
            "hazard_check": hazard_check,
        },
        "evidence": {
            "count": len(evidence),
            "items": evidence,
        },
        "estimate_warning": (
            "SAR search zones are planning estimates based on available "
            "data and are not exact survivor locations."
        ),
        "status": "SAR mission package generated",
    }


# ============================================================
# SAR Mission Brief PDF
# ============================================================

@app.get("/api/sar/{incident_id}/mission-brief/pdf")
def generate_sar_mission_brief_pdf(incident_id: int):
    """Generate and return the SAR Mission Brief PDF for the requested incident."""

    conn = get_connection()

    incident = conn.execute(
        """
        SELECT
            id,
            status,
            last_known_latitude,
            last_known_longitude,
            created_at
        FROM sar_incidents
        WHERE id = ?
        """,
        (incident_id,),
    ).fetchone()

    conn.close()

    if incident is None:
        return {
            "error": "SAR incident not found"
        }

    try:
        from sar_mission_brief_pdf import build_pdf
    except ImportError as exc:
        return {
            "error": "SAR PDF generator is not available",
            "details": str(exc),
        }

    build_pdf()

    pdf_path = "sar_mission_brief.pdf"

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename="sar_mission_brief.pdf",
    )


# ============================================================
# Standalone Risk Engine
# ============================================================

@app.post("/api/risk/calculate")
def calculate_risk(request: RiskRequest):

    return calculate_risk_score(
        request.wave_score,
        request.wind_score,
        request.weather_score,
        request.current_score,
        request.geofence_score,
        request.alert_score,
    )


# ============================================================
# Root
# ============================================================

@app.get("/")
def root():

    return {
        "status": "ORCA GIS + SAR API is running"
    }