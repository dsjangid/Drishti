"""
JUCC Edge AI Engine - High-Accuracy YOLOv8 Neural Inference Pipeline
Module: ai_engine/run_inference.py

Performs deep learning inference on road dashcam video feeds using
trained YOLOv8 weights (ONNX / PyTorch), extracts verified potholes,
eliminates optical false positives, and grades defect severity.
"""

import os
import sys
import json
import time
import argparse
import numpy as np
import cv2


MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "models/weights/pothole_yolov8.onnx"))


class DeepPotholeInferenceEngine:
    def __init__(self, model_path: str = MODEL_PATH, conf_thresh: float = 0.55, iou_thresh: float = 0.45):
        self.model_path = model_path
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        self.net = None

        if os.path.exists(model_path):
            print(f"[✓] Loading YOLOv8 Neural Network weights from {model_path}...")
            try:
                self.net = cv2.dnn.readNetFromONNX(model_path)
                self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                print("[✓] YOLOv8 Neural Network initialized successfully.")
            except Exception as e:
                print(f"[!] Note loading OpenCV DNN ONNX: {e}")
        else:
            print(f"[!] Model weights not found at {model_path}")

    def is_within_road_horizontal_bounds(self, cx: float, cy: float, w: int, h: int) -> bool:
        """Calculates dynamic horizontal road boundaries [x_left(y), x_right(y)] from perspective trapezoid."""
        y_top = int(h * 0.50)
        y_bottom = int(h * 0.98)
        if cy < y_top or cy > y_bottom:
            return False

        progress = (cy - y_top) / max(1, (y_bottom - y_top))
        # Centered Drivable Asphalt Corridor: 20% at horizon -> 8% at bumper
        left_bound = int(w * (0.20 - 0.12 * progress))
        right_bound = int(w * (0.80 + 0.12 * progress))

        return left_bound <= cx <= right_bound

    def process_frame(self, frame: np.ndarray):
        """Run deep learning neural inference on a single frame."""
        if frame is None:
            return []

        h, w = frame.shape[:2]

        if self.net is not None:
            # Preprocess to 640x640 float32 blob
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (640, 640), swapRB=True, crop=False)
            self.net.setInput(blob)
            outputs = self.net.forward()

            # Output shape: [1, 5, 8400] -> transpose to [8400, 5]
            if len(outputs.shape) == 3 and outputs.shape[1] < outputs.shape[2]:
                preds = outputs[0].T
            else:
                preds = outputs[0]

            boxes = []
            confidences = []

            for row in preds:
                conf = float(row[4])
                if conf >= self.conf_thresh:
                    cx, cy, bw, bh = row[0], row[1], row[2], row[3]
                    # Scale back to original frame dimensions
                    x1 = int((cx - bw / 2) * (w / 640.0))
                    y1 = int((cy - bh / 2) * (h / 640.0))
                    box_w = int(bw * (w / 640.0))
                    box_h = int(bh * (h / 640.0))
                    center_x = x1 + box_w / 2.0
                    center_y = y1 + box_h / 2.0

                    # 1. HORIZONTAL ROAD BOUNDARY MASK (Eliminates off-road shops, sidewalks, trees)
                    if not self.is_within_road_horizontal_bounds(center_x, center_y, w, h):
                        continue

                    # 2. Strict Physical Ground-Plane Geometry Invariant
                    if (y1 >= int(h * 0.50) and 
                        y1 + box_h <= int(h * 0.98) and 
                        box_w >= int(box_h * 0.70) and 
                        box_w <= int(w * 0.40) and 
                        box_h <= int(h * 0.28)):
                        boxes.append([x1, y1, box_w, box_h])
                        confidences.append(conf)

            indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_thresh, self.iou_thresh)
            results = []
            if len(indices) > 0:
                for idx in indices.flatten():
                    bx, by, bw, bh = boxes[idx]
                    score = confidences[idx]
                    area_px = bw * bh
                    rel_x = (bx + bw / 2.0) / w
                    
                    # Side shoulder waterlogging detection logic (monsoon edge depressions)
                    is_shoulder = (rel_x < 0.28 or rel_x > 0.72)
                    defect_type = "WATERLOGGED_SHOULDER_POTHOLE" if is_shoulder else "POTHOLE"

                    # NISER iWatchRoad Severity Classification
                    if area_px < 6000:
                        sev = "Low Severity"
                        color = "#10B981"
                        depth_cm = round(4.0 + (area_px / 6000.0) * 3.5, 1)
                        cost = "₹9,500"
                    elif area_px <= 8000:
                        sev = "Moderate Severity"
                        color = "#F59E0B"
                        depth_cm = round(7.5 + ((area_px - 6000) / 2000.0) * 6.5, 1)
                        cost = "₹24,000"
                    else:
                        sev = "High Severity"
                        color = "#E11D48"
                        depth_cm = round(14.0 + min(10.0, (area_px - 8000) / 1000.0), 1)
                        cost = "₹48,000"

                    results.append({
                        "class": defect_type,
                        "confidence": f"{score * 100:.1f}%",
                        "bbox": [bx, by, bw, bh],
                        "bbox_norm": [round(bx / max(1, w), 4), round(by / max(1, h), 4), round(bw / max(1, w), 4), round(bh / max(1, h), 4)],
                        "severity": sev,
                        "color": color,
                        "depth_cm": depth_cm,
                        "repair_cost": cost,
                        "location": "Roadside Shoulder (Drainage Dip)" if is_shoulder else "Center Drivable Lane",
                        "contractor": "Rajeshwar Infra Ltd (48h SLA)"
                    })
            return results
        return []

    def process_video(self, video_path: str, output_json: str = None):
        """Process video at 0.5s temporal sampling intervals and compute cluster repair zones."""
        if not os.path.exists(video_path):
            print(f"[!] Video not found: {video_path}")
            return None

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        step_frames = max(1, int(fps * 0.5))  # Sample every 0.5 second (2 Hz)
        print(f"[*] Processing {video_path} ({total_frames} frames @ {fps:.1f} FPS, 0.5s sample step: {step_frames} frames)...")

        detections = []
        frame_idx = 0
        start_t = time.time()

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Sample strictly every 0.5 seconds
            if frame_idx % step_frames == 0:
                frame_results = self.process_frame(frame)
                if len(frame_results) > 0:
                    time_sec = round(frame_idx / fps, 2)
                    
                    # Severe Distress Zone: When multiple potholes are found on the road section
                    has_cluster = len(frame_results) >= 2
                    cluster_meta = None
                    if has_cluster:
                        cluster_meta = {
                            "status": "CRITICAL_CLUSTER",
                            "alert": "EMERGENCY: SEVERE ROAD DISTRESS ZONE - SUDDEN RESURFACING REQUIRED",
                            "pothole_count": len(frame_results),
                            "action": "Immediate 20 MT Hot-Mix Asphalt Overlay (24h SOS SLA)"
                        }

                    detections.append({
                        "frame": frame_idx,
                        "time_sec": time_sec,
                        "objects": frame_results,
                        "cluster_zone": cluster_meta
                    })

            frame_idx += 1

        cap.release()
        elapsed = time.time() - start_t
        print(f"[✓] Processed {frame_idx} frames in {elapsed:.2f}s ({frame_idx/max(0.1, elapsed):.1f} FPS).")
        print(f"[✓] Total 0.5s anomaly intervals detected: {len(detections)}")

        if output_json:
            with open(output_json, "w") as f:
                json.dump({"video": video_path, "fps": fps, "detections": detections}, f, indent=2)
            print(f"[✓] Exported telemetry to {output_json}")

        return detections


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JUCC YOLOv8 Pothole Neural Inference")
    parser.add_argument("--video", type=str, required=True, help="Input dashcam video path")
    parser.add_argument("--out", type=str, default=None, help="Output JSON path")
    args = parser.parse_args()

    engine = DeepPotholeInferenceEngine()
    engine.process_video(args.video, args.out)
