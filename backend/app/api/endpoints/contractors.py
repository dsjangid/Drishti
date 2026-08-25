from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, ConfigDict

from app.db.session import get_db
from app.models.contractor import Contractor

router = APIRouter()

class ContractorResponse(BaseModel):
    id: str
    name: str
    assigned_wards: str
    total_assigned_dockets: int
    resolved_on_time: int
    delayed_count: int
    sla_compliance_rate: float
    quality_grade: str
    avg_turnaround_hours: float

    model_config = ConfigDict(from_attributes=True)

@router.get("", response_model=List[ContractorResponse], summary="List all municipal road repair contractors & SLA grades")
def get_contractors(db: Session = Depends(get_db)):
    return db.query(Contractor).order_by(Contractor.sla_compliance_rate.desc()).all()

@router.get("/{contractor_id}", response_model=ContractorResponse, summary="Get single contractor scorecard")
def get_contractor_by_id(contractor_id: str, db: Session = Depends(get_db)):
    contractor = db.query(Contractor).filter(Contractor.id == contractor_id).first()
    if not contractor:
        raise HTTPException(status_code=404, detail=f"Contractor '{contractor_id}' not found.")
    return contractor
