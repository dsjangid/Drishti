# JUCC Edge-AI Onboard Urban Sensing Platform

**Smart India Hackathon 2026 | Problem Statement: PS-26124**  
*Transforming Public Transit Bus Fleets into Real-Time Mobile Sensing Units for Smart City Infrastructure & Traffic Intelligence.*

---

## 1. System Architecture

The platform consists of two integrated tiers:
1. **Edge-AI Onboard Perception Unit (NVIDIA Jetson Orin Nano / Edge NPU)**: Ingests 4 camera streams on each municipal transit bus, running concurrent real-time deep learning inference for road defects, vehicle density, pedestrian safety, and ANPR plate recognition.
2. **Centralized Urban Intelligence Platform**: Aggregates telemetry from 10+ buses, builds dynamic GIS defect cartography, estimates route delays, and coordinates automated work orders for Municipal Corporations (JDA/PWD) and Traffic Police.

```mermaid
graph TD
    subgraph Bus_Edge_AI_Unit ["Bus Edge-AI Onboard Unit (NVIDIA Jetson / NPU)"]
        Cam1[Front 1080p Cam] --> Ingestion[Multi-Camera Stream Manager]
        Cam2[Downward Asphalt Cam] --> Ingestion
        Cam3[Left Kerb 120° FOV] --> Ingestion
        Cam4[Driver Cabin IR DMS] --> Ingestion
        
        Ingestion --> EdgePipe[Master Edge Pipeline]
        EdgePipe --> DefectModel[Road Defect Detector (Potholes, Cracks, Waterlogging)]
        EdgePipe --> TrafficModel[6-Class Vehicle Classifier & PCU Density]
        EdgePipe --> PedModel[Pedestrian Near-Miss & School Zone Analyzer]
        EdgePipe --> ANPRModel[Hit-and-Run ANPR OCR Recognizer]
        EdgePipe --> DMSModel[Driver Cabin DMS & Fatigue Analyzer]

        DefectModel --> BandwidthOpt[Edge Bandwidth Optimizer]
        TrafficModel --> BandwidthOpt
        PedModel --> BandwidthOpt
        ANPRModel --> BandwidthOpt
        DMSModel --> BandwidthOpt

        BandwidthOpt -->|Compact JSON Telemetry <0.5 KB| LTEModem[4G/5G Cellular Link]
        BandwidthOpt -->|Keyframe Evidence JPEG <40 KB| LTEModem
    end

    subgraph Central_Urban_Platform ["Centralized Urban Intelligence Platform"]
        LTEModem --> IngestAPI[Command Ingest API :8000]
        IngestAPI --> GISDB[(GIS Defect Mesh Database)]
        GISDB --> WebDashboard[BEL Urban Command Center Dashboard]
        GISDB --> PWDOrders[Automated PWD Work Orders]
        GISDB --> PoliceAlerts[Rajasthan Police FIR Pursuit Vectors]
    end
```

---

## 2. Core AI Subsystems

### A. Road Defect Profilometry (`ai_engine/models/defect_detector.py`)
- **Detects:** Potholes, Asphalt Cracks/Raveling, Waterlogging Inundation, Missing Signboards, Faded Zebra Crossings, Broken Dividers.
- **Physical Profilometry Equations:**
  $$\text{Area}_{\text{ground}} = \frac{w_{\text{box}} \times h_{\text{box}}}{w_{\text{img}} \times h_{\text{img}}} \times \text{FOV}_{\text{calib}}$$
  $$\text{Depth}_{\text{est}} = \min\left(22.0, \frac{h_{\text{box}}}{h_{\text{img}}} \times 45.0 + 3.0\right)\text{ cm}$$
  $$\text{Hot-Mix Asphalt (MT)} = \text{Area}_{\text{ground}} \times \frac{\text{Depth}}{100} \times 2.4 \times 6.0$$

### B. Traffic & Vehicle Density Analyzer (`ai_engine/models/vehicle_analyzer.py`)
- **6-Class Detection:** Car, Motorcycle, Auto-Rickshaw, Bus, Truck, Pedestrian.
- **Indian Highway Passenger Car Unit (PCU) Conversion (IRC 106-1990):**
  $$\text{Total PCU} = \sum_{i=1}^{N} \text{PCU\_Factor}(\text{Class}_i)$$
  - *Car: 1.0 | Motorcycle: 0.5 | Auto-Rickshaw: 1.2 | Bus/Truck: 3.0 | Pedestrian: 0.2*
- **Congestion States:** `FREE_FLOW`, `MODERATE`, `CONGESTED`, `GRIDLOCK`.

### C. Vulnerable Pedestrian & School Zone Safety (`ai_engine/models/pedestrian_safety.py`)
- **Time-to-Collision (TTC) Formula:**
  $$\text{TTC} = \frac{d_{\text{pedestrian}}}{\max(1.0, v_{\text{bus}})}$$
- Generates proactive JDA intervention recommendations (Pelican signals, raised speed tables, pedestrian refuge islands).

### D. Hit-and-Run ANPR OCR Engine (`ai_engine/models/anpr_ocr.py`)
- **Indian Plate Format Regex:**
  `^([A-Z]{2})[- ]?([0-9]{1,2})[- ]?([A-Z]{1,3})[- ]?([0-9]{4})$` (e.g. `RJ-14-CE-8821`).
- Resolves optical character ambiguities (`8`/`B`, `0`/`O`, `1`/`I`) and packages automated Police FIR dossiers.

### E. Edge Bandwidth Optimization (`ai_engine/pipeline/bandwidth_optimizer.py`)
- **Bandwidth Reduction Ratio:** Compresses edge transmissions by **> 98.5%**, transmitting lightweight telemetry packets over 4G/LTE instead of raw 18.5 Mbps video streams.

---

## 3. Quick Start & Execution

### Run CLI Evaluation Benchmark on Dashcam Stream
```bash
python3 /Users/meydivyansh/dashboard/ai_engine/evaluate.py --frames 60 --output /Users/meydivyansh/dashboard/ai_output
```

### Start Central Command Server
```bash
python3 /Users/meydivyansh/dashboard/ai_engine/server/command_api.py
```

### Endpoints Available
- `GET /api/fleet` - Live telemetry and GPS for all 10 buses
- `GET /api/defects` - Active municipal defect dockets
- `GET /api/traffic` - Traffic volume curves and PCU breakdown
- `GET /api/geojson` - Standard GeoJSON GIS defect layer export
- `POST /api/telemetry/ingest` - Real-time Edge telemetry ingestion endpoint
