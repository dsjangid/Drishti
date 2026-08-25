from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.models.bus import Bus
from app.models.telemetry import TelemetryLog
from app.models.docket import RoadDocket
from app.schemas.telemetry import TelemetryIngest, TelemetryResponse
from app.services.cost_calculator import IRCCostCalculator

router = APIRouter()

@router.post("/ingest", response_model=TelemetryResponse, status_code=status.HTTP_201_CREATED, summary="Ingest 4G LTE IoT packet from bus edge unit")
def ingest_telemetry(payload: TelemetryIngest, db: Session = Depends(get_db)):
    bus = db.query(Bus).filter(Bus.id == payload.bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{payload.bus_id}' not registered in fleet inventory.")

    # 1. Update live bus coordinates & velocity
    bus.current_lat = payload.lat
    bus.current_lng = payload.lng
    bus.current_speed = payload.speed_kmh
    bus.updated_at = datetime.utcnow()

    # 2. Record time-series telemetry log
    log_entry = TelemetryLog(
        bus_id=payload.bus_id,
        lat=payload.lat,
        lng=payload.lng,
        speed_kmh=payload.speed_kmh,
        heading_deg=payload.heading_deg,
        imu_z_accel_g=payload.imu_z_accel_g,
        imu_vibration_rms=payload.imu_vibration_rms,
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)

    # 3. If edge NPU detected a defect or IMU shock spike (> 2.8g), auto-generate docket
    if payload.defect_detected or payload.imu_z_accel_g >= 2.8:
        defect_type = payload.defect_type or "POTHOLE"
        depth_cm = payload.defect_depth_cm or (14.0 if payload.imu_z_accel_g > 3.0 else 8.0)
        confidence = payload.defect_confidence or 0.95
        
        severity = "Critical" if payload.imu_z_accel_g >= 3.2 else "High" if depth_cm > 12.0 else "Moderate"
        
        metrics = IRCCostCalculator.calculate_repair_metrics(depth_cm=depth_cm, defect_type=defect_type)
        
        existing_ids = {d.id for d in db.query(RoadDocket.id).all()}
        num = 8940
        while f"INC-{num}" in existing_ids:
            num += 1
        docket_id = f"INC-{num}"
        
        new_docket = RoadDocket(
            id=docket_id,
            defect_type=defect_type,
            severity=severity,
            status="Pending Review",
            location_name=f"{bus.route_name} · Real-Time Telemetry Intercept",
            ward_number=5,
            corridor=bus.corridor_type,
            lat=payload.lat,
            lng=payload.lng,
            detected_by_bus=payload.bus_id,
            confidence=confidence,
            depth_cm=depth_cm,
            estimated_volume_m3=metrics["volume_m3"],
            imu_shock_g=payload.imu_z_accel_g,
            asphalt_tonnage_mt=metrics["tonnage_mt"],
            repair_cost_inr=metrics["estimated_cost_inr"],
            assigned_contractor="Municipal Smart City Infrastructure Ltd",
            detected_at=datetime.utcnow()
        )
        db.add(new_docket)

    db.commit()
    db.refresh(log_entry)
    return log_entry

@router.get("/recent", response_model=List[TelemetryResponse], summary="Get recent telemetry logs")
def get_recent_telemetry(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(TelemetryLog).order_by(TelemetryLog.timestamp.desc()).limit(limit).all()
