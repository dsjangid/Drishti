from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from typing import List
import json

from app.db.session import get_db
from app.models.docket import RoadDocket
from app.schemas.analytics import GeoJSONFeatureCollection, TrafficHourVolume, WardDefectAggregate
from app.services.geojson_service import GeoJSONService

router = APIRouter()

@router.get("/geojson", response_model=GeoJSONFeatureCollection, summary="Export all road defects as standard RFC 7946 GeoJSON")
def export_geojson(db: Session = Depends(get_db)):
    dockets = db.query(RoadDocket).all()
    return GeoJSONService.dockets_to_geojson(dockets)

@router.get("/geojson/download", summary="Download defect layer as .geojson file")
def download_geojson(db: Session = Depends(get_db)):
    dockets = db.query(RoadDocket).all()
    geojson_data = GeoJSONService.dockets_to_geojson(dockets)
    content = json.dumps(geojson_data.dict(), indent=2)
    
    return Response(
        content=content,
        media_type="application/geo+json",
        headers={"Content-Disposition": 'attachment; filename="Drishti_Urban_Defects_Layer.geojson"'}
    )

@router.get("/traffic-curves", response_model=List[TrafficHourVolume], summary="24-Hour Passenger Car Unit (PCU) traffic flow curves")
def get_traffic_curves():
    # 24-hour diurnal urban traffic profile
    hours = ["06:00", "07:00", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00", 
             "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00"]
    volumes = [420, 850, 1420, 1890, 1650, 1200, 1150, 1220, 1310, 1450, 1780, 2150, 2300, 1980, 1420, 890]
    speeds = [45.0, 38.0, 24.5, 18.2, 22.0, 32.0, 34.0, 31.5, 30.0, 26.0, 19.5, 15.0, 14.2, 18.5, 28.0, 39.0]
    
    curve = []
    for h, v, s in zip(hours, volumes, speeds):
        congestion = round(min(1.0, max(0.1, v / 2500.0)), 2)
        curve.append(TrafficHourVolume(
            hour_label=h,
            pcu_volume=v,
            avg_speed_kmh=s,
            congestion_index=congestion
        ))
    return curve

@router.get("/ward-breakdown", response_model=List[WardDefectAggregate], summary="Ward-level road defect aggregations")
def get_ward_breakdown(db: Session = Depends(get_db)):
    dockets = db.query(RoadDocket).all()
    wards_map = {}
    
    for d in dockets:
        w_num = d.ward_number or 1
        if w_num not in wards_map:
            wards_map[w_num] = {
                "ward_number": w_num,
                "ward_name": f"Ward {w_num} (Municipal Zone {((w_num - 1) // 4) + 1})",
                "active_defects": 0,
                "resolved_defects": 0,
                "critical_potholes": 0,
                "hotmix_required_mt": 0.0
            }
        
        if d.status == "Resolved":
            wards_map[w_num]["resolved_defects"] += 1
        else:
            wards_map[w_num]["active_defects"] += 1
            wards_map[w_num]["hotmix_required_mt"] += d.asphalt_tonnage_mt
            
        if d.severity in ["Critical", "High"]:
            wards_map[w_num]["critical_potholes"] += 1

    result = [WardDefectAggregate(**data) for data in sorted(wards_map.values(), key=lambda x: x["ward_number"])]
    return result
