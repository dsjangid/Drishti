from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from app.db.base import Base

class TelemetryLog(Base):
    __tablename__ = "telemetry_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    bus_id = Column(String(32), ForeignKey("buses.id"), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    speed_kmh = Column(Float, default=0.0)
    heading_deg = Column(Float, default=0.0)
    
    # 6-Axis IMU Z-axis spike
    imu_z_accel_g = Column(Float, default=1.0)
    imu_vibration_rms = Column(Float, default=0.1)
    
    # Traffic flow PCU
    pcu_flow_count = Column(Integer, default=0)
    detected_objects_count = Column(Integer, default=0)
