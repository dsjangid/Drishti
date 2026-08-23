"""
AI Engine Models Package
Includes iWatchRoad YOLOv8 Integration & Governance Architecture
"""

from ai_engine.models.defect_detector import RoadDefectDetector, DefectClass
from ai_engine.models.vehicle_analyzer import VehicleFlowAnalyzer, VehicleClass, TrafficCongestionLevel
from ai_engine.models.pedestrian_safety import PedestrianSafetyAnalyzer
from ai_engine.models.anpr_ocr import ANPRPlateRecognizer
from ai_engine.models.driver_behavior import DriverSafetyIndexCalculator
from ai_engine.models.iwatchroad_engine import (
    IWatchRoadDetector,
    IWatchRoadContractorTracker,
    DefectSeverityGrade,
    PotholeLifecycleStatus
)
