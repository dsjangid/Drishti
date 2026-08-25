from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.session import get_db
from app.models.bus import Bus
from app.schemas.fleet import BusResponse, BusCreate, BusUpdate, DriverLeaderboardItem

router = APIRouter()

@router.get("", response_model=List[BusResponse], summary="List all transit buses and edge hardware status")
def get_fleet(
    active_only: bool = Query(False, description="Filter for online units only"),
    db: Session = Depends(get_db)
):
    query = db.query(Bus)
    if active_only:
        query = query.filter(Bus.is_active == True)
    return query.order_by(Bus.id.asc()).all()

@router.get("/drivers/leaderboard", response_model=List[DriverLeaderboardItem], summary="Get Driver Safety Monitoring (DMS) scorecards")
def get_driver_leaderboard(db: Session = Depends(get_db)):
    buses = db.query(Bus).all()
    leaderboard = []
    
    for b in buses:
        score = b.driver_safety_score
        if score >= 90:
            grade = "A+"
            risk = "Low"
            events = 0
        elif score >= 80:
            grade = "A"
            risk = "Moderate"
            events = 1
        elif score >= 70:
            grade = "B"
            risk = "Elevated"
            events = 3
        else:
            grade = "C"
            risk = "High (Training Required)"
            events = 5
            
        leaderboard.append(DriverLeaderboardItem(
            bus_id=b.id,
            driver_name=b.driver_name,
            safety_score=score,
            grade=grade,
            risk_level=risk,
            recent_events=events
        ))
        
    leaderboard.sort(key=lambda x: x.safety_score, reverse=True)
    return leaderboard

@router.get("/{bus_id}", response_model=BusResponse, summary="Get single bus telemetry status")
def get_bus_by_id(bus_id: str, db: Session = Depends(get_db)):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found.")
    return bus

@router.patch("/{bus_id}", response_model=BusResponse, summary="Update bus position, speed, or driver score")
def update_bus(bus_id: str, payload: BusUpdate, db: Session = Depends(get_db)):
    bus = db.query(Bus).filter(Bus.id == bus_id).first()
    if not bus:
        raise HTTPException(status_code=404, detail=f"Bus '{bus_id}' not found.")
        
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(bus, key, value)
        
    db.commit()
    db.refresh(bus)
    return bus
