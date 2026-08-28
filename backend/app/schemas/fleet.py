from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class BusBase(BaseModel):
    id: str = Field(..., json_schema_extra={"example": "BUS-001"})
    driver_name: str = Field(..., json_schema_extra={"example": "Rajesh Sharma"})
    driver_phone: Optional[str] = Field(None, json_schema_extra={"example": "+91 98290 11234"})
    driver_safety_score: int = Field(85, ge=0, le=100)
    route_name: str = Field(..., json_schema_extra={"example": "Route 1: Central Spine Arterial"})
    corridor_type: str = Field("Arterial", json_schema_extra={"example": "Arterial"})
    current_lat: float = Field(..., json_schema_extra={"example": 26.9124})
    current_lng: float = Field(..., json_schema_extra={"example": 75.7873})
    current_speed: float = Field(0.0, json_schema_extra={"example": 32.5})
    is_active: bool = Field(True)
    edge_device: str = Field("NVIDIA Jetson Orin Nano")
    npu_temp_c: float = Field(45.0, json_schema_extra={"example": 48.2})
    inference_fps: float = Field(18.5, json_schema_extra={"example": 19.1})
    latency_ms: float = Field(14.8, json_schema_extra={"example": 14.8})
    cellular_signal: str = Field("98% (4G LTE)")

class BusCreate(BusBase):
    pass

class BusUpdate(BaseModel):
    driver_name: Optional[str] = None
    driver_safety_score: Optional[int] = None
    current_lat: Optional[float] = None
    current_lng: Optional[float] = None
    current_speed: Optional[float] = None
    is_active: Optional[bool] = None
    npu_temp_c: Optional[float] = None
    inference_fps: Optional[float] = None
    latency_ms: Optional[float] = None
    cellular_signal: Optional[str] = None

class BusResponse(BusBase):
    model_config = ConfigDict(from_attributes=True)
    updated_at: datetime

class DriverLeaderboardItem(BaseModel):
    bus_id: str
    driver_name: str
    safety_score: int
    grade: str
    risk_level: str
    recent_events: int

