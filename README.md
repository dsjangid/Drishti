# दृष्टि (Drishti) — Urban Road Intelligence Command Center

> **Every municipal bus becomes a living road sensor. Every pothole gets a work order in under 60 seconds.**

[![GitHub Pages](https://img.shields.io/badge/Live%20Demo-GitHub%20Pages-4A62D6?style=for-the-badge&logo=github)](https://dsjangid.github.io/Drishti/)
[![AI Model: YOLOv8x](https://img.shields.io/badge/AI%20Model-YOLOv8x%20PotholeGuard-121316?style=for-the-badge&logo=nvidia)](docs/ai-pipeline.md)
[![Inference: 14.8ms](https://img.shields.io/badge/Edge%20Inference-14.8ms%20%40%2060FPS-4A62D6?style=for-the-badge)](docs/ai-pipeline.md)
[![mAP: 96.8%](https://img.shields.io/badge/Detection%20mAP-96.8%25-121316?style=for-the-badge)](docs/ai-pipeline.md)
[![SIH 2024](https://img.shields.io/badge/Smart%20India%20Hackathon-2026-4A62D6?style=for-the-badge)](docs/demo-flow.md)

---

## The Problem

India loses **₹6 lakh crore every year** to bad roads (3–5% of GDP). In 2026:
- **177,175 people died** in road accidents (MoRTH 2026)
- **2,385 deaths** were directly caused by potholes — a 53% increase since 2020
- Cities detect and patch the same potholes repeatedly because they lack continuous, city-wide monitoring

Current solutions — dedicated road survey vans — cost ₹1.2 lakh per kilometer and survey a city once every 3–6 months.

**दृष्टि costs ₹0 per kilometer** — because the bus fleet is already running.

---

## The Solution

दृष्टि mounts low-cost AI hardware onto existing municipal bus fleets. Every bus becomes a continuously scanning road sensor, detecting potholes, surface distress, waterlogging, and safety violations in real-time — and dispatching automated municipal work orders before the next bus passes.

**Key differentiators:**
- **100× cheaper** than dedicated survey vans
- **20× more scans per day** per corridor vs. manual inspection
- **Sub-60 second** docket dispatch from detection to work order
- **14.8ms edge inference** — fully offline on a ₹15,000 Jetson Orin Nano chip
- **Real trained AI model** — not a prototype, not fine-tuned — trained from scratch on 8,400+ frames

---

## What's Real vs. Simulated

| Component | Status |
|:---|:---|
| YOLOv8x pothole detection model | ✅ **Real** — runs via `ui.py` |
| Streamlit AI inference app | ✅ **Real** — full video pipeline |
| ByteTrack multi-object tracker | ✅ **Real** |
| Pre-rendered demo videos | ✅ **Real model outputs** |
| GIS map & fleet tracking | 🟡 Simulated (deterministic waypoints) |
| Live telemetry numbers | 🟡 Simulated (representative projections) |
| Work order dispatch | 🟡 UI mockup |

See [`docs/architecture.md`](docs/architecture.md) for full disclosure.

---

## Quick Start

### 1. View the Website (No Setup Required)

**[→ Live Demo on GitHub Pages](https://dsjangid.github.io/Drishti/)**

Or run locally:
```bash
git clone https://github.com/dsjangid/Drishti.git
cd Drishti
python3 -m http.server 8000
# Open: http://localhost:8000
```

### 2. Run the Real AI Pothole Detection Model

```bash
# Install Python dependencies
pip install -r requirements.txt

# Place model weights in the project root (gitignored — not in repo)
# File: "best (16).pt"  OR  models/drishti_potholedetect_v1.pt

# Launch the AI Lab
bash scripts/run_ai_lab.sh
# Opens at: http://localhost:8501
```

Upload any road or dashcam video. The YOLOv8x model will detect and track potholes frame by frame.

---

## Platform Structure

| Page | File | Description |
|:---|:---|:---|
| **Home** | [`index.html`](index.html) | Product landing page with ROI calculator and AI demo player |
| **How It Works** | [`how_it_works.html`](how_it_works.html) | 4-stage edge-to-cloud pipeline with hardware specs |
| **AI Demo Lab** | [`ai_demo.html`](ai_demo.html) | Inference video player + real model run instructions |
| **Features** | [`features.html`](features.html) | Full capability showcase + contractor SLA tracker |
| **Command Center** | [`dashboard.html`](dashboard.html) | Live GIS map, fleet telemetry, work orders, analytics |
| **AI Inference App** | [`ui.py`](ui.py) | Streamlit app — real YOLOv8x pothole detection |

---

## Hardware Specifications (Edge Unit Per Bus)

| Component | Specification |
|:---|:---|
| Edge NPU | NVIDIA Jetson Orin Nano · 40 TOPS · 15W |
| Optical Sensors | 2× Sony IMX327 STARVIS · 1080p @ 60FPS HDR |
| IMU | STAN 6-axis · 1000Hz Z-axis sampling |
| Connectivity | Quectel 4G LTE CAT-4 + Multi-constellation GNSS |
| Bandwidth | 2.4 KB/min (metadata-only, 99.5% reduction vs. raw video) |
| Unit Cost | ~₹15,000 per bus |

---

## AI Model Specifications

| Property | Value |
|:---|:---|
| Architecture | YOLOv8x + ByteTrack |
| Inference latency | **14.8ms** (Jetson Orin Nano, INT8 TensorRT) |
| Detection accuracy | **96.8% mAP@0.5** |
| Training frames | 8,400+ annotated road images |
| Classes detected | Potholes, raveling, waterlogging, edge failure |

See [`docs/ai-pipeline.md`](docs/ai-pipeline.md) for full training configuration and evaluation results.

---

## Technology Stack

- **Frontend**: Vanilla HTML5, Tailwind CSS (CDN), Material Symbols, Plus Jakarta Sans
- **Maps & GIS**: Leaflet.js + OpenStreetMap (CartoDB Voyager), GeoJSON export
- **Charts**: Chart.js (traffic volume, contractor SLA)
- **AI/ML**: Python, Ultralytics YOLOv8x, OpenCV, Streamlit, ByteTrack
- **Deployment**: GitHub Pages (static) + local Streamlit (AI lab)

---

## Documentation

| Document | Description |
|:---|:---|
| [`docs/architecture.md`](docs/architecture.md) | System architecture, layer diagram, real vs. simulated |
| [`docs/ai-pipeline.md`](docs/ai-pipeline.md) | Training data, model config, evaluation metrics |
| [`docs/demo-flow.md`](docs/demo-flow.md) | 3-minute SIH demo script with talking points |
| [`docs/deployment.md`](docs/deployment.md) | Local setup, GitHub Pages, production architecture |
| [`data/README.md`](data/README.md) | Demo data strategy and source citations |

---

## Scripts

```bash
bash scripts/run_ai_lab.sh    # Launch Streamlit AI inference app
bash scripts/sync_docs.sh     # Sync root HTML files to docs/ (GitHub Pages)
```

---

## Developed For

**Smart India Hackathon (SIH) 2024**  
Problem Domain: Smart Roads & Public Transport · Sustainable Cities  
Sponsor: Bharat Electronics Limited (BEL)

*© 2026 दृष्टि Urban Road Intelligence. Built for every Indian city.*
