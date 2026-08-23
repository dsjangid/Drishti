"""
JUCC Edge AI Engine - Evaluation & Demo CLI Runner
Module: ai_engine/evaluate.py
Smart India Hackathon Problem Statement PS-26124

Executes real-time multi-angle edge perception on transit video streams:
- Road Defect Detection (Potholes, Cracks, Waterlogging)
- 6-Class Traffic Vehicle Classification & Speed Tracking
- Hit-and-Run ANPR OCR Target Interception (RJ-14-CE-8821)
- Pedestrian & School Zone Proximity Hazard Analysis
- Edge Bandwidth Optimization Report
"""

import os
import sys
import time
import argparse
import cv2
import json

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai_engine.pipeline.edge_pipeline import BusEdgeAIUnit
from ai_engine.pipeline.camera_stream import CameraAngle


def run_evaluation(video_path: str, max_frames: int = 60, output_dir: str = "ai_output"):
    print("=" * 70)
    print("  JUCC EDGE AI ONBOARD SENSING ENGINE - EVALUATION BENCHMARK")
    print("  Developed for Bharat Electronics Limited (BEL) & Nagar Nigam Jaipur")
    print("  Problem Statement: PS-26124")
    print("=" * 70)

    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(video_path):
        print(f"[!] Warning: Video '{video_path}' not found. Using synthetic calibrated camera stream.")
        video_path = None

    print(f"[*] Initializing Edge AI Unit for BUS-003 (Tonk Road Corridor)...")
    edge_unit = BusEdgeAIUnit(
        bus_id="BUS-003",
        driver_name="Manoj Meena",
        route_name="Route 3: Tonk Road",
        video_source_path=video_path,
        initial_gps=(26.8520, 75.7920)
    )

    angles = [CameraAngle.FRONT, CameraAngle.ASPHALT, CameraAngle.BLINDSPOT, CameraAngle.CABIN]
    total_defects = 0
    total_vehicles = 0
    anpr_detections = []
    fps_measurements = []

    print(f"[*] Commencing multi-angle edge inference on {max_frames} frames...\n")

    start_time = time.time()
    for frame_idx in range(max_frames):
        angle = angles[frame_idx % len(angles)]
        t0 = time.time()

        result = edge_unit.process_telemetry_frame(active_angle=angle)
        
        t1 = time.time()
        fps = 1.0 / max(0.001, t1 - t0)
        fps_measurements.append(fps)

        telemetry = result["telemetry"]
        stats = result["bandwidth_stats"]
        defects = telemetry["road_defects"]
        traffic = telemetry["traffic_state"]
        target_plates = telemetry["anpr_fir_dossiers"]

        total_defects += len(defects)
        total_vehicles += traffic.get("active_vehicles_in_frame", 0)
        if target_plates:
            anpr_detections.extend(target_plates)

        # Print live progress every 10 frames
        if (frame_idx + 1) % 10 == 0 or frame_idx == 0:
            print(
                f"  Frame {frame_idx + 1:03d}/{max_frames} [{angle.upper():9s}] | "
                f"FPS: {fps:4.1f} | Defects: {len(defects)} | "
                f"Vehicles: {traffic['active_vehicles_in_frame']} ({traffic['congestion_state']}) | "
                f"Bandwidth Saved: {stats['bandwidth_saved_percentage']}%"
            )

        # Save sample annotated keyframe
        if frame_idx == 0 or len(defects) > 0 or len(target_plates) > 0:
            out_frame_path = os.path.join(output_dir, f"frame_{frame_idx+1:03d}_{angle}.jpg")
            cv2.imwrite(out_frame_path, result["annotated_frame"])

    total_time = time.time() - start_time
    avg_fps = len(fps_measurements) / max(0.001, total_time)

    edge_unit.close()

    print("\n" + "=" * 70)
    print("  EVALUATION SUMMARY & PERFORMANCE METRICS")
    print("=" * 70)
    print(f"  • Total Frames Processed:          {max_frames}")
    print(f"  • Average Inference Throughput:    {avg_fps:.1f} FPS (Target: 18.0+ FPS on Jetson Orin)")
    print(f"  • Total Road Defects Localized:    {total_defects} (Potholes, Cracks, Waterlogging)")
    print(f"  • Total Vehicles Classified:       {total_vehicles} (PCU Flow Scanned)")
    print(f"  • ANPR FIR Target Locks:           {len(anpr_detections)} (Plate: RJ-14-CE-8821)")
    print(f"  • Edge Bandwidth Optimization:     {stats['bandwidth_saved_percentage']}% Saved (Ratio: {stats['edge_compression_ratio']})")
    print(f"  • Output Evidence Saved To:        {output_dir}/")
    print("=" * 70)

    # Save summary report JSON
    report = {
        "benchmark_timestamp": time.strftime("%Y-%m-%d %H:%M:%S IST"),
        "bus_id": "BUS-003",
        "route": "Route 3: Tonk Road",
        "total_frames": max_frames,
        "average_fps": round(avg_fps, 2),
        "total_defects_detected": total_defects,
        "total_vehicles_counted": total_vehicles,
        "anpr_hits": anpr_detections,
        "bandwidth_optimization": stats
    }
    with open(os.path.join(output_dir, "evaluation_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"[✓] Benchmark evaluation completed successfully.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JUCC Edge AI Engine Evaluation Benchmark")
    parser.add_argument("--video", type=str, default="/Users/meydivyansh/dashboard/bus_dashcam_1080p.mp4", help="Path to input test video")
    parser.add_argument("--frames", type=int, default=40, help="Number of frames to process")
    parser.add_argument("--output", type=str, default="/Users/meydivyansh/dashboard/ai_output", help="Output directory for annotated frames")
    args = parser.parse_args()

    run_evaluation(args.video, args.frames, args.output)
