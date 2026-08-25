# दृष्टि — Deployment Guide

## Current Deployment: Static GitHub Pages

The marketing website and command center dashboard are deployed as static HTML on GitHub Pages.

**Live URL:** `https://dsjangid.github.io/Drishti/`  
**Source branch:** `main` → `/` (root, not `/docs`)  
**GitHub Actions:** `.github/workflows/pages.yml` auto-deploys on every push to `main`

---

## Local Development

No build tools required. This is pure HTML.

```bash
# 1. Clone the repository
git clone https://github.com/dsjangid/Drishti.git
cd Drishti

# 2. Run a local HTTP server
python3 -m http.server 8000

# 3. Open in browser
# Website: http://localhost:8000/index.html
# Dashboard: http://localhost:8000/dashboard.html
```

### After Editing HTML Files

Always sync root files to `docs/` for GitHub Pages:
```bash
bash scripts/sync_docs.sh
```

---

## AI Lab Local Setup

The Streamlit AI inference app runs separately from the website.

```bash
# Install dependencies
pip install -r requirements.txt

# Place model weights (gitignored — not in the repo)
# Option A: Place in root as "best (16).pt"
# Option B: Place in models/ as "drishti_potholedetect_v1.pt"

# Launch
bash scripts/run_ai_lab.sh
# Opens at http://localhost:8501
```

**Requirements:**
- Python 3.9+
- pip packages: `streamlit`, `ultralytics`, `opencv-python-headless`
- Model weights: `best (16).pt` (5.1 MB, not in git)

---

## Production Architecture (Post-MVP)

The following describes the planned production system architecture for full municipal deployment.

```
┌─────────────────┐     MQTT/gRPC      ┌─────────────────────────┐
│  Bus Edge Unit  │ ─────────────────→ │  Cloud Ingestion API    │
│  Jetson Orin    │   2.4 KB/min JSON  │  (FastAPI / gRPC)       │
└─────────────────┘                    └────────────┬────────────┘
                                                    │
                                       ┌────────────▼────────────┐
                                       │  TimescaleDB            │
                                       │  (GPS + defect events)  │
                                       └────────────┬────────────┘
                                                    │
                                       ┌────────────▼────────────┐
                                       │  Work Order Engine       │
                                       │  (auto-docket + SLA)    │
                                       └────────────┬────────────┘
                                                    │
                              ┌─────────────────────▼──────────────────────┐
                              │            Next.js / React Dashboard        │
                              │  (replaces current static HTML dashboard)   │
                              └────────────────────────────────────────────┘
```

### Recommended Production Stack

| Layer | Technology | Rationale |
|:---|:---|:---|
| **Edge runtime** | NVIDIA TensorRT INT8 | 4× faster than PyTorch on Jetson |
| **Edge OS** | JetPack 5.1 + Ubuntu 20.04 | NVIDIA certified |
| **Event streaming** | Apache Kafka / MQTT | High-throughput bus telemetry |
| **Time-series DB** | TimescaleDB (PostgreSQL) | GPS + sensor data |
| **GIS storage** | PostGIS extension | Spatial queries on defect clusters |
| **API layer** | FastAPI (Python) | Type-safe, auto OpenAPI docs |
| **Dashboard** | React + Mapbox GL | Production-grade map rendering |
| **Auth** | Supabase Auth | Municipal user role management |
| **Alerts** | MSG91 / Twilio SMS | Docket notifications to engineers |
| **CI/CD** | GitHub Actions | Auto test + deploy pipeline |

---

## Scaling Estimates

| Fleet Size | Buses | Data/day | Storage/year | Infrastructure Cost |
|:---|:---|:---|:---|:---|
| Pilot | 10 | ~35 MB | ~12 GB | Shared cloud (free tier) |
| City tier-2 | 200 | ~700 MB | ~250 GB | ₹8,000/month (cloud) |
| City tier-1 | 1,000 | ~3.5 GB | ~1.25 TB | ₹35,000/month (cloud) |
| National | 50,000+ | ~175 GB | ~65 TB | On-prem / dedicated |

*All estimates based on 2.4 KB/min metadata-only uplink (no video stream).*

---

## Security Considerations

- All `.pt` model weights are gitignored — never committed to public repo
- No API keys or secrets in any HTML, JS, or Python files (verified by security scan)
- `.env.example` documents future API key requirements
- Future: JWT authentication for dashboard access
- Future: End-to-end encryption on edge uplink (TLS 1.3)

