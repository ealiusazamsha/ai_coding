import os
os.environ["AACP_ENV"] = "test"
os.environ["AACP_DEMO_MODE"] = "true"
os.environ.pop("DATABASE_URL", None)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_and_capabilities():
    assert client.get("/health").json()["demo"] is True
    assert client.get("/api/v1/capabilities").json()["live_checkout"] is False

def test_catalog_filters():
    response = client.get("/api/v1/products", params={"category": "Audio"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["in_stock"] is False

def test_product_not_found():
    assert client.get("/api/v1/products/no-such-product").status_code == 404

def test_assistant_is_explicitly_demo():
    response = client.post("/api/v1/assistant/demo", json={"question": "headphones"})
    assert response.status_code == 200
    assert response.json()["mode"] == "deterministic-demo"
    assert "not live AI" in response.json()["reply"]

def test_payments_and_orders_disabled_in_preview():
    assert client.post("/api/v1/checkout", json={}).status_code == 503
    assert client.post("/api/v1/quotes", json={"items":[{"product_id":"00000000-0000-0000-0000-000000000001","quantity":1}]}).status_code == 503
    assert client.post("/api/v1/orders", json={"items":[],"idempotency_key":"a-valid-key-123"}).status_code in (401,422)
    assert client.get("/ready").status_code == 503

def test_admin_route_disabled_in_demo_mode():
    result = client.get("/api/v1/admin/summary")
    # Authentication is required and/or the operator API remains disabled.
    assert result.status_code in (401, 503)
