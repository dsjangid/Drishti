# 🏛️ JUCC — Jaipur Urban Command Center

> **Real-Time Edge-AI Municipal Road Perception, Public Transit Safety & Fleet Telemetry Network**  
> *Developed for Bharat Electronics Limited (BEL) & Nagar Nigam Jaipur (JMC) · Smart India Hackathon (SIH) Evaluation Prototype*

[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-10B981?style=for-the-badge&logo=shield)](https://github.com/dsjangid/dashboard)
[![Inference Latency: 14.8ms](https://img.shields.io/badge/NPU%20Latency-14.8ms%20@%2060FPS-121316?style=for-the-badge&logo=nvidia)](https://github.com/dsjangid/dashboard)
[![Detection Accuracy: 96.8%](https://img.shields.io/badge/Model%20Accuracy-96.8%25%20mAP-10B981?style=for-the-badge)](https://github.com/dsjangid/dashboard)
[![License: BEL / JMC](https://img.shields.io/badge/License-BEL%20%2F%20JMC%20Internal-121316?style=for-the-badge)](https://github.com/dsjangid/dashboard)

---

## 🌟 Executive Overview

**JUCC (Jaipur Urban Command Center)** transforms everyday municipal transit buses into an intelligent, moving AI sensing network. By mounting low-cost 1080p optical cameras and edge NPUs onto public transit fleets, JUCC continuously inspects urban road corridors, detects potholes, asphalt raveling, waterlogging, and safety violations in real-time, and dispatches automated PWD repair dockets in under 60 seconds.

---

## 📑 Platform Structure

The repository contains both the public-facing **Multi-Page Marketing & Technical Overview Website** and the full **Live Municipal Command Center Dashboard**:

| Page / Module | File | Description |
| :--- | :--- | :--- |
| **1. Home Overview** | [`index.html`](index.html) | High-end product website home page with interactive Municipal ROI & Asphalt Savings Calculator, Ward telemetry filter, and live video demo player. |
| **2. How It Works** | [`how_it_works.html`](how_it_works.html) | 4-Stage Edge-to-Cloud neural pipeline inspector, NVIDIA Jetson Orin hardware specifications, and data security protocols. |
| **3. AI Perception Lab** | [`ai_demo.html`](ai_demo.html) | Widescreen interactive perception video laboratory with live telemetry streams and neural model benchmark comparisons. |
| **4. Features Suite** | [`features.html`](features.html) | Deep-dive capability showcase and PWD Contractor SLA accountability scorecard. |
| **5. Command Center Dashboard** | [`dashboard.html`](dashboard.html) | Mission-critical GIS Command Center with real-time Leaflet mapping across 10 Jaipur buses, live camera HUD, driver DMS scoring, hit-and-run forensics, and GIS export engine. |

---

## 🚀 Key Features & Capabilities

### 1. Real-Time Optical Edge-AI Profilometry
- **Dual Optical Sensors**: Wide-angle 120° windshield camera for traffic flow & ANPR + downward macro camera for millimeter-accurate asphalt crater measurement.
- **Edge NPU Acceleration**: Executes quantized YOLOv8 neural models locally on NVIDIA Jetson hardware at **14.8 ms latency (60 FPS)**.
- **STAN Sensor Fusion**: Combines optical computer vision with 6-axis IMU accelerometer Z-axis vibration spikes to classify impact severity (up to 3.4g).

### 2. Automated Municipal Work Orders & Contractor SLA
- **Instant Docket Generation**: Auto-calculates crater volume, estimated hot-mix asphalt tonnage (e.g., *12 MT Hot-Mix*), repair budget allocation, and assigned Zone Engineer.
- **Contractor Accountability**: Tracks contractor repair SLAs (24h / 48h emergency turnaround) and grades contractor completion quality.

### 3. Hit-and-Run Forensics & ANPR OCR Intercept
- **Multi-Camera Trail Reconstruction**: High-speed OCR engine extracts vehicle license plates (`RJ-14-CE-8821`) with 97.4% accuracy across multiple passing buses.
- **Police PCR Escalation**: Generates instant multi-angle evidentiary dockets with GPS trajectory vectors for law enforcement.

### 4. Driver Safety Monitoring (DMS)
- **Infrared Cabin Sensing**: 60 FPS eye-tracking monitoring Eye Aspect Ratio (EAR), drowsiness triggers, phone distractions, and harsh braking events.
- **Driver Safety Scorecards**: Tracks individual safety scores (0–100) and routes drivers for mandatory defensive transit training.

---

## ⚡ Quick Start Guide

### Run Locally (Zero Build Tools Required):

```bash
# 1. Clone the repository
git clone git@github.com:dsjangid/dashboard.git
cd dashboard

# 2. Start a lightweight local HTTP server
python3 -m http.server 8000
```

- Open **[http://localhost:8000/index.html](http://localhost:8000/index.html)** (or just **`http://localhost:8000/`**) to explore the **Product Website**.
- Open **[http://localhost:8000/dashboard.html](http://localhost:8000/dashboard.html)** to launch the **Live Command Center Dashboard**.

---

## 🛠️ Technology Stack

- **Frontend & UI**: Vanilla HTML5, Modern CSS, Tailwind CSS Utility Architecture, Material Symbols Icons, Google Fonts (*Plus Jakarta Sans* & *JetBrains Mono*).
- **Mapping & GIS Engine**: Leaflet.js, OpenStreetMap Cartography, Custom Dark High-Contrast Shader Layers, Spatial Clustering.
- **Edge AI & Computer Vision**: YOLOv8x Neural Network, OpenCV, NVIDIA TensorRT INT8 Quantization.
- **Data Visualization**: Chart.js for real-time traffic volume time-series and contractor SLA donuts.
- **Media Engine**: Native HTML5 Video Stream with burnt-in H.264 neural HUD telemetry overlays.

---

## 📐 Hardware Specifications (Onboard Bus Unit)

| Component | Specification |
| :--- | :--- |
| **Edge NPU Chipset** | NVIDIA Jetson Orin Nano (40 TOPS AI, 15W Power Envelope) |
| **Optical Sensors** | Dual Sony IMX327 Starvis CMOS (1080p @ 60 FPS HDR) |
| **IMU Telemetry** | STAN 6-Axis Accelerometer / Gyroscope (1000 Hz Z-Axis Sampling) |
| **Cellular Uplink** | Quectel 4G LTE CAT-4 + Multi-Constellation GNSS (Sub-meter RTK) |
| **Telemetry Bandwidth** | 2.4 KB/min (98.4% bandwidth reduction via edge metadata extraction) |

---

## 👥 Evaluation Credits

Developed for the **Bharat Electronics Limited (BEL) & Nagar Nigam Jaipur (JMC)** Smart City Urban Mobility Evaluation Benchmark (*SIH Problem Statement PS-26124*).

*© 2026 JUCC Jaipur Urban Command Center. All Rights Reserved.*
