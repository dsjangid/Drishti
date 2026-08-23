"""
JUCC Edge AI Engine - Model Export & Quantization Utility
Module: ai_engine/training/export_to_edge.py
Smart India Hackathon Problem Statement PS-26124

Exports trained PyTorch weights to edge formats:
- ONNX (Open Neural Network Exchange)
- TensorRT Engine (for NVIDIA Jetson Orin Nano / Xavier)
- FP16 Half-Precision Quantization
- NCNN / TFLite (for low-power ARM micro-NPUs)
"""

import os
import sys
import argparse


def export_model_for_edge(
    model_path: str = "runs/train_rad/rad_yolo_model/weights/best.pt",
    format_type: str = "onnx",
    img_size: int = 640,
    half_precision: bool = True
):
    print("=" * 70)
    print("  JUCC EDGE AI - MODEL EXPORT & QUANTIZATION PIPELINE")
    print(f"  Source PyTorch Model: {model_path}")
    print(f"  Target Edge Format:   {format_type.upper()}")
    print(f"  Half Precision (FP16): {half_precision}")
    print("=" * 70)

    try:
        from ultralytics import YOLO
        if not os.path.exists(model_path):
            print(f"[!] Warning: Model file '{model_path}' not found. Using baseline 'yolov8n.pt'.")
            model_path = "yolov8n.pt"

        model = YOLO(model_path)
        print(f"[*] Exporting model with image size {img_size}x{img_size}...")
        
        exported_path = model.export(
            format=format_type,
            imgsz=img_size,
            half=half_precision,
            simplify=True
        )

        print(f"\n[✓] Export completed successfully!")
        print(f"[✓] Deployment artifact: {exported_path}")
        return exported_path

    except ImportError:
        print("[!] Ultralytics not installed. Export command for edge deployment:")
        print(f"    yolo export model={model_path} format={format_type} imgsz={img_size} half={half_precision}")
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export trained model for Jetson edge inference")
    parser.add_argument("--model", type=str, default="runs/train_rad/rad_yolo_model/weights/best.pt", help="Path to best.pt weights")
    parser.add_argument("--format", type=str, default="onnx", choices=["onnx", "engine", "tflite", "ncnn", "coreml"], help="Target format")
    parser.add_argument("--imgsz", type=int, default=640, help="Inference resolution")
    parser.add_argument("--fp16", action="store_true", default=True, help="Enable FP16 quantization")
    args = parser.parse_args()

    export_model_for_edge(args.model, args.format, args.imgsz, args.fp16)
