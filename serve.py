#!/usr/bin/env python3
"""Local dev server — runs the same WSGI app Vercel deploys (api/index.py),
so what you see locally is what ships.

    python serve.py            # http://localhost:8000
"""
import os, sys
from wsgiref.simple_server import make_server

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "api"))
from index import app  # noqa: E402  (api/index.py)

PORT = int(os.environ.get("PORT", "8000"))

if __name__ == "__main__":
    print(f"Cold Read → http://localhost:{PORT}")
    make_server("0.0.0.0", PORT, app).serve_forever()
