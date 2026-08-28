from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from datetime import datetime
from app.db.base import Base

class RoadDocket(Base):
    __tablename__ = "road_dockets"

    id = Column(String(32), primary_key=True, index=True) # e.g. "INC-8924"
    defect_type = Column(String(64), nullable=False) # POTHOLE, WATERLOGGING, CRACK, EDGE_FAILURE
    severity = Column(String(32), nullable=False) # High, Moderate, Low, Critical
    status = Column(String(32), default="Pending Review") # Pending Review, In Progress, Resolved, Active Pursuit
    
    # Location
    location_name = Column(String(256), nullable=False)
    ward_number = Column(Integer, default=1)
    corridor = Column(String(128), default="Arterial Corridor 1")
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    
    # Detection Metrics
    detected_by_bus = Column(String(32), ForeignKey("buses.id"), nullable=False)
    confidence = Column(Float, nullable=False) # 0.0 - 1.0 (e.g. 0.968)
    depth_cm = Column(Float, default=0.0)
    estimated_volume_m3 = Column(Float, default=0.0)
    imu_shock_g = Column(Float, default=1.0) # Z-axis peak shock (e.g. 3.2g)
    
    # Financial & Engineering
    asphalt_tonnage_mt = Column(Float, default=0.0) # Hot-Mix MT
    repair_cost_inr = Column(Float, default=0.0) # Estimated repair budget
    assigned_contractor = Column(String(128), nullable=True)
    sla_target_hours = Column(Integer, default=48)
    
    # Notes & Media
    notes = Column(Text, nullable=True)
    snapshot_url = Column(String(512), nullable=True)
    
    detected_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)

