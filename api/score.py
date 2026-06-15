"""Vercel serverless entry point — POST /api/score → offline engine result."""
import json
from http.server import BaseHTTPRequestHandler

import engine_adapter


class handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        b = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n) or b"{}")
            self._send(200, engine_adapter.score(payload.get("text", "")))
        except Exception as e:  # noqa: BLE001
            self._send(500, {"error": str(e)})

    def do_GET(self):
        self._send(200, {"ok": True, "service": "cold-read", "post": "text -> scores"})

    def log_message(self, *a):
        pass
