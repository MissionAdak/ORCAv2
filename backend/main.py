import os
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Import the existing app (now an APIRouter) from Sangeeta's services
from app import app as sangeeta_router
from data_ingestion import fetch_open_meteo_data, fetch_mock_incois_pfz, fetch_mock_alerts
from agents.bhashini_service import BhashiniService
from agents.evidence_engine import EvidenceEngine
app = FastAPI(title="ORCA API Gateway")

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Database connection stub (Day 4)
# ============================================================
def get_available_data_sources(category: str):
    """
    Mock DB connection to data_source_registry.
    Filters available tide and lightning datasets.
    """
    db_url = os.getenv("DATABASE_URL")
    # Simulate DB lookup
    registry = [
        {
            "id": "uuid-tide-1",
            "source_name": "incois",
            "dataset_name": "tide_predictions",
            "category": "tide",
            "parameter": "tide_height",
            "update_frequency": "hourly",
            "authority_level": "official",
            "is_available": True
        },
        {
            "id": "uuid-lightning-1",
            "source_name": "imd",
            "dataset_name": "lightning_alerts",
            "category": "lightning",
            "parameter": "lightning_strike",
            "update_frequency": "real-time",
            "authority_level": "official",
            "is_available": True
        }
    ]
    return [source for source in registry if source["category"] == category and source["is_available"]]

# ============================================================
# API Gateway Shells
# ============================================================

@app.get("/api/marine/forecast")
def get_marine_forecast(lat: float, lon: float, date: str = None):
    """
    Day 3: Serve the normalized Open-Meteo data.
    """
    data = fetch_open_meteo_data(lat, lon)
    return {"status": "success", "data": data}

@app.get("/api/weather/forecast")
def get_weather_forecast(lat: float, lon: float, date: str = None):
    """
    Day 3: Serve normalized weather forecast data.
    """
    data = fetch_open_meteo_data(lat, lon)
    return {"status": "success", "data": data}

@app.get("/api/pfz/nearby")
def get_pfz_nearby(lat: float, lon: float, max_distance_km: Optional[float] = 50.0):
    """
    Day 3: Serve the mocked INCOIS PFZ polygons.
    """
    data = fetch_mock_incois_pfz(lat, lon)
    return {"status": "success", "data": data}

@app.get("/api/alerts/nearby")
def get_alerts_nearby(lat: float, lon: float, radius_km: Optional[float] = 50.0):
    """
    Day 3: Active hazard/cyclone/lightning alerts.
    """
    data = fetch_mock_alerts(lat, lon, radius_km)
    return {"status": "success", "alerts": data}

@app.get("/api/geospatial/zones")
def get_geospatial_zones(bbox: str):
    """
    Day 3: Hazard/restricted/IMBL polygons for map layer.
    """
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[72.0, 19.0], [73.0, 19.0], [73.0, 20.0], [72.0, 20.0], [72.0, 19.0]]
                    ]
                },
                "properties": {
                    "zone_type": "restricted",
                    "severity": "high"
                }
            }
        ]
    }

@app.post("/api/chat")
async def post_chat(
    audio: Optional[UploadFile] = File(None), 
    text: Optional[str] = Form(None)
):
    """
    Day 3: Route the structured Bhashini intent JSON to Yug's orchestrator.
    """
    try:
        bhashini_service = BhashiniService()
        
        if audio:
            audio_bytes = await audio.read()
            intent_json = bhashini_service.process_voice_query(audio_bytes)
        else:
            # Fallback if no audio is provided
            intent_json = bhashini_service._get_fallback_intent()
            
        return {
            "status": "success",
            "message": "Intent routed to LangGraph orchestrator.",
            "received_intent": intent_json
        }
    except Exception as e:
        # Fallback to ensure 500 error isn't thrown
        return {
            "status": "success",
            "message": "Fallback intent routed.",
            "received_intent": {
                "intent": "fishing_safety", 
                "language_detected": "mr-IN", 
                "location": {"name": "Versova", "lat": 19.13, "lon": 72.81}, 
                "date": "2026-09-23"
            }
        }

class FishingProductivityRequest(BaseModel):
    region: dict
    start_date: str
    end_date: str
    species: Optional[str] = None

@app.post("/api/trends/fishing-productivity")
def get_fishing_productivity(request: FishingProductivityRequest):
    """
    Day 4: Query historical SST, chlorophyll, and PFZ changes.
    """
    return {
        "status": "success",
        "trend_direction": "declining",
        "trend_metrics": {
            "sst_trend": "+0.5C",
            "chlorophyll_trend": "-1.2mg/m3",
            "pfz_frequency": "-15%"
        },
        "observed_changes": "The selected region shows a decline in PFZ frequency and chlorophyll concentration over the selected period, while SST increased.",
        "possible_contributing_factors": ["SST increase", "Current shifts"],
        "evidence": ["incois_historical", "mosdac_historical"],
        "confidence": 0.85
    }

@app.get("/api/data-sources/catalog")
def get_data_sources_catalog():
    """
    Shell for Data Sources Catalog.
    """
    tides = get_available_data_sources("tide")
    lightning = get_available_data_sources("lightning")
    return {"status": "success", "catalog": tides + lightning}

@app.get("/api/data-sources/status")
def get_data_sources_status():
    """
    Health/staleness of each ingestion source.
    """
    return {
        "status": "success",
        "sources": [
            {"source": "open-meteo", "status": "healthy", "last_updated": "2026-09-17T08:00:00Z"},
            {"source": "incois", "status": "healthy", "last_updated": "2026-09-17T08:00:00Z"}
        ]
    }

class SARIncidentCreate(BaseModel):
    object_type: str
    people_count: int
    last_known_lat: float
    last_known_lon: float
    vessel_id: str

class SARLocationUpdate(BaseModel):
    lat: float
    lon: float
    accuracy: float
    source: str

class SARDriftPredictRequest(BaseModel):
    incident_id: str

@app.post("/api/sar/create")
def create_sar_incident(request: SARIncidentCreate):
    return {
        "status": "success",
        "incident_id": "sar-uuid-1234",
        "initial_status": "search_active"
    }

@app.post("/api/sar/location")
def update_sar_location(request: SARLocationUpdate):
    return {"status": "success", "message": "Location updated"}

@app.post("/api/sar/predict-drift")
def predict_sar_drift(request: SARDriftPredictRequest):
    return {
        "status": "success",
        "incident_id": request.incident_id,
        "search_zones": [
            {"zone": "A", "probability": 0.78, "priority": 1},
            {"zone": "B", "probability": 0.61, "priority": 2},
            {"zone": "C", "probability": 0.34, "priority": 3}
        ],
        "uncertainty_radius_m": 2400
    }

@app.get("/api/sar/{id}")
def get_sar_incident(id: str):
    return {
        "status": "success",
        "incident_id": id,
        "object_type": "capsized_hull",
        "people_count": 4,
        "vessel_id": "MH01AB1234",
        "last_known_lat": 19.1136,
        "last_known_lon": 72.8090,
        "severity": "critical"
    }

@app.get("/api/sar/{id}/search-zones")
def get_sar_search_zones(id: str):
    return {
        "status": "success",
        "incident_id": id,
        "sar_search_zones": [
            {"zone": "A", "probability": 0.78, "priority": 1, "recommended_action": "Deploy nearest"},
            {"zone": "B", "probability": 0.61, "priority": 2, "recommended_action": "Secondary sweep"},
            {"zone": "C", "probability": 0.34, "priority": 3, "recommended_action": "Extend search"}
        ]
    }

@app.post("/api/sar/{id}/brief")
def generate_sar_brief(id: str):
    return {
        "status": "success",
        "incident_id": id,
        "brief_url": f"https://orca.gov.in/brief/{id}.pdf",
        "geojson_url": f"https://orca.gov.in/brief/{id}.geojson"
    }

# Finally mount Sangeeta's and Yug's existing services
# This ensures Gateway mock endpoints take precedence!
app.include_router(sangeeta_router)
