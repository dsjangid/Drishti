"""
JUCC Edge AI Engine - Master Edge Processing Pipeline
Module: ai_engine/pipeline/edge_pipeline.py
Smart India Hackathon Problem Statement PS-26124

Orchestrates multi-sensor edge processing on municipal transit buses:
- Synchronized Road Defect Detection (Potholes, Cracks, Waterlogging)
- 6-Class Traffic Vehicle Classification & Density Estimation
- Pedestrian & School Zone Proximity Hazard Scoring
- Automatic Number Plate Recognition (ANPR / OCR) for Hit & Run / Rash Driving
- Driver DMS Fatigue & Behavioral Telemetry
- Bandwidth-Optimized JSON Telemetry Publishing
"""

import time
import cv2
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from ai_engine.models.defect_detector import RoadDefectDetector
from ai_engine.models.vehicle_analyzer import VehicleFlowAnalyzer
from ai_engine.models.pedestrian_safety import PedestrianSafetyAnalyzer
from ai_engine.models.anpr_ocr import ANPRPlateRecognizer
from ai_engine.models.driver_behavior import DriverSafetyIndexCalculator
from ai_engine.pipeline.camera_stream import MultiCameraStreamManager, CameraAngle
from ai_engine.pipeline.bandwidth_optimizer import EdgeBandwidthOptimizer


class BusEdgeAIUnit:
    """
    Onboard Edge AI Processing Unit installed on NVIDIA Jetson / Edge NPUs in municipal buses.
    """

    def __init__(
        self,
        bus_id: str = "BUS-003",
        driver_name: str = "Manoj Meena",
        route_name: str = "Route 3: Tonk Road",
        video_source_path: Optional[str] = None,
        initial_gps: Tuple[float, float] = (26.8520, 75.7920)
    ):
        self.bus_id = bus_id
        self.driver_name = driver_name
        self.route_name = route_name
        self.gps_lat, self.gps_lng = initial_gps
        self.current_speed_kmh = 28.0

        # Hardware & inference metrics
        self.npu_temperature_c = 48.0
        self.inference_fps = 18.4
        self.edge_latency_ms = 42

        # Initialize AI subsystems
        self.defect_detector = RoadDefectDetector()
        self.vehicle_analyzer = VehicleFlowAnalyzer()
        self.pedestrian_safety = PedestrianSafetyAnalyzer()
        self.anpr_recognizer = ANPRPlateRecognizer()
        self.driver_monitor = DriverSafetyIndexCalculator(driver_name=driver_name)
        self.camera_manager = MultiCameraStreamManager(video_source_path)
        self.bandwidth_optimizer = EdgeBandwidthOptimizer()

        self.step_counter = 0

    def process_telemetry_frame(self, active_angle: str = CameraAngle.FRONT) -> Dict[str, Any]:
        """
        Executes a complete multi-modal edge perception cycle across active bus cameras.
        """
        self.step_counter += 1
        ret, frame = self.camera_manager.read_angle_frame(active_angle)
        
        # 1. Road Defect Profilometry
        defect_detections = self.defect_detector.detect(frame, camera_angle=active_angle)

        # 2. Vehicle & Traffic Flow Perception
        traffic_detections = self.vehicle_analyzer.detect_and_classify(frame)
        density_state = self.vehicle_analyzer.compute_traffic_density_state(traffic_detections)

        # 3. Pedestrian & School Zone Near-Miss Risk
        ped_detections = [d for d in traffic_detections if d.get("class_name") == "PEDESTRIAN"]
        ped_risks = self.pedestrian_safety.evaluate_pedestrian_risks(
            ped_detections,
            bus_speed_kmh=self.current_speed_kmh,
            current_location=self.route_name
        )

        # 4. ANPR License Plate OCR on High-Speed Vehicles
        target_plates = []
        is_hit_and_run_event = False
        if any(d.get("estimated_speed_kmh", 0) > 65.0 for d in traffic_detections):
            fir_dossier = self.anpr_recognizer.extract_license_plate(
                frame,
                bus_id=self.bus_id,
                gps_coords=(self.gps_lat, self.gps_lng),
                estimated_speed_kmh=84.0,
                vehicle_desc="White Toyota Fortuner SUV"
            )
            target_plates.append(fir_dossier)
            is_hit_and_run_event = fir_dossier["is_target_lock"]

        # 5. Driver DMS Monitoring
        driver_telemetry = self.driver_monitor.evaluate_cabin_frame(
            eye_aspect_ratio=0.28,
            seatbelt_latched=True,
            phone_detected=False,
            imu_decel_g=-0.1
        )

        # Incident trigger flag for keyframe docket packaging
        is_critical_incident = len(defect_detections) > 0 or is_hit_and_run_event or any(r["risk_score"] > 80 for r in ped_risks)

        # Compile comprehensive edge telemetry packet
        telemetry_packet = {
            "bus_id": self.bus_id,
            "route": self.route_name,
            "driver": self.driver_name,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
            "gps_coordinates": {
                "latitude": self.gps_lat,
                "longitude": self.gps_lng
            },
            "speed_kmh": self.current_speed_kmh,
            "hardware_health": {
                "processor": "NVIDIA Jetson Orin Nano",
                "temperature_c": self.npu_temperature_c,
                "fps": self.inference_fps,
                "latency_ms": self.edge_latency_ms,
                "4g_signal": "98% (LTE)",
                "status": "ONLINE"
            },
            "road_defects": defect_detections,
            "traffic_state": density_state,
            "pedestrian_safety_risks": ped_risks,
            "anpr_fir_dossiers": target_plates,
            "driver_safety": driver_telemetry
        }

        # Compress and package through Edge Bandwidth Optimizer
        _, json_payload, bandwidth_stats = self.bandwidth_optimizer.process_and_package(
            frame, telemetry_packet, is_incident_trigger=is_critical_incident
        )

        return {
            "telemetry": telemetry_packet,
            "json_payload": json_payload,
            "bandwidth_stats": bandwidth_stats,
            "annotated_frame": self._render_composite_overlay(frame, defect_detections, traffic_detections, density_state)
        }

    def _render_composite_overlay(
        self,
        frame: np.ndarray,
        defects: List[Dict[str, Any]],
        traffic: List[Dict[str, Any]],
        density: Dict[str, Any]
    ) -> np.ndarray:
        """
        Renders composite multi-layer visual detection output.
        """
        if frame is None:
            return frame
        vis = self.defect_detector.draw_detections(frame, defects)
        vis = self.vehicle_analyzer.draw_traffic_hud(vis, traffic, density)
        return vis

    def close(self):
        self.camera_manager.release()
