import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.db.seed import seed_database

# Use in-memory SQLite with StaticPool so all connections share the same database
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_database(db)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "docs_url" in data

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_fleet():
    response = client.get("/api/v1/fleet")
    assert response.status_code == 200
    buses = response.json()
    assert len(buses) == 10
    assert buses[0]["id"] == "BUS-001"
    assert "npu_temp_c" in buses[0]

def test_get_driver_leaderboard():
    response = client.get("/api/v1/fleet/drivers/leaderboard")
    assert response.status_code == 200
    drivers = response.json()
    assert len(drivers) == 10
    # Should be sorted by score descending
    assert drivers[0]["safety_score"] >= drivers[-1]["safety_score"]

def test_dockets_crud():
    # 1. Get initial dockets
    res = client.get("/api/v1/dockets")
    assert res.status_code == 200
    initial_count = len(res.json())
    assert initial_count >= 8

    # 2. Create new docket
    new_docket = {
        "defect_type": "POTHOLE",
        "severity": "High",
        "status": "Pending Review",
        "location_name": "Test Arterial Sector 9",
        "ward_number": 3,
        "corridor": "Arterial Corridor 1",
        "lat": 26.9123,
        "lng": 75.7890,
        "detected_by_bus": "BUS-001",
        "confidence": 0.975,
        "depth_cm": 15.0,
        "imu_shock_g": 3.1
    }
    create_res = client.post("/api/v1/dockets", json=new_docket)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["location_name"] == "Test Arterial Sector 9"
    assert created_data["asphalt_tonnage_mt"] > 0.0
    assert created_data["repair_cost_inr"] > 0.0
    docket_id = created_data["id"]

    # 3. Update docket status to In Progress
    patch_res = client.patch(f"/api/v1/dockets/{docket_id}", json={"status": "In Progress"})
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "In Progress"

    # 4. Resolve docket
    resolve_res = client.patch(f"/api/v1/dockets/{docket_id}", json={"status": "Resolved"})
    assert resolve_res.status_code == 200
    assert resolve_res.json()["status"] == "Resolved"
    assert resolve_res.json()["resolved_at"] is not None

def test_dockets_summary_stats():
    res = client.get("/api/v1/dockets/stats/summary")
    assert res.status_code == 200
    data = res.json()
    assert data["total_dockets"] >= 8
    assert data["estimated_total_repair_inr"] > 0

def test_telemetry_ingest():
    payload = {
        "bus_id": "BUS-003",
        "lat": 26.9150,
        "lng": 75.7900,
        "speed_kmh": 36.5,
        "heading_deg": 180.0,
        "imu_z_accel_g": 3.4, # High shock should trigger auto-docket
        "defect_detected": True,
        "defect_type": "POTHOLE",
        "defect_depth_cm": 18.0
    }
    res = client.post("/api/v1/telemetry/ingest", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["bus_id"] == "BUS-003"
    assert data["speed_kmh"] == 36.5

def test_analytics_geojson():
    res = client.get("/api/v1/analytics/geojson")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) >= 8
    assert "geometry" in data["features"][0]
    assert data["features"][0]["geometry"]["type"] == "Point"

def test_traffic_curves():
    res = client.get("/api/v1/analytics/traffic-curves")
    assert res.status_code == 200
    curves = res.json()
    assert len(curves) == 16
    assert "pcu_volume" in curves[0]

def test_contractors_list():
    res = client.get("/api/v1/contractors")
    assert res.status_code == 200
    contractors = res.json()
    assert len(contractors) == 4
    assert contractors[0]["sla_compliance_rate"] >= 80.0

