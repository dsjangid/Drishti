"""
JUCC Edge AI Engine - Local Neural Inference API Server
Module: ai_engine/server.py

Provides a high-performance local HTTP/WebSocket API for running
real YOLOv8 deep learning neural inference on uploaded video files.
"""

import os
import sys
import json
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.parse
from run_inference import DeepPotholeInferenceEngine


PORT = 8080
ENGINE = None


class NeuralInferenceHandler(SimpleHTTPRequestHandler):
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
        if self.path == '/api/process_video':
            content_len = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_len)
            
            try:
                data = json.loads(post_body.decode('utf-8'))
                video_path = data.get('video_path')
                
                if not video_path or not os.path.exists(video_path):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": f"Video not found: {video_path}"}).encode())
                    return

                if ENGINE is None:
                    ENGINE = DeepPotholeInferenceEngine()

                detections = ENGINE.process_video(video_path)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "detections": detections}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            super().do_POST()


def run_server():
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, NeuralInferenceHandler)
    print("=" * 60)
    print(f"  JUCC YOLOv8 Neural Inference Server running on http://localhost:{PORT}")
    print("=" * 60)
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
