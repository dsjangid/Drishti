from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class TelemetryIngest(BaseModel):
    bus_id: str = Field(..., json_schema_extra={"example": "BUS-003"})
    lat: float = Field(..., json_schema_extra={"example": 26.8850})
    lng: float = Field(..., json_schema_extra={"example": 75.8000})
    speed_kmh: float = Field(0.0, json_schema_extra={"example": 34.2})
    heading_deg: float = Field(0.0, json_schema_extra={"example": 182.5})
    
    # 6-Axis IMU
    imu_z_accel_g: float = Field(1.0, json_schema_extra={"example": 3.4})
    imu_vibration_rms: float = Field(0.1, json_schema_extra={"example": 0.25})
    
    # Optional Edge AI Defect Event attached to telemetry packet
    defect_detected: Optional[bool] = Field(False)
    defect_type: Optional[str] = Field(None, json_schema_extra={"example": "POTHOLE"})
    defect_confidence: Optional[float] = Field(None, json_schema_extra={"example": 0.968})
    defect_depth_cm: Optional[float] = Field(None, json_schema_extra={"example": 16.2})

class TelemetryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bus_id: str
    timestamp: datetime
    lat: float
    lng: float
    speed_kmh: float
    imu_z_accel_g: float

class LiveMapBusPacket(BaseModel):
    bus_id: str
    driver_name: str
    route_name: str
    lat: float
    lng: float
    speed: float
    safety_score: int
    is_active: bool
