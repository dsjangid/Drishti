from sqlalchemy.orm import Session
from app.models.bus import Bus
from app.models.docket import RoadDocket
from app.models.contractor import Contractor
from app.services.cost_calculator import IRCCostCalculator

SEED_BUSES = [
    {"id": "BUS-001", "driver_name": "Rajesh Sharma", "driver_phone": "+91 98290 11001", "driver_safety_score": 92, "route_name": "Route 1: Central Spine Arterial", "corridor_type": "Arterial", "current_lat": 26.9239, "current_lng": 75.8267, "current_speed": 28.5},
    {"id": "BUS-002", "driver_name": "Vikram Singh", "driver_phone": "+91 98290 11002", "driver_safety_score": 88, "route_name": "Route 2: 200ft Bypass Express", "corridor_type": "Bypass", "current_lat": 26.8950, "current_lng": 75.7450, "current_speed": 34.0},
    {"id": "BUS-003", "driver_name": "Manoj Meena", "driver_phone": "+91 98290 11003", "driver_safety_score": 78, "route_name": "Route 3: South Arterial Corridor", "corridor_type": "Arterial", "current_lat": 26.9124, "current_lng": 75.7873, "current_speed": 22.0},
    {"id": "BUS-004", "driver_name": "Ramesh Gurjar", "driver_phone": "+91 98290 11004", "driver_safety_score": 95, "route_name": "Route 4: Institutional Hub North", "corridor_type": "Institutional", "current_lat": 26.9600, "current_lng": 75.7700, "current_speed": 31.0},
    {"id": "BUS-005", "driver_name": "Suresh Verma", "driver_phone": "+91 98290 11005", "driver_safety_score": 84, "route_name": "Route 5: Industrial Corridor Link", "corridor_type": "Industrial", "current_lat": 26.9200, "current_lng": 75.8300, "current_speed": 42.0},
    {"id": "BUS-006", "driver_name": "Anil Kumawat", "driver_phone": "+91 98290 11006", "driver_safety_score": 90, "route_name": "Route 6: Metro Interchange Ring", "corridor_type": "Arterial", "current_lat": 26.9180, "current_lng": 75.7800, "current_speed": 26.0},
    {"id": "BUS-007", "driver_name": "Dinesh Sharma", "driver_phone": "+91 98290 11007", "driver_safety_score": 74, "route_name": "Route 7: Sub-Arterial Crossway", "corridor_type": "Sub-Arterial", "current_lat": 26.8600, "current_lng": 75.7700, "current_speed": 29.0},
    {"id": "BUS-008", "driver_name": "Sunil Yadav", "driver_phone": "+91 98290 11008", "driver_safety_score": 86, "route_name": "Route 8: Airport Expressway", "corridor_type": "Expressway", "current_lat": 26.9350, "current_lng": 75.7850, "current_speed": 35.0},
    {"id": "BUS-009", "driver_name": "Praveen Bairwa", "driver_phone": "+91 98290 11009", "driver_safety_score": 81, "route_name": "Route 9: Ring Road Bypass Sector 4", "corridor_type": "Bypass", "current_lat": 26.8750, "current_lng": 75.8200, "current_speed": 18.0},
    {"id": "BUS-010", "driver_name": "Mahesh Choudhary", "driver_phone": "+91 98290 11010", "driver_safety_score": 89, "route_name": "Route 10: Heritage Transit Loop", "corridor_type": "Institutional", "current_lat": 26.9400, "current_lng": 75.8100, "current_speed": 14.0},
]

SEED_CONTRACTORS = [
    {"id": "CON-01", "name": "Municipal Smart City Infrastructure Ltd", "assigned_wards": "1,2,3,4,8,12", "total_assigned_dockets": 48, "resolved_on_time": 46, "delayed_count": 2, "sla_compliance_rate": 95.8, "quality_grade": "A+", "avg_turnaround_hours": 16.4},
    {"id": "CON-02", "name": "Apex Urban Road Infra JV", "assigned_wards": "5,6,7,9,10", "total_assigned_dockets": 32, "resolved_on_time": 29, "delayed_count": 3, "sla_compliance_rate": 90.6, "quality_grade": "A", "avg_turnaround_hours": 21.0},
    {"id": "CON-03", "name": "Bharat Highway Maintenance Corp", "assigned_wards": "11,13,14,15,16", "total_assigned_dockets": 24, "resolved_on_time": 21, "delayed_count": 3, "sla_compliance_rate": 87.5, "quality_grade": "B+", "avg_turnaround_hours": 26.5},
    {"id": "CON-04", "name": "Urban Rapid Paving Solutions", "assigned_wards": "17,18,19,20", "total_assigned_dockets": 18, "resolved_on_time": 18, "delayed_count": 0, "sla_compliance_rate": 100.0, "quality_grade": "A+", "avg_turnaround_hours": 11.2},
]

SEED_DOCKETS = [
    {"id": "INC-8924", "defect_type": "POTHOLE", "severity": "High", "status": "Pending Review", "location_name": "Corridor 1 · KM 4.2 Northbound", "ward_number": 12, "corridor": "Arterial Corridor 1", "lat": 26.8850, "lng": 75.7900, "detected_by_bus": "BUS-003", "confidence": 0.964, "depth_cm": 16.4, "imu_shock_g": 3.2, "assigned_contractor": "Municipal Smart City Infrastructure Ltd"},
    {"id": "INC-8925", "defect_type": "WATERLOGGED_SHOULDER", "severity": "Moderate", "status": "Pending Review", "location_name": "Bypass Crossway · KM 7.1", "ward_number": 8, "corridor": "200ft Bypass", "lat": 26.8800, "lng": 75.7720, "detected_by_bus": "BUS-002", "confidence": 0.948, "depth_cm": 22.0, "imu_shock_g": 1.8, "assigned_contractor": "Apex Urban Road Infra JV"},
    {"id": "INC-8926", "defect_type": "POTHOLE", "severity": "Critical", "status": "Active Pursuit", "location_name": "South Arterial · Central Lane", "ward_number": 14, "corridor": "South Arterial", "lat": 26.8450, "lng": 75.8150, "detected_by_bus": "BUS-003", "confidence": 0.982, "depth_cm": 18.5, "imu_shock_g": 3.4, "assigned_contractor": "Municipal Smart City Infrastructure Ltd"},
    {"id": "INC-8927", "defect_type": "EDGE_FAILURE", "severity": "Moderate", "status": "Pending Review", "location_name": "Institutional Hub · Sector 3", "ward_number": 4, "corridor": "Institutional North", "lat": 26.9300, "lng": 75.7920, "detected_by_bus": "BUS-004", "confidence": 0.956, "depth_cm": 12.4, "imu_shock_g": 1.2, "assigned_contractor": "Apex Urban Road Infra JV"},
    {"id": "INC-8928", "defect_type": "POTHOLE", "severity": "Moderate", "status": "Resolved", "location_name": "Industrial Link · Junction 9", "ward_number": 18, "corridor": "Industrial Link", "lat": 26.9000, "lng": 75.8600, "detected_by_bus": "BUS-005", "confidence": 0.924, "depth_cm": 9.5, "imu_shock_g": 1.5, "assigned_contractor": "Urban Rapid Paving Solutions"},
    {"id": "INC-8929", "defect_type": "RAVELING", "severity": "Low", "status": "Resolved", "location_name": "Metro Interchange · West Flyover", "ward_number": 6, "corridor": "Metro Ring", "lat": 26.9020, "lng": 75.7500, "detected_by_bus": "BUS-006", "confidence": 0.910, "depth_cm": 4.5, "imu_shock_g": 0.8, "assigned_contractor": "Bharat Highway Maintenance Corp"},
    {"id": "INC-8930", "defect_type": "POTHOLE", "severity": "High", "status": "In Progress", "location_name": "Airport Expressway · KM 2.4", "ward_number": 11, "corridor": "Airport Expressway", "lat": 26.9100, "lng": 75.8120, "detected_by_bus": "BUS-008", "confidence": 0.971, "depth_cm": 15.2, "imu_shock_g": 2.9, "assigned_contractor": "Municipal Smart City Infrastructure Ltd"},
    {"id": "INC-8931", "defect_type": "WATERLOGGED_SHOULDER", "severity": "Low", "status": "Resolved", "location_name": "Heritage Transit Loop · South Gate", "ward_number": 1, "corridor": "Heritage Loop", "lat": 26.9200, "lng": 75.8300, "detected_by_bus": "BUS-010", "confidence": 0.935, "depth_cm": 8.0, "imu_shock_g": 1.1, "assigned_contractor": "Urban Rapid Paving Solutions"},
]

def seed_database(db: Session):
    """Populates empty database with initial municipal data."""
    if db.query(Bus).count() == 0:
        for b in SEED_BUSES:
            db.add(Bus(**b))
            
    if db.query(Contractor).count() == 0:
        for c in SEED_CONTRACTORS:
            db.add(Contractor(**c))
            
    if db.query(RoadDocket).count() == 0:
        for d in SEED_DOCKETS:
            metrics = IRCCostCalculator.calculate_repair_metrics(
                depth_cm=d["depth_cm"],
                defect_type=d["defect_type"]
            )
            docket_obj = RoadDocket(
                **d,
                estimated_volume_m3=metrics["volume_m3"],
                asphalt_tonnage_mt=metrics["tonnage_mt"],
                repair_cost_inr=metrics["estimated_cost_inr"]
            )
            db.add(docket_obj)
            
    db.commit()
