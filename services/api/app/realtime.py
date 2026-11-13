"""Development-only WebSocket protocol.

No payment, supplier, customer or private order data is transmitted here.
Production realtime will require authenticated, tenant-scoped subscriptions
backed by a durable event bus rather than per-process socket state.
"""
import asyncio
import json
import os
from uuid import UUID
import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

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


async def verify_customer_token(token: str) -> UUID | None:
    """Server-side Supabase Auth introspection; claims in WebSocket messages are never trusted."""
    from .config import settings
    c = settings()
    if not c.supabase_url or not c.supabase_publishable_key:
        return None
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(
                c.supabase_url + "/auth/v1/user",
                headers={"apikey": c.supabase_publishable_key,
                         "Authorization": "Bearer " + token},
            )
        if response.status_code != 200:
            return None
        return UUID(str(response.json()["id"]))
    except (httpx.HTTPError, ValueError, KeyError):
        return None


@router.websocket("/ws/v1/customer")
async def authenticated_customer_ws(ws: WebSocket):
    """Authenticated, customer-scoped on-demand snapshots.

    Not yet a durable event delivery channel: no Redis, DB LISTEN/NOTIFY,
    multi-instance fanout, unread tracking or automatic push is claimed.
    """
    from .config import settings, DEMO_TENANT
    c = settings()
    if (c.demo_mode or not c.database_url or c.tenant_id == DEMO_TENANT or
            ws.headers.get("origin") not in allowed_origins()):
        await ws.close(code=1008)
        return

    await ws.accept()
    try:
        initial = await asyncio.wait_for(ws.receive_text(), timeout=8)
        if len(initial.encode("utf-8")) > 8192:
            await ws.close(code=1009)
            return
        try:
            authorization = json.loads(initial)
        except json.JSONDecodeError:
            await ws.close(code=1008)
            return
        if not isinstance(authorization, dict) or authorization.get("type") != "auth":
            await ws.close(code=1008)
            return
        token = authorization.get("access_token")
        if not isinstance(token, str) or not (16 <= len(token) <= 7500):
            await ws.close(code=1008)
            return
        user_id = await verify_customer_token(token)
        if user_id is None:
            await ws.close(code=1008)
            return
        del token
        await ws.send_json({"type": "auth.ok", "mode": "customer", "version": 1})

        # Limit a verified-token socket to at most 15 minutes; require re-authentication.
        deadline = asyncio.get_running_loop().time() + 900
        for _ in range(100):
            remaining = deadline - asyncio.get_running_loop().time()
            if remaining <= 0:
                await ws.close(code=1008)
                return
            text = await asyncio.wait_for(ws.receive_text(), timeout=remaining)
            if len(text.encode("utf-8")) > 2048:
                await ws.close(code=1009)
                return
            try:
                message = json.loads(text)
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "code": "invalid_json"})
                continue
            if not isinstance(message, dict):
                await ws.send_json({"type": "error", "code": "invalid_payload"})
                continue
            command = message.get("type")
            if command == "ping":
                await ws.send_json({"type": "pong", "mode": "customer", "version": 1})
            elif command in ("order.snapshot", "support.snapshot"):
                try:
                    record_id = UUID(str(message.get("id", "")))
                except ValueError:
                    await ws.send_json({"type": "error", "code": "invalid_id"})
                    continue
                from sqlalchemy.orm import Session
                from .database import engine
                from .commerce import owned_order
                from .support import owned_case
                try:
                    with Session(engine()) as db:
                        if command == "order.snapshot":
                            record = owned_order(db, record_id, user_id)
                            payload = record.model_dump(mode="json")
                        else:
                            case = owned_case(db, record_id, user_id)
                            payload = {"id": str(case.id), "status": case.status,
                                       "updated_at": case.updated_at.isoformat()}
                    await ws.send_json({"type": command, "version": 1, "data": payload})
                except HTTPException:
                    await ws.send_json({"type": "error", "code": "not_found"})
                except Exception:
                    # No SQL errors, credentials or resource identifiers in socket responses.
                    await ws.send_json({"type": "error", "code": "database_unavailable"})
            else:
                await ws.send_json({"type": "error", "code": "unsupported_event"})
        await ws.close(code=1008)
    except (WebSocketDisconnect, asyncio.TimeoutError):
        try:
            await ws.close(code=1008)
        except RuntimeError:
            pass
