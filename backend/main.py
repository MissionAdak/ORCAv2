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
app.include_router(sangeeta_router)
