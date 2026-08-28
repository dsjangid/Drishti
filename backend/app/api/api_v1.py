from fastapi import APIRouter
from app.api.endpoints import dockets, fleet, telemetry, analytics, contractors, inference

api_router = APIRouter()

api_router.include_router(dockets.router, prefix="/dockets", tags=["Road Dockets & Work Orders"])
api_router.include_router(fleet.router, prefix="/fleet", tags=["Transit Fleet & Drivers"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["IoT Ingestion & Telemetry"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["GIS Cartography & Traffic Analytics"])
api_router.include_router(contractors.router, prefix="/contractors", tags=["PWD Contractor SLA Management"])
api_router.include_router(inference.router, prefix="/inference", tags=["Edge-AI Perception & Defect Detection"])

