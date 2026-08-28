from sqlalchemy import Column, String, Integer, Float
from app.db.base import Base

class Contractor(Base):
    __tablename__ = "contractors"

    id = Column(String(32), primary_key=True, index=True) # e.g. "CON-01"
    name = Column(String(128), nullable=False)
    assigned_wards = Column(String(128), default="1,2,3,4,5")
    total_assigned_dockets = Column(Integer, default=0)
    resolved_on_time = Column(Integer, default=0)
    delayed_count = Column(Integer, default=0)
    sla_compliance_rate = Column(Float, default=94.5) # Percentage
    quality_grade = Column(String(8), default="A+")
    avg_turnaround_hours = Column(Float, default=18.2)

