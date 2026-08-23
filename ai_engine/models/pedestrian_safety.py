"""
JUCC Edge AI Engine - Vulnerable Pedestrian & School Zone Safety
Module: ai_engine/models/pedestrian_safety.py
Smart India Hackathon Problem Statement PS-26124

Calculates near-miss probability, Time-to-Collision (TTC),
and school zone pedestrian risk scores with automated municipal safety recommendations.
"""

from typing import List, Dict, Any, Tuple
import numpy as np


class PedestrianSafetyAnalyzer:
    """
    Evaluates pedestrian spatial proximity, crossing intent, and near-miss risk.
    """

    # Critical Jaipur School & Crossing Zones
    HIGH_RISK_ZONES = {
        "St. Xavier School (Bhagwan Das Rd)": {"base_risk": 87, "rec": "Install Automated Pelican Signal & School Warning Beacon"},
        "Rajasthan University Gate (JLN Marg)": {"base_risk": 82, "rec": "Deploy Raised Speed Table & Zebra Repainting"},
        "SMS Hospital Crossing": {"base_risk": 85, "rec": "Pedestrian Overhead Footbridge & High-Visibility Kerb Ramps"},
        "Choti Chaupar Heritage Arcade": {"base_risk": 79, "rec": "Dedicated E-Rickshaw Drop Bay & Bollard Lane Separation"}
    }

    def __init__(self, bus_speed_kmh: float = 30.0):
        self.bus_speed_kmh = bus_speed_kmh

    def evaluate_pedestrian_risks(
        self,
        pedestrian_detections: List[Dict[str, Any]],
        bus_speed_kmh: float,
        current_location: str = "JLN Marg near RU Gate"
    ) -> List[Dict[str, Any]]:
        """
        Evaluates risk score and Time-To-Collision (TTC) for every detected pedestrian.
        """
        bus_speed_ms = bus_speed_kmh / 3.6
        risk_reports = []

        for ped in pedestrian_detections:
            dist_m = ped.get("distance_m", 5.0)
            box = ped.get("box", [0, 0, 50, 100])
            conf = ped.get("confidence", 90.0)

            # Time-to-Collision Calculation (TTC = Distance / Relative Velocity)
            ttc_seconds = dist_m / max(1.0, bus_speed_ms)
            
            # Risk score calculation (0 - 100)
            if ttc_seconds < 1.8 or dist_m < 2.5:
                risk_level = "CRITICAL_NEAR_MISS"
                risk_score = min(99, int(90 + (2.5 - min(2.5, dist_m)) * 4.0))
            elif ttc_seconds < 3.5 or dist_m < 5.0:
                risk_level = "HIGH_ALERT"
                risk_score = min(88, int(70 + (5.0 - dist_m) * 3.5))
            else:
                risk_level = "SAFE_MARGIN"
                risk_score = max(10, int(40 - dist_m * 2))

            # Matched location recommendation
            matched_rec = "Maintain Standard Crossing Vigilance"
            for zone_name, zone_data in self.HIGH_RISK_ZONES.items():
                if any(k.lower() in current_location.lower() for k in zone_name.split()[:2]):
                    matched_rec = zone_data["rec"]
                    break

            risk_reports.append({
                "pedestrian_box": box,
                "confidence": conf,
                "distance_meters": dist_m,
                "time_to_collision_sec": round(ttc_seconds, 2),
                "risk_score": risk_score,
                "risk_level": risk_level,
                "recommended_intervention": matched_rec,
                "requires_audio_buzzer": (risk_score >= 80)
            })

        return risk_reports
