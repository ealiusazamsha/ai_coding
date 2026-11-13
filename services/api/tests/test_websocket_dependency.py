"""Make sure the ASGI server can actually accept WebSocket upgrades.

The in-process FastAPI TestClient does not require the Uvicorn server protocol,
so without this test REST/WS unit tests may pass while real Docker WS upgrades fail.
"""
from importlib.util import find_spec

from app.main import app

def test_uvicorn_websocket_protocol_is_installed():
    assert find_spec("websockets") is not None, (
        "Uvicorn requires WebSocket support: install uvicorn[standard]"
    )

def test_demo_websocket_is_registered():
    assert any(route.path == "/ws/v1/demo" for route in app.routes)
