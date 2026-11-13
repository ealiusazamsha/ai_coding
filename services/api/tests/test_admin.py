"""Operator policy tests; database writes are only available in configured mode."""
import os
from uuid import UUID
import pytest
from fastapi import HTTPException

from app.admin import (
    OfferUpsert, ProductCreate, ProductUpdate, SupplierCreate,
    current_operator,
)

def test_operator_defaults_to_closed(monkeypatch):
    monkeypatch.setenv("AACP_ENV", "test")
    monkeypatch.setenv("AACP_DEMO_MODE", "true")
    with pytest.raises(HTTPException) as exc:
        current_operator(UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"))
    assert exc.value.status_code == 503

def test_operator_requires_allowlisted_verified_id(monkeypatch):
    monkeypatch.setenv("AACP_ENV", "test")
    monkeypatch.setenv("AACP_DEMO_MODE", "false")
    monkeypatch.setenv("AACP_OPERATOR_USER_IDS", "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
    with pytest.raises(HTTPException) as exc:
        current_operator(UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"))
    assert exc.value.status_code == 403
    assert current_operator(UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")) is not None

def test_manual_offer_contract_has_no_verification_override():
    assert "source_verified" not in OfferUpsert.model_fields
    payload = OfferUpsert(
        product_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        supplier_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        supplier_sku="ABC", unit_cost_minor=1000,
        currency="BDT", quantity=5,
    )
    assert payload.quantity == 5

def test_products_start_as_drafts_and_allow_explicit_status():
    product = ProductCreate(sku="A-1", name="Demo home item", sale_price_minor=1600)
    assert product.currency == "BDT"
    assert ProductUpdate(status="active").status == "active"
    with pytest.raises(Exception):
        ProductUpdate(status="paid")
    with pytest.raises(Exception):
        SupplierCreate(name="Supplier", integration_type="arbitrary")
