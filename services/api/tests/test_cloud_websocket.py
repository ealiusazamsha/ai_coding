"""Authenticated WS protocol: no anonymous access and no client-declared user IDs."""
import os
from uuid import UUID
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
import pytest

from app.main import app
from app import realtime

client = TestClient(app)
ORIGIN = {"origin": "http://localhost:3000"}
USER = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")


def test_cloud_websocket_rejects_demo_mode(monkeypatch):
    monkeypatch.setenv("AACP_DEMO_MODE", "true")
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/v1/customer", headers=ORIGIN) as ws:
            ws.receive_json()


def test_cloud_websocket_requires_valid_auth(monkeypatch):
    monkeypatch.setenv("AACP_DEMO_MODE", "false")
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("AACP_DEFAULT_TENANT_ID", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/v1/customer", headers=ORIGIN) as ws:
            ws.send_json({"type": "ping"})
            ws.receive_json()


def test_cloud_websocket_handshake_and_ping(monkeypatch):
    monkeypatch.setenv("AACP_DEMO_MODE", "false")
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("AACP_DEFAULT_TENANT_ID", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    async def fake_verify(token):
        return USER if token == "test-only-valid-jwt-placeholder" else None
    monkeypatch.setattr(realtime, "verify_customer_token", fake_verify)
    with client.websocket_connect("/ws/v1/customer", headers=ORIGIN) as ws:
        ws.send_json({"type": "auth", "access_token": "test-only-valid-jwt-placeholder"})
        assert ws.receive_json()["type"] == "auth.ok"
        ws.send_json({"type": "ping", "user_id": "someone-else"})
        assert ws.receive_json()["type"] == "pong"
        ws.send_json({"type": "capture_payment"})
        assert ws.receive_json()["code"] == "unsupported_event"


def test_cloud_websocket_cross_origin_rejected(monkeypatch):
    monkeypatch.setenv("AACP_DEMO_MODE", "false")
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("AACP_DEFAULT_TENANT_ID", "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/v1/customer",
            headers={"origin": "https://example.invalid"}) as ws:
            ws.receive_json()
