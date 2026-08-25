from pydantic import BaseModel, Field
from typing import List, Dict, Any

class GeoJSONGeometry(BaseModel):
    type: str = "Point"
    coordinates: List[float] # [lng, lat]

class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONGeometry
    properties: Dict[str, Any]

class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]

class TrafficHourVolume(BaseModel):
    hour_label: str # "08:00", "09:00"
    pcu_volume: int
    avg_speed_kmh: float
    congestion_index: float # 0.0 - 1.0

class WardDefectAggregate(BaseModel):
    ward_number: int
    ward_name: str
    active_defects: int
    resolved_defects: int
    critical_potholes: int
    hotmix_required_mt: float
