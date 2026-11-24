"""Local dashboard. No cloud account and no external assets.

Served by the Jetson on the LAN or on an access point the user configures.
Live updates use server-sent events. ``/api/snapshot`` is the same data for
a client that does not keep a stream open.
"""

from __future__ import annotations

import asyncio
import json
from importlib.resources import files

_PAGE = None


def load_page() -> str:
    global _PAGE
    if _PAGE is None:
        _PAGE = (files("battery_monitor.web") / "index.html").read_text(encoding="utf-8")
    return _PAGE


def create_app(get_snapshot, interval_s: float = 0.5):
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, StreamingResponse

    app = FastAPI(title="Battery monitor", docs_url=None, redoc_url=None)

    @app.get("/", response_class=HTMLResponse)
    def index():
        return HTMLResponse(load_page())

    @app.get("/api/snapshot")
    def snapshot():
        return get_snapshot()

    @app.get("/events")
    async def events():
        async def stream():
            while True:
                payload = json.dumps(get_snapshot(), separators=(",", ":"))
                yield f"data: {payload}\n\n"
                await asyncio.sleep(interval_s)

        return StreamingResponse(stream(), media_type="text/event-stream")

    return app
