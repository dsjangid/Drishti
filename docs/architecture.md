# दृष्टि (Drishti) — System Architecture

## Overview

दृष्टि is a public transit bus fleet intelligence platform that turns every municipal bus into a moving road sensor. The system detects potholes, asphalt distress, waterlogging, traffic violations, and driver safety issues in real-time using edge AI inference onboard every bus.

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│                        EDGE HARDWARE (On each bus)                  │
│  ┌──────────────┐  ┌─────────────────┐  ┌────────────────────────┐ │
│  │ Sony STARVIS │  │ NVIDIA Jetson   │  │  STAN 6-Axis IMU       │ │
│  │ 1080p Camera │→ │ Orin Nano NPU   │← │  1000Hz Z-Axis Sample  │ │
│  │ (2× per bus) │  │ 40 TOPS / 15W   │  │  (vibration + GPS)     │ │
│  └──────────────┘  └────────┬────────┘  └────────────────────────┘ │
│                             │ 14.8ms inference / frame              │
│                             ↓                                       │
│                    YOLOv8x-PotholeGuard                             │
│                    (INT8 TensorRT quantized)                        │
│                    + ByteTrack multi-object IDs                     │
└─────────────────────────────┬───────────────────────────────────────┘
                              │ 2.4 KB/min (JSON metadata only)
                              │ Quectel 4G LTE CAT-4
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    CLOUD GATEWAY / MESSAGE BROKER                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Incident Event Stream (JSON per defect detection event)    │   │
│  │  GPS Telemetry Stream (location, speed, heading per bus)    │   │
│  │  Driver DMS Alerts (drowsiness, phone, harsh braking)       │   │
│  └─────────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    MUNICIPAL COMMAND CENTER (Web Dashboard)         │
│                                                                     │
│  GIS Map + Fleet Tracking      Work Order / Docket Engine          │
│  Incident Bento Grid           Contractor SLA Accountability        │
│  Driver Safety Scorecard       24h Traffic Analytics                │
│  Hit & Run ANPR Forensics      GIS Export (GeoJSON / Shapefile)     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## What Is Real vs. Simulated (Honest SIH Disclosure)

| Component | Status | Notes |
|:---|:---|:---|
| YOLOv8x pothole detection model | ✅ **REAL** | Trained on 8,400+ frames, runs via `ui.py` |
| Streamlit AI inference app | ✅ **REAL** | Full end-to-end video inference pipeline |
| ByteTrack multi-object tracker | ✅ **REAL** | Wired into `ui.py` inference loop |
| Pre-rendered demo videos | ✅ **REAL** | Output from actual model runs |
| GIS map with bus routes | 🟡 **SIMULATED** | Deterministic waypoint animation (no live GPS feed) |
| Live telemetry numbers | 🟡 **SIMULATED** | Scripted JS data representing projected system output |
| Driver DMS scores | 🟡 **SIMULATED** | Mock scores for dashboard demonstration |
| Work order auto-dispatch | 🟡 **SIMULATED** | UI mockup; no real PWD API integration |
| ANPR plate OCR | 🟡 **SIMULATED** | Forensics flow is UI-only; no real OCR engine wired |

---

## Repository Structure

```
Drishti/
├── index.html              # Product landing page (50/50 split design)
├── how_it_works.html       # 4-stage pipeline explainer + hardware specs
├── ai_demo.html            # AI perception lab + real model run instructions
├── features.html           # Capability showcase + contractor SLA table
├── dashboard.html          # Full municipal command center (4,626 lines)
│
├── ui.py                   # Streamlit YOLOv8 inference app (REAL AI)
├── requirements.txt        # Python dependencies for ui.py
│
├── models/
│   └── README.md           # Model weights placement instructions
│                           # (*.pt files are gitignored)
│
├── sample_videos/          # Pre-rendered inference output videos
│   └── 02_ai_detected.mp4  # Used in ai_demo.html video player
│
├── scripts/
│   ├── run_ai_lab.sh       # One-command Streamlit launcher
│   └── sync_docs.sh        # Copies root HTML to docs/ for GitHub Pages
│
├── docs/                   # GitHub Pages deployment mirror
│   ├── *.html              # Exact copies of root HTML files
│   ├── architecture.md     # This file
│   ├── ai-pipeline.md      # ML training & inference pipeline docs
│   ├── demo-flow.md        # 3-minute SIH demo guide
│   └── deployment.md       # Production deployment architecture
│
├── data/
│   └── README.md           # Demo data strategy explanation
│
├── .gitignore              # Ignores *.pt, .DS_Store, venv, etc.
├── .env.example            # Environment variables template
└── README.md               # SIH-ready project README
```

---

## Technology Stack

### Frontend
- **HTML5 / CSS3** — Semantic, accessible markup
- **Tailwind CSS** (CDN v3) — Utility-first styling, responsive layouts
- **Google Material Symbols** — Icon system
- **Plus Jakarta Sans + JetBrains Mono** — Typography

### Mapping & GIS
- **Leaflet.js 1.9.4** — Interactive map tiles + custom bus/incident markers
- **OpenStreetMap** (CartoDB Voyager layer) — Map provider
- **GeoJSON export** — Defect layer export for municipal GIS teams

### Data Visualization
- **Chart.js** — Traffic volume time-series, contractor SLA donut charts

### AI / ML
- **Python 3.9+** — Backend inference runtime
- **Streamlit** — Real-time AI lab web interface
- **Ultralytics YOLOv8x** — Object detection architecture
- **OpenCV** — Video frame pipeline, annotated output rendering
- **ByteTrack** — Multi-object persistent ID tracking

### Edge Hardware (Specified for Production)
- **NVIDIA Jetson Orin Nano** — 40 TOPS NPU, TensorRT INT8
- **Sony IMX327 STARVIS** — 1080p @ 60FPS HDR cameras (2× per bus)
- **STAN 6-axis IMU** — 1000Hz Z-axis sampling for vibration classification
- **Quectel 4G LTE CAT-4** — Sub-meter GNSS + cellular uplink

