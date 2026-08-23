# Training Road Anomaly Detection (RAD) Models for Edge Transit Units

**Dataset:** [Kaggle: `rohitsuresh15/radroad-anomaly-detection`](https://www.kaggle.com/datasets/rohitsuresh15/radroad-anomaly-detection)  
**SIH-2026 Problem Statement:** PS-26124 (Mobile Urban Sensing Units)

---

## 1. Dataset Overview

The **RAD (Road Anomaly Detection)** dataset contains **11,800 images and videos across 371 road scenarios** with labeled bounding boxes for:
- `pothole` (Class 0)
- `crack` (Class 1)
- `manhole` (Class 2)
- `speed_bump` (Class 3)
- `protrusion` (Class 4)
- `lmv` (Light Motor Vehicles: cars, bikes, autos) (Class 5)
- `hmv` (Heavy Motor Vehicles: buses, trucks) (Class 6)
- `pedestrian` (Class 7)
- `unsurfaced_road` (Class 8)

---

## 2. Quick Setup & Download

### Option A: Automatic Download via Kaggle CLI
```bash
# 1. Install Kaggle CLI
pip install kaggle

# 2. Download and extract directly into ai_engine/training/datasets
python3 ai_engine/training/download_rad_dataset.py
```

### Option B: Direct Kaggle CLI Command
```bash
kaggle datasets download -d rohitsuresh15/radroad-anomaly-detection --unzip -p ai_engine/training/datasets/rad_dataset
```

---

## 3. Training the Model (YOLOv8 / YOLO11)

### Local / GPU Server Training
```bash
python3 ai_engine/training/train_rad_yolo.py \
  --config ai_engine/training/dataset_config.yaml \
  --model yolov8n.pt \
  --epochs 50 \
  --batch 16 \
  --imgsz 640
```

### Training on Google Colab or Kaggle Notebooks (Free GPU)
```python
# In Colab/Kaggle cell:
!pip install ultralytics kaggle

# Download dataset
!kaggle datasets download -d rohitsuresh15/radroad-anomaly-detection --unzip -p ./rad_dataset

# Train model
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
model.train(data='ai_engine/training/dataset_config.yaml', epochs=50, imgsz=640, batch=16, device=0)
```

---

## 4. Exporting Trained Weights to Jetson / Edge NPU

Export the best checkpoint (`best.pt`) to high-speed **ONNX** and **TensorRT Engine** (FP16 half-precision):

```bash
# Export to ONNX (dynamic batching, optimized for Jetson)
python3 ai_engine/training/export_to_edge.py --model runs/train_rad/rad_yolo_model/weights/best.pt --format onnx --fp16

# Export to TensorRT Engine (.engine) on NVIDIA Jetson
python3 ai_engine/training/export_to_edge.py --model runs/train_rad/rad_yolo_model/weights/best.pt --format engine --fp16
```

---

## 5. Integrating with the Master Edge Pipeline

Once exported, place your `best.pt` or `best.onnx` model in `ai_engine/models/` and run real-time inference:

```bash
python3 ai_engine/evaluate.py --video bus_dashcam_1080p.mp4 --frames 100
```
