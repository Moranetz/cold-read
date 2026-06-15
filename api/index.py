"""Cold Read — single WSGI app (Vercel entrypoint + local dev).

Serves the page on GET and scores a cold message on POST /api/score. Pure
stdlib + numpy via the engine; no web framework. The Persuasion-Max engine is
vendored unmodified at ./core (see core/PROVENANCE.md) and bundled alongside
this module so the function is self-contained.
"""
import json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import engine_adapter  # noqa: E402

_HTML = open(os.path.join(os.path.dirname(__file__), "index.html"), "rb").read()


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/").rstrip("/") or "/"

    if method == "POST" and path == "/api/score":
        try:
            size = int(environ.get("CONTENT_LENGTH") or 0)
            body = json.loads(environ["wsgi.input"].read(size) or b"{}")
            payload = json.dumps(engine_adapter.score(body.get("text", ""))).encode()
            start_response("200 OK", [("Content-Type", "application/json"),
                                      ("Access-Control-Allow-Origin", "*")])
            return [payload]
        except Exception as e:  # noqa: BLE001
            start_response("500 Internal Server Error",
                           [("Content-Type", "application/json")])
            return [json.dumps({"error": str(e)}).encode()]

    if path == "/api/score":  # GET on the endpoint → health
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps({"ok": True, "service": "cold-read"}).encode()]

    start_response("200 OK", [("Content-Type", "text/html; charset=utf-8")])
    return [_HTML]
