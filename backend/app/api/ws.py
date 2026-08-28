import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from app.services.fleet_simulator import FleetSimulator
from app.db.session import SessionLocal
from app.models.bus import Bus

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast_json(self, data: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection)

manager = ConnectionManager()

@router.websocket("/telemetry")
async def websocket_telemetry_stream(websocket: WebSocket):
    """
    Real-time WebSocket telemetry stream.
    Broadcasts live GPS movement, speed vectors, and defect alerts across all 10 transit buses.
    """
    await manager.connect(websocket)
    step = 0.0

    try:
        while True:
            step = (step + 0.02) % 1.0
            
            # Fetch active bus IDs from DB
            db = SessionLocal()
            try:
                buses = db.query(Bus).all()
                fleet_packet = []
                for b in buses:
                    pos = FleetSimulator.get_interpolated_position(b.id, step)
                    fleet_packet.append({
                        "bus_id": b.id,
                        "driver": b.driver_name,
                        "route": b.route_name,
                        "lat": pos["lat"],
                        "lng": pos["lng"],
                        "speed": pos["speed"],
                        "safety_score": b.driver_safety_score,
                        "is_active": b.is_active
                    })
            finally:
                db.close()

            payload = {
                "event": "FLEET_TELEMETRY_UPDATE",
                "timestamp": asyncio.get_event_loop().time(),
                "fleet_size": len(fleet_packet),
                "buses": fleet_packet
            }

            await websocket.send_json(payload)
            await asyncio.sleep(1.0) # 1Hz telemetry frequency

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

