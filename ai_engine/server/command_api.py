"""
JUCC Centralized Urban Intelligence Backend
Module: ai_engine/server/command_api.py
Smart India Hackathon Problem Statement PS-26124

Aggregates edge telemetry from 10+ municipal buses across Jaipur,
maintains real-time GIS defect cartography, and serves REST/JSON endpoints
for municipal command centers, PWD engineers, and traffic police.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from typing import Dict, Any, List


class CentralCommandDatabase:
    """
    In-memory high-throughput GIS telemetry and municipal defect repository.
    """

    def __init__(self):
        self.buses = {
            f"BUS-{str(i).zfill(3)}": {
                "id": f"BUS-{str(i).zfill(3)}",
                "route": f"Route {i}: Jaipur Corridor",
                "lat": 26.8520 + (i * 0.012),
                "lng": 75.7920 + (i * 0.008),
                "speed": 25 + (i * 2),
                "driver": f"Driver {i}",
                "status": "ONLINE",
                "score": 90 - (i % 3) * 5,
                "temp": 46 + (i % 5),
                "fps": 18.5,
                "lat_ms": 42,
                "last_updated": datetime.now().isoformat()
            } for i in range(1, 11)
        }

        self.defects: List[Dict[str, Any]] = [
            {
                "id": "DEF-001",
                "type": "POTHOLE",
                "location": "Tonk Road KM 4.2",
                "lat": 26.8540,
                "lng": 75.7940,
                "detected_by": "BUS-003",
                "depth_cm": 16.4,
                "hot_mix_mt": 12.0,
                "cost_inr": "₹45,000",
                "status": "Pending",
                "severity": "High",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": "DEF-002",
                "type": "WATERLOGGING",
                "location": "Ajmer Road 200ft Bypass",
                "lat": 26.8820,
                "lng": 75.7480,
                "detected_by": "BUS-002",
                "depth_cm": 25.0,
                "hot_mix_mt": 0.0,
                "cost_inr": "₹80,000",
                "status": "In Progress",
                "severity": "Medium",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "id": "DEF-003",
                "type": "HIT_AND_RUN",
                "location": "Airport T2 Junction",
                "lat": 26.8290,
                "lng": 75.8070,
                "detected_by": "BUS-005",
                "plate_number": "RJ-14-CE-8821",
                "status": "Critical",
                "severity": "High",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]

    def ingest_telemetry(self, telemetry_packet: Dict[str, Any]):
        """Ingests live telemetry packet from a bus edge unit."""
        bus_id = telemetry_packet.get("bus_id")
        if bus_id and bus_id in self.buses:
            coords = telemetry_packet.get("gps_coordinates", {})
            self.buses[bus_id].update({
                "lat": coords.get("latitude", self.buses[bus_id]["lat"]),
                "lng": coords.get("longitude", self.buses[bus_id]["lng"]),
                "speed": telemetry_packet.get("speed_kmh", self.buses[bus_id]["speed"]),
                "last_updated": datetime.now().isoformat()
            })

        # Ingest road defects if detected
        for d in telemetry_packet.get("road_defects", []):
            m = d.get("metrics", {})
            self.defects.append({
                "id": f"DEF-{len(self.defects)+1:03d}",
                "type": d.get("defect_type"),
                "location": telemetry_packet.get("route", "Jaipur Urban Route"),
                "lat": coords.get("latitude", 26.85),
                "lng": coords.get("longitude", 75.80),
                "detected_by": bus_id,
                "depth_cm": m.get("depth_cm", 0.0),
                "hot_mix_mt": m.get("hot_mix_mt", 0.0),
                "cost_inr": m.get("est_cost_inr", "₹25,000"),
                "status": "Pending",
                "severity": "High" if m.get("severity_score", 5) > 6 else "Medium",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    def export_geojson(self) -> Dict[str, Any]:
        """Exports defect mesh as standard GeoJSON FeatureCollection."""
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "id": d["id"],
                        "type": d["type"],
                        "location": d["location"],
                        "status": d["status"],
                        "detected_by": d["detected_by"]
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [d["lng"], d["lat"]]
                    }
                } for d in self.defects
            ]
        }


db = CentralCommandDatabase()


class CommandRequestHandler(BaseHTTPRequestHandler):
    """
    High-performance HTTP Request Handler for Central Urban Command.
    """

    def _send_json(self, data: Any, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/fleet":
            self._send_json(list(db.buses.values()))
        elif url.path == "/api/defects":
            self._send_json(db.defects)
        elif url.path == "/api/geojson":
            self._send_json(db.export_geojson())
        elif url.path == "/api/traffic":
            self._send_json({
                "hourly_volume_scanned": [1200, 7800, 5200, 4900, 5400, 7030, 8400, 4200],
                "vehicle_classification": {"cars_pct": 42, "bikes_pct": 28, "autos_pct": 14, "buses_pct": 8, "trucks_pct": 5, "pedestrians_pct": 3}
        elif url.path == "/api/contractors":
            from ai_engine.models.iwatchroad_engine import IWatchRoadContractorTracker
            self._send_json(IWatchRoadContractorTracker.MUNICIPAL_CONTRACTS)
        elif url.path == "/api/governance":
            from ai_engine.models.iwatchroad_engine import IWatchRoadContractorTracker
            self._send_json({
                "system": "iWatchRoad Municipal Governance Matrix",
                "active_contracts": IWatchRoadContractorTracker.MUNICIPAL_CONTRACTS,
                "lifecycle_stages": ["Reported", "Verified", "In Progress", "Fixed", "Closed"],
                "total_dockets_tracked": len(db.defects)
            })
        else:
            self._send_json({
                "status": "JUCC Urban Intelligence API Online",
                "framework": "iWatchRoad v2 + BEL Urban Sensing",
                "endpoints": [
                    "/api/fleet",
                    "/api/defects",
                    "/api/traffic",
                    "/api/geojson",
                    "/api/contractors",
                    "/api/governance"
                ]
            }, 200)

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/api/telemetry/ingest":
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode('utf-8'))
                db.ingest_telemetry(data)
                self._send_json({"status": "SUCCESS", "message": "Telemetry Ingested", "timestamp": datetime.now().isoformat()})
            except Exception as e:
                self._send_json({"status": "ERROR", "message": str(e)}, 400)
        else:
            self._send_json({"error": "Endpoint Not Found"}, 404)


def run_command_server(port: int = 8000):
    server = HTTPServer(('0.0.0.0', port), CommandRequestHandler)
    print(f"[JUCC Server] Central Command Server running at http://0.0.0.0:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
        print("\n[JUCC Server] Server stopped gracefully.")


if __name__ == "__main__":
    run_command_server(8000)
