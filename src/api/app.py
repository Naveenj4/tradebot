"""
src/api/app.py
FastAPI Application Entry Point with WebSocket Telemetry & React Production Frontend Integration.
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import asyncio
import json
import logging

from src.api.routes import monitor, settings, control, orders, reports

logger = logging.getLogger("TradeBot.App")

app = FastAPI(
    title="TradeBot 1.0 - Algorithmic Options Trading Gateway",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(monitor.router)
app.include_router(settings.router)
app.include_router(control.router)
app.include_router(orders.router)
app.include_router(reports.router)

# Mount Vite React build assets if present
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if (FRONTEND_DIST / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")

# Active WebSocket clients list
connected_clients: list[WebSocket] = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        # Send initial full state snapshot
        await websocket.send_json({"type": "STATE_UPDATE", "data": monitor.state_cache})
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("action") == "PING":
                    await websocket.send_json({"type": "PONG"})
            except Exception:
                pass
    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)
    except Exception:
        if websocket in connected_clients:
            connected_clients.remove(websocket)

async def broadcast_state():
    """Broadcasts current state cache to all connected WebSocket clients."""
    if not connected_clients:
        return
    payload = json.dumps({"type": "STATE_UPDATE", "data": monitor.state_cache})
    for client in list(connected_clients):
        try:
            await client.send_text(payload)
        except Exception:
            if client in connected_clients:
                connected_clients.remove(client)

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """Serves the compiled React Vite production application."""
    index_file = FRONTEND_DIST / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h1>TradeBot 1.0 React App is building...</h1>")
