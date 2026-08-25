from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.api.api_v1 import api_router
from app.api.ws import router as ws_router
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.seed import seed_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and auto-seed initial municipal dataset
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    # Shutdown: Clean up any background tasks if necessary

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
# दृष्टि (Drishti) — Urban Road Intelligence Command Backend API

An end-to-end municipal platform turning public transit fleets into real-time road perception networks.

### Capabilities:
* **IoT Telemetry Ingestion**: 4G LTE sub-second telemetry streams with STAN 6-axis IMU vibration shock logging.
* **Automated Work Orders**: Instant defect classification and Indian Roads Congress (IRC) asphalt tonnage estimation.
* **GIS Cartography**: RFC 7946 GeoJSON layers for municipal GIS teams (ESRI ArcGIS, QGIS).
* **Live WebSocket Telemetry**: 1Hz multi-bus position & velocity broadcasts.
* **Edge-AI Video Inference**: Ultralytics YOLOv8x defect classification with ByteTrack multi-object tracking.
    """,
    openapi_tags=[
        {"name": "Road Dockets & Work Orders", "description": "Manage pothole dockets, dispatch repair crews, update SLA."},
        {"name": "Transit Fleet & Drivers", "description": "10-bus fleet inventory, live velocity, and driver DMS safety index."},
        {"name": "IoT Ingestion & Telemetry", "description": "Receive sensor packets from bus edge units (Jetson Orin Nano)."},
        {"name": "GIS Cartography & Traffic Analytics", "description": "Export GeoJSON layers, 24h traffic volume curves, and ward aggregations."},
        {"name": "PWD Contractor SLA Management", "description": "Contractor turnaround scorecard and compliance monitoring."},
        {"name": "Edge-AI Perception & Defect Detection", "description": "Real-time YOLOv8 neural network inference on road frames."},
    ],
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(ws_router, prefix="/ws", tags=["Real-Time WebSockets"])

@app.get("/", summary="Root Health Check & API Metadata")
def root():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_v1": settings.API_V1_STR,
        "websocket_url": "/ws/telemetry"
    }

@app.get("/health", summary="Liveness & Readiness Probe")
def health_check():
    return {"status": "healthy", "timestamp": str(asynccontextmanager)}
