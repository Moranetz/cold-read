#!/usr/bin/env python3
"""Local dev server for Cold Read. Stdlib only — serves the static front end
and the /api/score endpoint backed by the offline engine. Mirrors the Vercel
routing so the same front end works in both places.

    python serve.py            # http://localhost:8000
"""
import json, os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "api"))
import engine_adapter  # noqa: E402

PUBLIC = ROOT  # static served from repo root (index.html lives here, mirrors Vercel)
PORT = int(os.environ.get("PORT", "8000"))


class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
        elif isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            return self._serve_file("index.html", "text/html; charset=utf-8")
        if path == "/api/buyers":
            return self._send(200, engine_adapter.list_buyers())
        safe = os.path.normpath(path).lstrip("/")
        if safe and os.path.isfile(os.path.join(PUBLIC, safe)):
            return self._serve_file(safe, self._ctype(safe))
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        if self.path.split("?")[0] != "/api/score":
            return self._send(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n) or b"{}")
            result = engine_adapter.score(payload.get("text", ""))
            return self._send(200, result)
        except Exception as e:  # noqa: BLE001
            return self._send(500, {"error": str(e)})

    def _serve_file(self, rel, ctype):
        try:
            with open(os.path.join(PUBLIC, rel), "rb") as f:
                return self._send(200, f.read(), ctype)
        except FileNotFoundError:
            return self._send(404, {"error": "not found"})

    @staticmethod
    def _ctype(p):
        if p.endswith(".css"): return "text/css"
        if p.endswith(".js"):  return "application/javascript"
        if p.endswith(".svg"): return "image/svg+xml"
        return "application/octet-stream"

    def log_message(self, *a):  # quiet
        pass


if __name__ == "__main__":
    print(f"Cold Read → http://localhost:{PORT}")
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
