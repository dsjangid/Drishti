"""
JUCC Edge AI Engine - Local Neural Inference API Server
Module: ai_engine/server.py

Provides a high-performance local HTTP server for running
real YOLOv8 deep learning neural inference on uploaded video files.
"""

import os
import sys
import json
import time
import cgi
from http.server import HTTPServer, SimpleHTTPRequestHandler
from run_inference import DeepPotholeInferenceEngine


PORT = 8080
DASHBOARD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENGINE = None


class NeuralInferenceHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DASHBOARD_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        global ENGINE
        if self.path == '/api/upload_and_process':
            try:
                content_len = int(self.headers.get('Content-Length', 0))
                raw_bytes = self.rfile.read(content_len)

                # Save temporary upload
                uploads_dir = os.path.join(DASHBOARD_DIR, "sample_videos")
                os.makedirs(uploads_dir, exist_ok=True)
                temp_video_path = os.path.join(uploads_dir, "latest_uploaded_dashcam.mp4")

                with open(temp_video_path, 'wb') as f:
                    f.write(raw_bytes)

                print(f"[*] Ingested custom video: {len(raw_bytes)/(1024*1024):.2f} MB")
                print("[*] Running YOLOv8 Deep Learning Neural Network...")

                if ENGINE is None:
                    ENGINE = DeepPotholeInferenceEngine()

                detections = ENGINE.process_video(temp_video_path)

                response_data = {
                    "status": "success",
                    "total_anomaly_frames": len(detections),
                    "detections": detections
                }

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response_data).encode())
            except Exception as e:
                print(f"[!] Processing error: {e}")
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            super().do_POST()


def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, NeuralInferenceHandler)
    print("=" * 70)
    print("  JUCC YOLOv8 Deep Learning AI Dashboard & Inference Server")
    print(f"  Live URL: http://localhost:{PORT}")
    print(f"  Root Dir: {DASHBOARD_DIR}")
    print("=" * 70)
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
