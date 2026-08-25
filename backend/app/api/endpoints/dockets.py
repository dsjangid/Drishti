from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db.session import get_db
from app.models.docket import RoadDocket
from app.schemas.docket import DocketCreate, DocketUpdate, DocketResponse, DocketSummaryStats
from app.services.cost_calculator import IRCCostCalculator

router = APIRouter()

@router.get("", response_model=List[DocketResponse], summary="List all road defect dockets")
def get_dockets(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (e.g. Pending Review, Resolved)"),
    severity: Optional[str] = Query(None, description="Filter by severity (High, Moderate, Critical)"),
    bus_id: Optional[str] = Query(None, description="Filter by reporting bus ID"),
    ward: Optional[int] = Query(None, description="Filter by ward number"),
    search: Optional[str] = Query(None, description="Text search on location and defect type"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(RoadDocket)
    
    if status_filter and status_filter.upper() != "ALL":
        query = query.filter(RoadDocket.status.ilike(f"%{status_filter}%"))
    if severity:
        query = query.filter(RoadDocket.severity.ilike(f"%{severity}%"))
    if bus_id:
        query = query.filter(RoadDocket.detected_by_bus == bus_id)
    if ward:
        query = query.filter(RoadDocket.ward_number == ward)
    if search:
        s = f"%{search}%"
        query = query.filter(
            (RoadDocket.location_name.ilike(s)) |
            (RoadDocket.defect_type.ilike(s)) |
            (RoadDocket.id.ilike(s))
        )
        
    return query.order_by(RoadDocket.detected_at.desc()).limit(limit).all()

@router.get("/stats/summary", response_model=DocketSummaryStats, summary="Get summary statistics for municipal command center")
def get_docket_summary(db: Session = Depends(get_db)):
    dockets = db.query(RoadDocket).all()
    
    total = len(dockets)
    pending = sum(1 for d in dockets if d.status == "Pending Review")
    in_progress = sum(1 for d in dockets if d.status == "In Progress")
    resolved = sum(1 for d in dockets if d.status == "Resolved")
    pursuits = sum(1 for d in dockets if d.status == "Active Pursuit")
    critical = sum(1 for d in dockets if d.severity in ["Critical", "High"])
    total_cost = sum(d.repair_cost_inr for d in dockets)
    total_tonnage = sum(d.asphalt_tonnage_mt for d in dockets)
    
    return DocketSummaryStats(
        total_dockets=total,
        pending_review=pending,
        in_progress=in_progress,
        resolved_today=resolved,
        active_pursuits=pursuits,
        critical_count=critical,
        estimated_total_repair_inr=round(total_cost, 2),
        total_asphalt_tonnage_mt=round(total_tonnage, 2)
    )

@router.get("/{docket_id}", response_model=DocketResponse, summary="Get a single docket by ID")
def get_docket_by_id(docket_id: str, db: Session = Depends(get_db)):
    docket = db.query(RoadDocket).filter(RoadDocket.id == docket_id).first()
    if not docket:
        raise HTTPException(status_code=404, detail=f"Docket '{docket_id}' not found.")
    return docket

@router.post("", response_model=DocketResponse, status_code=status.HTTP_201_CREATED, summary="Create/Report new defect docket")
def create_docket(payload: DocketCreate, db: Session = Depends(get_db)):
    # Auto-generate ID if not provided
    docket_id = payload.id
    if not docket_id:
        existing_ids = {d.id for d in db.query(RoadDocket.id).all()}
        num = 8932
        while f"INC-{num}" in existing_ids:
            num += 1
        docket_id = f"INC-{num}"

    # Compute IRC asphalt and repair budget
    metrics = IRCCostCalculator.calculate_repair_metrics(
        depth_cm=payload.depth_cm,
        defect_type=payload.defect_type
    )

    docket = RoadDocket(
        id=docket_id,
        defect_type=payload.defect_type,
        severity=payload.severity,
        status=payload.status,
        location_name=payload.location_name,
        ward_number=payload.ward_number,
        corridor=payload.corridor,
        lat=payload.lat,
        lng=payload.lng,
        detected_by_bus=payload.detected_by_bus,
        confidence=payload.confidence,
        depth_cm=payload.depth_cm,
        estimated_volume_m3=metrics["volume_m3"],
        imu_shock_g=payload.imu_shock_g,
        asphalt_tonnage_mt=metrics["tonnage_mt"],
        repair_cost_inr=metrics["estimated_cost_inr"],
        assigned_contractor=payload.assigned_contractor,
        sla_target_hours=payload.sla_target_hours,
        notes=payload.notes,
        snapshot_url=payload.snapshot_url,
        detected_at=datetime.utcnow()
    )

    db.add(docket)
    db.commit()
    db.refresh(docket)
    return docket

@router.patch("/{docket_id}", response_model=DocketResponse, summary="Update docket status, contractor, or resolution")
def update_docket(docket_id: str, payload: DocketUpdate, db: Session = Depends(get_db)):
    docket = db.query(RoadDocket).filter(RoadDocket.id == docket_id).first()
    if not docket:
        raise HTTPException(status_code=404, detail=f"Docket '{docket_id}' not found.")

    if payload.status is not None:
        docket.status = payload.status
        if payload.status == "Resolved" and not docket.resolved_at:
            docket.resolved_at = datetime.utcnow()
    if payload.severity is not None:
        docket.severity = payload.severity
    if payload.assigned_contractor is not None:
        docket.assigned_contractor = payload.assigned_contractor
    if payload.notes is not None:
        docket.notes = payload.notes

    db.commit()
    db.refresh(docket)
    return docket

@router.delete("/{docket_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a docket")
def delete_docket(docket_id: str, db: Session = Depends(get_db)):
    docket = db.query(RoadDocket).filter(RoadDocket.id == docket_id).first()
    if not docket:
        raise HTTPException(status_code=404, detail=f"Docket '{docket_id}' not found.")
    db.delete(docket)
    db.commit()
    return None
