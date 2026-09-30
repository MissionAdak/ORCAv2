import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the production APIRouter from Sangeeta's core services
from app import app as sangeeta_router

# Import the production APIRouter from Yug's AI chat services
from chat_router import router as chat_router

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
# Production Routes
# ============================================================

# Mount Yug's AI Chat & Voice Services
app.include_router(chat_router)

# Mount Sangeeta's Core GIS, PFZ, and SAR Services
from fastapi import APIRouter

pfz_router = APIRouter()
@pfz_router.get("/nearby")
def get_nearby_pfz(lat: float, lon: float):
    return {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": { "name": "High Probability PFZ", "type": "Potential Fishing Zone", "confidence": "92%", "source": "INCOIS" },
            "geometry": { "type": "Polygon", "coordinates": [[[72.75, 19.10], [72.70, 19.15], [72.78, 19.18], [72.80, 19.12], [72.75, 19.10]]] }
        }]
    }

geospatial_router = APIRouter()
@geospatial_router.get("/zones")
def get_zones():
    return {
        "imbl": {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": { "name": "IMBL 5nm Buffer", "type": "International Maritime Boundary Line", "warning": "Approaching International Waters" },
                "geometry": { "type": "LineString", "coordinates": [[72.4, 18.9], [72.3, 19.2], [72.2, 19.5]] }
            }]
        },
        "hazards": {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": { "name": "Cyclone Warning", "type": "hazard", "severity": "High", "source": "IMD" },
                "geometry": { "type": "Polygon", "coordinates": [[[72.5, 18.9], [72.6, 18.9], [72.6, 19.0], [72.5, 19.0], [72.5, 18.9]]] }
            }]
        },
        "rescue": {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": { "name": "Coast Guard Station", "type": "rescue", "contact": "VHF 16" },
                "geometry": { "type": "Point", "coordinates": [72.82, 19.15] }
            }]
        }
    }

app.include_router(pfz_router, prefix="/api/pfz")
app.include_router(geospatial_router, prefix="/api/geospatial")
app.include_router(sangeeta_router)
