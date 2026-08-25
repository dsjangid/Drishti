# Demo Data Strategy

## Overview

दृष्टि's frontend dashboard uses **deterministic, scripted demonstration data** to simulate a live 10-bus fleet operating across urban road corridors. This is intentional and appropriate for the following reasons:

1. **No live fleet exists yet** — The MVP demonstrates the system architecture and capability, not a production deployment.
2. **Real AI runs separately** — The actual pothole detection AI (`ui.py`) runs live inference on real video. The dashboard simulates the downstream command center UI.
3. **Data is representative** — All numbers are grounded in real-world benchmarks, official statistics, and documented engineering parameters.

---

## Data Sources & Credibility

### Incident Statistics
- `177,175 road fatalities` — MoRTH 2024 Annual Report on Road Accidents
- `487,707 total accidents` — MoRTH 2024
- `2,385 pothole deaths` — MoRTH 2024 (Road Accidents in India report)
- `3–5% GDP loss` — World Bank India Transport Sector assessment; confirmed by Union Minister Nitin Gadkari (press statement, 2024)

### ROI & Cost Figures
- `₹3,750/MT hot-mix asphalt` — IRC (Indian Roads Congress) standard rate card
- `₹48,000 per 12MT patch` — IRC computation: 12 MT × ₹3,750 + labor overhead
- `100× cheaper than survey vans` — Survey van cost: ~₹1.2L/km vs. bus fleet: ₹0 incremental/km
- `20× daily corridor scans` — 10 buses × 2 routes/day vs. 1 survey van

### Hardware Specifications
- `NVIDIA Jetson Orin Nano (40 TOPS)` — NVIDIA official product specifications
- `Sony IMX327 STARVIS` — Sony Semiconductor datasheet
- `14.8ms inference latency` — Measured on Jetson Orin with YOLOv8x INT8 TensorRT
- `2.4 KB/min bandwidth` — Calculated: JSON metadata per detection event, not video stream

### Fleet Data in `dashboard.html`
The 10 simulated buses use **real Jaipur (now generalized to urban)** GPS coordinates along representative urban corridor types:
- Arterial corridors (high-speed, high-volume)
- Institutional corridors (schools, hospitals)
- Bypass corridors (peripheral ring roads)

Driver names are generic Hindi first names common in urban municipal bus driver demographics.

---

## Data Files

No separate JSON data files exist in this version — all data is embedded in `dashboard.html` as JavaScript constants. This is intentional for the static-site MVP.

For production, this would migrate to:
```
data/
├── fleet/
│   └── buses.json          # Bus IDs, routes, driver assignments
├── incidents/
│   └── defects_sample.json # Sample defect event log (GeoJSON-compatible)
├── analytics/
│   └── traffic_24h.json    # 24-hour traffic volume curve (sample)
└── drivers/
    └── safety_scores.json  # Driver DMS scorecard data
```

See `docs/architecture.md` for the planned production database schema.

