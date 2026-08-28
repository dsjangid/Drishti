# दृष्टि (Drishti) — Backend REST & WebSocket API Specification

## Base URL
- **Local Development**: `http://localhost:8000/api/v1`
- **Interactive Swagger UI**: `http://localhost:8000/docs`
- **ReDoc Interactive Spec**: `http://localhost:8000/redoc`
- **Live WebSocket Telemetry**: `ws://localhost:8000/ws/telemetry`

---

## 1. Road Dockets & Work Orders (`/api/v1/dockets`)

### `GET /api/v1/dockets`
Retrieve list of all defect dockets with optional filtering.

**Query Parameters:**
- `status` (string, optional): Filter by status (`Pending Review`, `In Progress`, `Resolved`, `Active Pursuit`)
- `severity` (string, optional): `Critical`, `High`, `Moderate`, `Low`
- `bus_id` (string, optional): e.g. `BUS-003`
- `ward` (integer, optional): e.g. `12`
- `search` (string, optional): Free text query matching location or defect type
- `limit` (integer, default `50`)

**Response Example (`200 OK`):**
```json
[
  {
    "id": "INC-8924",
    "defect_type": "POTHOLE",
    "severity": "High",
    "status": "Pending Review",
    "location_name": "Corridor 1 · KM 4.2 Northbound",
    "ward_number": 12,
    "corridor": "Arterial Corridor 1",
    "lat": 26.8850,
    "lng": 75.7900,
    "detected_by_bus": "BUS-003",
    "confidence": 0.964,
    "depth_cm": 16.4,
    "estimated_volume_m3": 0.186,
    "imu_shock_g": 3.2,
    "asphalt_tonnage_mt": 0.51,
    "repair_cost_inr": 4900.0,
    "assigned_contractor": "Municipal Smart City Infrastructure Ltd",
    "sla_target_hours": 48,
    "detected_at": "2026-08-25T11:00:00Z",
    "resolved_at": null
  }
]
```

### `POST /api/v1/dockets`
Submit a new defect docket. Automated Indian Roads Congress (IRC) cost calculator determines hot-mix tonnage and repair budget.

**Request Body:**
```json
{
  "defect_type": "POTHOLE",
  "severity": "High",
  "location_name": "Arterial Corridor 1 · Sector 9",
  "ward_number": 3,
  "lat": 26.9123,
  "lng": 75.7890,
  "detected_by_bus": "BUS-001",
  "confidence": 0.975,
  "depth_cm": 15.0,
  "imu_shock_g": 3.1
}
```

### `PATCH /api/v1/dockets/{docket_id}`
Update docket status, reassign contractor, or mark resolved.

**Request Body:**
```json
{
  "status": "Resolved",
  "notes": "Patching completed with 12 MT Hot-Mix asphalt by crew #4."
}
```

### `GET /api/v1/dockets/stats/summary`
Get high-level summary KPIs for the municipal command center dashboard.

---

## 2. Transit Fleet & Drivers (`/api/v1/fleet`)

### `GET /api/v1/fleet`
Lists all 10 transit buses with real-time GPS coordinates, velocity, and edge NPU hardware metrics.

### `GET /api/v1/fleet/drivers/leaderboard`
Returns Driver Safety Monitoring (DMS) rankings, eye aspect ratio alert events, and safety index scores (0–100).

---

## 3. IoT Edge Telemetry Ingestion (`/api/v1/telemetry`)

### `POST /api/v1/telemetry/ingest`
High-frequency ingestion endpoint for 4G LTE IoT packets from buses.

**Request Body:**
```json
{
  "bus_id": "BUS-003",
  "lat": 26.8850,
  "lng": 75.7900,
  "speed_kmh": 34.2,
  "heading_deg": 182.5,
  "imu_z_accel_g": 3.4,
  "imu_vibration_rms": 0.25,
  "defect_detected": true,
  "defect_type": "POTHOLE",
  "defect_confidence": 0.968,
  "defect_depth_cm": 16.2
}
```

> **Auto-Docket Trigger**: If `imu_z_accel_g >= 2.8g` or `defect_detected == true`, the backend automatically generates a municipal work docket and assigns the responsible ward contractor.

---

## 4. GIS Cartography & Analytics (`/api/v1/analytics`)

### `GET /api/v1/analytics/geojson`
Returns RFC 7946 compliant GeoJSON FeatureCollection of all active defect dockets for seamless integration with QGIS, ESRI ArcGIS, and Leaflet.

### `GET /api/v1/analytics/traffic-curves`
Returns 24-hour diurnal traffic volume curves (Passenger Car Units - PCU) and congestion indices.

### `GET /api/v1/analytics/ward-breakdown`
Returns ward-by-ward defect density, asphalt tonnage demand, and resolution rates.

---

## 5. Edge-AI Computer Vision (`/api/v1/inference`)

### `POST /api/v1/inference/image`
Upload a dashcam image (`multipart/form-data`) to execute YOLOv8x defect inference, returning detected bounding boxes, confidence scores, class labels, and metric depth estimates.

---

## 6. Real-Time WebSocket Streaming (`/ws/telemetry`)

Connect via WebSocket to receive 1Hz continuous live updates of all 10 transit buses.

**Sample WebSocket Message:**
```json
{
  "event": "FLEET_TELEMETRY_UPDATE",
  "timestamp": 1724587600.12,
  "fleet_size": 10,
  "buses": [
    {
      "bus_id": "BUS-001",
      "driver": "Rajesh Sharma",
      "route": "Route 1: Central Spine Arterial",
      "lat": 26.9239,
      "lng": 75.8267,
      "speed": 28.5,
      "safety_score": 92,
      "is_active": true
    }
  ]
}
```

