"""
JUCC Edge AI Engine - Driver Behavior & Cabin Monitoring System (DMS)
Module: ai_engine/models/driver_behavior.py
Smart India Hackathon Problem Statement PS-26124

Monitors driver fatigue, Eye Aspect Ratio (EAR), mobile distraction,
and IMU sensor telemetry (harsh braking & acceleration).
"""

from typing import Dict, Any, List
import numpy as np


class DriverSafetyIndexCalculator:
    """
    Evaluates driver attention, fatigue index, and safety score (0 - 100).
    """

    def __init__(self, driver_name: str = "Rajesh Sharma", base_score: int = 95):
        self.driver_name = driver_name
        self.safety_score = base_score
        self.harsh_braking_events = 0
        self.fatigue_events = 0
        self.phone_distraction_events = 0

    def evaluate_cabin_frame(
        self,
        eye_aspect_ratio: float = 0.28,
        seatbelt_latched: bool = True,
        phone_detected: bool = False,
        head_yaw_angle: float = 0.0,
        imu_decel_g: float = 0.0
    ) -> Dict[str, Any]:
        """
        Processes a single cabin DMS sensor frame.
        - Normal EAR > 0.25 (Alert)
        - Drowsy EAR < 0.20 for > 2.0 seconds (Warning)
        - Deceleration < -0.55g logs harsh braking
        """
        is_drowsy = eye_aspect_ratio < 0.20
        is_distracted = phone_detected or abs(head_yaw_angle) > 25.0
        is_harsh_braking = imu_decel_g < -0.55

        # Score deduction penalties
        if is_drowsy:
            self.fatigue_events += 1
            self.safety_score = max(40, self.safety_score - 2)

        if is_distracted:
            self.phone_distraction_events += 1
            self.safety_score = max(40, self.safety_score - 3)

        if is_harsh_braking:
            self.harsh_braking_events += 1
            self.safety_score = max(40, self.safety_score - 2)

        # Status category
        if self.safety_score >= 90:
            status = "EXEMPLARY"
        elif self.safety_score >= 75:
            status = "NORMAL"
        elif self.safety_score >= 60:
            status = "CAUTION"
        else:
            status = "HIGH_RISK_MANDATORY_TRAINING"

        return {
            "driver_name": self.driver_name,
            "safety_score": self.safety_score,
            "status": status,
            "eye_aspect_ratio": round(eye_aspect_ratio, 2),
            "seatbelt_latched": seatbelt_latched,
            "drowsiness_flag": is_drowsy,
            "distraction_flag": is_distracted,
            "harsh_braking_count": self.harsh_braking_events,
            "requires_audio_buzzer": is_drowsy or is_distracted
        }
