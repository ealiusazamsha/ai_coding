"""Browser clients need cross-origin PATCH support for merchant and support workflows."""
import os
from fastapi.testclient import TestClient
from app.main import app


def test_operator_preflight_allows_patch_and_authorization():
    client = TestClient(app)
    response = client.options(
        "/api/v1/admin/products/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        headers={
            "origin": "http://localhost:3000",
            "access-control-request-method": "PATCH",
            "access-control-request-headers": "authorization,content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
    assert "PATCH" in response.headers.get("access-control-allow-methods", "")
