from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from datetime import datetime
from app.db.base import Base

class Bus(Base):
    __tablename__ = "buses"

    id = Column(String(32), primary_key=True, index=True) # e.g. "BUS-001"
    driver_name = Column(String(128), nullable=False)
    driver_phone = Column(String(32), nullable=True)
    driver_safety_score = Column(Integer, default=85) # 0-100 score
    route_name = Column(String(128), nullable=False)
    corridor_type = Column(String(64), default="Arterial")
    
    # Real-time state
    current_lat = Column(Float, nullable=False)
    current_lng = Column(Float, nullable=False)
    current_speed = Column(Float, default=0.0) # km/h
    is_active = Column(Boolean, default=True)
    
    # Hardware Telemetry (Edge NPU Jetson)
    edge_device = Column(String(64), default="NVIDIA Jetson Orin Nano")
    npu_temp_c = Column(Float, default=45.0)
    inference_fps = Column(Float, default=18.5)
    latency_ms = Column(Float, default=14.8)
    cellular_signal = Column(String(32), default="98% (4G LTE)")
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
