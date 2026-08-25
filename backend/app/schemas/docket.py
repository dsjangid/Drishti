from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class DocketBase(BaseModel):
    defect_type: str = Field(..., json_schema_extra={"example": "POTHOLE"})
    severity: str = Field("Moderate", json_schema_extra={"example": "High"})
    status: str = Field("Pending Review", json_schema_extra={"example": "Pending Review"})
    location_name: str = Field(..., json_schema_extra={"example": "Corridor 1 · KM 4.2 Northbound"})
    ward_number: int = Field(1, ge=1, le=100)
    corridor: str = Field("Arterial Corridor 1")
    lat: float = Field(..., json_schema_extra={"example": 26.8850})
    lng: float = Field(..., json_schema_extra={"example": 75.8000})
    detected_by_bus: str = Field(..., json_schema_extra={"example": "BUS-003"})
    confidence: float = Field(..., ge=0.0, le=1.0, json_schema_extra={"example": 0.964})
    depth_cm: float = Field(0.0, json_schema_extra={"example": 16.4})
    estimated_volume_m3: float = Field(0.0, json_schema_extra={"example": 0.18})
    imu_shock_g: float = Field(1.0, json_schema_extra={"example": 3.2})
    assigned_contractor: Optional[str] = Field("Municipal Smart City Ltd")
    sla_target_hours: int = Field(48)
    notes: Optional[str] = None
    snapshot_url: Optional[str] = None

class DocketCreate(DocketBase):
    id: Optional[str] = Field(None, json_schema_extra={"example": "INC-8924"})

class DocketUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    assigned_contractor: Optional[str] = None
    notes: Optional[str] = None
    resolved_at: Optional[datetime] = None

class DocketResponse(DocketBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    asphalt_tonnage_mt: float
    repair_cost_inr: float
    detected_at: datetime
    resolved_at: Optional[datetime] = None

class DocketSummaryStats(BaseModel):
    total_dockets: int
    pending_review: int
    in_progress: int
    resolved_today: int
    active_pursuits: int
    critical_count: int
    estimated_total_repair_inr: float
    total_asphalt_tonnage_mt: float
