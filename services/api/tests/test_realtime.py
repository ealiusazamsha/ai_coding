"""WebSocket regression suite: local preview only."""
import os
import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

os.environ["AACP_ENV"] = "test"
os.environ["AACP_DEMO_MODE"] = "true"
from app.main import app

client = TestClient(app)
LOCAL_ORIGIN = {"origin": "http://localhost:3000"}

def test_websocket_connect_and_heartbeat():
    with client.websocket_connect("/ws/v1/demo", headers=LOCAL_ORIGIN) as ws:
        connected = ws.receive_json()
        assert connected["type"] == "system.connected"
        assert connected["mode"] == "demo"
        ws.send_json({"type": "ping"})
        assert ws.receive_json()["type"] == "pong"
        ws.send_json({"type": "catalog.preview"})
        assert ws.receive_json()["product_count"] == 4

def test_invalid_events_do_not_execute_commands():
    with client.websocket_connect("/ws/v1/demo", headers=LOCAL_ORIGIN) as ws:
        ws.receive_json()
        ws.send_json({"type": "capture_payment"})
        assert ws.receive_json()["code"] == "unsupported_event"
        ws.send_text("not-json")
        assert ws.receive_json()["code"] == "invalid_json"

def test_cross_origin_rejected():
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/v1/demo", headers={"origin": "https://example.invalid"}) as ws:
            ws.receive_json()

def test_missing_origin_rejected():
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/v1/demo") as ws:
            ws.receive_json()

def test_oversized_message_closed():
    with client.websocket_connect("/ws/v1/demo", headers=LOCAL_ORIGIN) as ws:
        ws.receive_json()
        ws.send_text("x" * 1200)
        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_json()
        assert exc.value.code == 1009

def test_websocket_rejected_outside_demo(monkeypatch):
    monkeypatch.setenv("AACP_ENV", "production")
    with pytest.raises(Exception):
        with client.websocket_connect("/ws/v1/demo", headers=LOCAL_ORIGIN) as ws:
            ws.receive_json()
