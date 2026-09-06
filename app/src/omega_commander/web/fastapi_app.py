"""
Optional adapter. Requires `pip install .[web]`.
This module intentionally exposes no direct broker-order endpoint.
"""
from __future__ import annotations

def create_app(read_provider=None, command_provider=None):
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import HTMLResponse
    except ImportError as e:
        raise RuntimeError("Install optional dependency group: web") from e

    app=FastAPI(title="ATLAS OMEGA Commander RU",docs_url="/technical/api-docs")

    @app.get("/",response_class=HTMLResponse)
    def home():
        from pathlib import Path
        p=Path(__file__).resolve().parent.parent/"static"/"index.html"
        return p.read_text(encoding="utf-8")

    @app.get("/api/v1/status")
    def status():
        if read_provider is None:
            return {"ok":True,"message_ru":"Демонстрационный режим Commander.","data":{}}
        return read_provider.status()

    @app.post("/api/v1/commands")
    def commands(payload: dict):
        if command_provider is None:
            raise HTTPException(status_code=503,detail="Control provider not connected")
        return command_provider.execute(payload)

    # No /broker/order endpoint by design.
    return app
