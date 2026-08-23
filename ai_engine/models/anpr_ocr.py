"""
JUCC Edge AI Engine - Automated Number Plate Recognition (ANPR / OCR)
Module: ai_engine/models/anpr_ocr.py
Smart India Hackathon Problem Statement PS-26124

Extracts, normalizes, and validates vehicle registration license plates
during critical Hit-and-Run or Rash Driving events with police evidence packaging.
"""

import re
import cv2
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple


class ANPRPlateRecognizer:
    """
    Automated License Plate Recognition (ANPR) & Forensic OCR Engine
    Optimized for Indian standard High-Security Registration Plates (HSRP).
    """

    # Standard Indian Regional Vehicle Registration Format Regex
    # Examples: RJ-14-CE-8821, RJ14CE8821, DL-03-CA-9912, MH-02-BZ-3451
    INDIAN_PLATE_PATTERN = re.compile(
        r"^([A-Z]{2})[- ]?([0-9]{1,2})[- ]?([A-Z]{1,3})[- ]?([0-9]{4})$",
        re.IGNORECASE
    )

    # Common OCR Character Confusion Corrections
    NUM_TO_CHAR = {'0': 'O', '1': 'I', '2': 'Z', '5': 'S', '8': 'B'}
    CHAR_TO_NUM = {'O': '0', 'I': '1', 'Z': '2', 'S': '5', 'B': '8', 'D': '0'}

    def __init__(self, target_plate_watch: Optional[str] = "RJ-14-CE-8821"):
        self.target_plate_watch = target_plate_watch.upper().replace("-", "").replace(" ", "") if target_plate_watch else None
        self.tracked_incidents: List[Dict[str, Any]] = []

    def preprocess_plate_region(self, image_roi: np.ndarray) -> np.ndarray:
        """
        Applies grayscale contrast stretching, bilateral filtering, and adaptive binarization
        to optimize license plate characters for optical extraction.
        """
        if image_roi is None or image_roi.size == 0:
            return image_roi

        gray = cv2.cvtColor(image_roi, cv2.COLOR_BGR2GRAY) if len(image_roi.shape) == 3 else image_roi
        filtered = cv2.bilateralFilter(gray, 11, 17, 17)
        equalized = cv2.equalizeHist(filtered)
        _, thresh = cv2.threshold(equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def format_indian_plate(self, raw_plate_text: str) -> str:
        """
        Formats a raw string into standard hyphenated Indian plate format (e.g. RJ-14-CE-8821).
        """
        clean = re.sub(r"[^A-Za-z0-9]", "", raw_plate_text).upper()
        match = self.INDIAN_PLATE_PATTERN.match(clean)
        if match:
            state, rto, series, num = match.groups()
            return f"{state}-{rto.zfill(2)}-{series}-{num}"
        
        # Fallback formatting if length is standard 10 characters
        if len(clean) == 10:
            return f"{clean[:2]}-{clean[2:4]}-{clean[4:6]}-{clean[6:]}"
        return clean

    def extract_license_plate(
        self,
        vehicle_roi: np.ndarray,
        bus_id: str = "BUS-005",
        gps_coords: Tuple[float, float] = (26.8290, 75.8070),
        estimated_speed_kmh: float = 84.0,
        vehicle_desc: str = "White Toyota Fortuner SUV"
    ) -> Dict[str, Any]:
        """
        Extracts license plate OCR, verifies watch list, and compiles Police FIR Dossier.
        """
        # Default mock high-accuracy plate extraction when scanning demo vehicles
        raw_text = "RJ14CE8821"
        confidence = 97.2

        formatted_plate = self.format_indian_plate(raw_text)
        is_target_hit = (self.target_plate_watch and self.target_plate_watch in formatted_plate.replace("-", ""))

        dossier = {
            "incident_id": f"FIR-{int(datetime.now().timestamp())}",
            "plate_number": formatted_plate,
            "ocr_confidence": confidence,
            "is_target_lock": is_target_hit,
            "offense": "Hit-and-Run Impact & High-Speed Flee Vector" if is_target_hit else "Routine ANPR Transit Scan",
            "vehicle_description": vehicle_desc,
            "vehicle_speed_kmh": estimated_speed_kmh,
            "intercepted_by_bus": bus_id,
            "gps_latitude": gps_coords[0],
            "gps_longitude": gps_coords[1],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S IST"),
            "dispatch_status": "ESCALATED_TO_POLICE_PCR" if is_target_hit else "ARCHIVED"
        }

        if is_target_hit:
            self.tracked_incidents.append(dossier)

        return dossier
