"""Development-only WebSocket protocol.

No payment, supplier, customer or private order data is transmitted here.
Production realtime will require authenticated, tenant-scoped subscriptions
backed by a durable event bus rather than per-process socket state.
"""
import json
import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
MAX_MESSAGES = 80
MAX_PAYLOAD_SIZE = 1024

def allowed_origins() -> set[str]:
    """Origin checks are mandatory because WebSocket requests bypass CORS middleware."""
    return {v.strip() for v in os.getenv("AACP_ALLOWED_ORIGINS", "http://localhost:3000").split(",") if v.strip()}

@router.websocket("/ws/v1/demo")
async def demo_ws(ws: WebSocket):
    is_demo = os.getenv("AACP_DEMO_MODE", "true").lower() == "true"
    environment = os.getenv("AACP_ENV", "development").lower()
    origin = ws.headers.get("origin")
    if not is_demo or environment not in {"development", "test"} or origin not in allowed_origins():
        await ws.close(code=1008)
        return

    await ws.accept()
    await ws.send_json({
        "type": "system.connected", "version": 1, "mode": "demo",
        "message": "Development event channel; no orders or payments.",
    })
    try:
        for _ in range(MAX_MESSAGES):
            message = await ws.receive_text()
            if len(message.encode("utf-8")) > MAX_PAYLOAD_SIZE:
                await ws.close(code=1009)
                return
            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "code": "invalid_json"})
                continue
            if not isinstance(payload, dict):
                await ws.send_json({"type": "error", "code": "invalid_payload"})
                continue
            command = payload.get("type")
            if command == "ping":
                await ws.send_json({"type": "pong", "version": 1, "mode": "demo"})
            elif command == "catalog.preview":
                await ws.send_json({"type": "catalog.preview", "version": 1, "mode": "demo", "product_count": 4})
            else:
                await ws.send_json({"type": "error", "code": "unsupported_event"})
        await ws.close(code=1008)
    except WebSocketDisconnect:
        pass
