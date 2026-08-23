# JUCC — Jaipur Urban Command Center

> **Real-Time Public Transit Safety, AI Road Defect Mesh & Fleet Command Dashboard**  
> *Developed for Bharat Electronics Limited (BEL) & Nagar Nigam Jaipur (JMC) · Smart India Hackathon (SIH) Problem Statement PS-26124*

---

## Overview

**JUCC (Jaipur Urban Command Center)** is a high-performance GIS Command Center designed for municipal transport authorities, traffic police, PWD/JDA engineers, and city planners.

It ingests live edge-AI telemetry from municipal buses equipped with NVIDIA Jetson edge NPUs and multi-camera setups, transforming raw transit feeds into real-time defect maps, driver behavior indices, and actionable municipal work orders.

---

## Key Features

### 1. Real-Time GIS Fleet & Defect Mesh
- **Interactive Dark-Mode Map**: Rendered with Leaflet.js and custom high-contrast cartography.
- **10 Municipal Buses**: Real-time GPS coordinates, speed, heading, driver identity, and connectivity status across Jaipur arterial routes (Tonk Road, JLN Marg, Ajmer Road, Sikar Road, etc.).
- **Incident Markers**: Real-time visualization of Potholes, Waterlogging, Hit-and-Run events, Missing Signage, Rash Driving, and Pedestrian risks.

### 2. Multi-View Architecture (6 Modes)
1. **Map & Heatmap View**: Spatial distribution with interactive defect clusters and live incident feed.
2. **Timeline Stream**: Chronological sensor-to-server time progression of municipal detections.
3. **Incident Dockets Grid**: Detailed visual docket cards with confidence scores and camera angles.
4. **Traffic & Charts View**: Real-time traffic flow time-series (24h) and 6-class AI vehicle classification charts (Chart.js).
5. **Before / After ROI**: Algorithmic repair verification and municipal return-on-investment payback analysis.
6. **Report & GIS Export**: Export engine supporting PDF, CSV, GeoJSON layers, and ESRI Shapefile metadata.

### 3. Interactive Filtering & 24h Playback
- **Time Scrubber**: 24-hour simulation slider with 1x, 2x, and 4x playback speeds.
- **Filter Presets**: Instant one-click presets for *Rush Hour View*, *High-Risk Hotspots*, and *Monsoon Hazards*.
- **Multi-Dimensional Filters**: Filter by Incident Type, Min Severity slider (0–100%), Timeframe, AI Confidence (>80%, >90%, >95%), Bus Unit, and Status.

### 4. Specialized Forensics & Safety Modules
- **Hit-and-Run Multi-Camera Trail**: Automatic ANPR/OCR plate extraction (`RJ-14-CE-8821`), cross-bus camera handoff, speed calculations, and instant police escalation.
- **Driver Safety Index**: Driver safety scores (0–100), rash acceleration/braking tallies, and training recommendations.
- **Pedestrian & School Zone Safety**: Near-miss analytics at high-risk pedestrian crossings (Choti Chaupar, RU Gate, Sindhi Camp) with recommended JDA interventions.

---

## Quick Start

### Run Locally (No dependencies required):
```bash
# Clone the repository
git clone git@github.com:dsjangid/dashboard.git
cd dashboard

# Start a local HTTP server
python3 -m http.server 8080
```
Open **[http://localhost:8080](http://localhost:8080)** (or `index.html`) in any modern web browser.

---

## Technology Stack
- **Interface**: Vanilla HTML5, Tailwind CSS, Material Symbols, Source Serif 4 & JetBrains Mono typography.
- **Mapping**: Leaflet GIS, OpenStreetMap tiles with custom dark inverted shader matrix.
- **Data Visualization**: Chart.js for time-series and doughnut charts.
- **Audio Feedback**: Web Audio API synthesized frequency beeps and alerts.

---

## License
Internal Defense & Municipal Evaluation Prototype · BEL SIH-2026.
