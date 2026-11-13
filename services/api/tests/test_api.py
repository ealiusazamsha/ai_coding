import os
os.environ["AACP_DEMO_MODE"] = "true"
os.environ["AACP_ENV"] = "test"
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_health():
    data = client.get("/health").json()
    assert data["status"] == "ok" and data["demo"] is True

def test_catalog_filters():
    response = client.get("/api/v1/products", params={"category": "Audio"})
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_product_not_found():
    assert client.get("/api/v1/products/no-such-product").status_code == 404

def test_assistant_is_explicitly_demo():
    response = client.post("/api/v1/assistant/demo", json={"question": "headphones"})
    assert response.status_code == 200
    assert response.json()["mode"] == "deterministic-demo"
    assert "not a live AI agent" in response.json()["reply"]

def test_no_fake_checkout():
    assert client.post("/api/v1/checkout", json={}).status_code == 404
