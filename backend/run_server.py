#!/usr/bin/env python3
import sys
import os
import uvicorn

# Add backend directory to python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))
sys.path.insert(0, os.path.dirname(__file__))

if __name__ == "__main__":
    print("=" * 65)
    print("  दृष्टि (Drishti) — Urban Road Intelligence Backend")
    print("  ═══════════════════════════════════════════════════════════════")
    print("  🚀 Starting FastAPI server at http://localhost:8000")
    print("  📖 Interactive Swagger UI Docs : http://localhost:8000/docs")
    print("  📖 Interactive ReDoc API Specs : http://localhost:8000/redoc")
    print("  🌐 WebSocket Live Telemetry    : ws://localhost:8000/ws/telemetry")
    print("=" * 65)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True
    )
