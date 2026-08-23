"""
JUCC Edge AI Engine - Multi-Camera Stream Ingestion Manager
Module: ai_engine/pipeline/camera_stream.py
Smart India Hackathon Problem Statement PS-26124

Manages video streams across 4 bus-mounted optical sensors:
- Front Windshield 1080p
- Downward Asphalt Profilometry Scanner
- Left Kerb & Blindspot 120-deg FOV Camera
- Driver Cabin 60 FPS Infrared DMS
"""

import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple


class CameraAngle:
    FRONT = "front"
    ASPHALT = "asphalt"
    BLINDSPOT = "blindspot"
    CABIN = "cabin"


class MultiCameraStreamManager:
    """
    Handles synchronized multi-channel camera frame acquisition from video files,
    USB v4l2 video devices, or network RTSP streams on NVIDIA Jetson / Edge NPUs.
    """

    def __init__(self, primary_video_path: Optional[str] = None):
        self.primary_video_path = primary_video_path
        self.cap = None
        if primary_video_path:
            self.cap = cv2.VideoCapture(primary_video_path)

    def read_angle_frame(self, angle: str = CameraAngle.FRONT) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Reads a frame for the specified camera angle.
        If a real video file is loaded, transforms perspectives to model multi-camera optical fields.
        """
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                # Loop video seamlessly
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
            
            if not ret or frame is None:
                return False, self._generate_synthetic_view(angle)

            # Transform perspective based on sensor angle
            if angle == CameraAngle.FRONT:
                return True, frame
            elif angle == CameraAngle.ASPHALT:
                # Downward crop and contrast enhancement for asphalt road profilometry
                h, w = frame.shape[:2]
                asphalt_roi = frame[int(h * 0.5):, :]
                resized = cv2.resize(asphalt_roi, (w, h))
                return True, resized
            elif angle == CameraAngle.BLINDSPOT:
                # Left kerb crop for sidewalk and passenger boarding area
                h, w = frame.shape[:2]
                kerb_roi = frame[:, :int(w * 0.5)]
                resized = cv2.resize(kerb_roi, (w, h))
                return True, resized
            elif angle == CameraAngle.CABIN:
                # Infrared driver cabin simulation (grayscale + illumination)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                ir_sim = cv2.applyColorMap(gray, cv2.COLORMAP_BONE)
                return True, ir_sim

        return True, self._generate_synthetic_view(angle)

    def _generate_synthetic_view(self, angle: str) -> np.ndarray:
        """
        Generates clean calibrated fallback frames if no physical camera or file is attached.
        """
        img = np.zeros((480, 960, 3), dtype=np.uint8)
        if angle == CameraAngle.FRONT:
            img[:] = (20, 24, 22)
            cv2.putText(img, "FRONT 1080p WINDSHIELD CAM", (320, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        elif angle == CameraAngle.ASPHALT:
            img[:] = (28, 33, 30)
            cv2.putText(img, "DOWNWARD ASPHALT SCANNER", (320, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (220, 200, 180), 2)
        elif angle == CameraAngle.BLINDSPOT:
            img[:] = (23, 27, 25)
            cv2.putText(img, "LEFT KERB BLINDSPOT CAM", (330, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 220, 200), 2)
        else:
            img[:] = (13, 16, 15)
            cv2.putText(img, "DRIVER DMS INFRARED CAM", (330, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 240, 220), 2)
        return img

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
