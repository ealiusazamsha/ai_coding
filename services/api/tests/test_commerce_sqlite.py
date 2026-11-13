"""Database integration tests running with SQLite schema translation.

Supabase/PostgreSQL-specific constraints still require cloud integration tests.
"""
import os
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4

os.environ["AACP_ENV"] = "test"
os.environ["AACP_DEMO_MODE"] = "true"
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from fastapi import HTTPException
import pytest
from app.config import DEMO_TENANT
from app.models import Base, Product, Supplier, SupplierOffer, Tenant, Order, OutboxEvent, AuditEvent
from app.schemas import QuoteRequest, OrderRequest
from app.commerce import quote, create_pending_order, owned_order

@pytest.fixture
def database():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread":False},
        poolclass=StaticPool,
        execution_options={"schema_translate_map":{"aacp":None}},
    )
    Base.metadata.create_all(engine)
    with Session(engine, expire_on_commit=False) as db:
        db.add(Tenant(id=DEMO_TENANT,name="Demo Merchant"))
        supplier=Supplier(tenant_id=DEMO_TENANT,name="Approved Test Supplier",integration_type="api",approved=True)
        product=Product(tenant_id=DEMO_TENANT,sku="TEST-A1",name="Test Product",description="Test",
                        category="Home",status="active",sale_price_minor=4000,currency="BDT")
        db.add_all([supplier,product])
        db.flush()
        db.add(SupplierOffer(tenant_id=DEMO_TENANT,supplier_id=supplier.id,product_id=product.id,
                             supplier_sku="SUP-A1",unit_cost_minor=2000,currency="BDT",
                             quantity=10,synced_at=datetime.now(timezone.utc)))
        db.commit()
        yield db,product,supplier

def test_quote_never_trusts_client_pricing(database):
    db,product,_=database
    q=quote(db,QuoteRequest(items=[{"product_id":product.id,"quantity":2}]))
    assert q.can_checkout and q.subtotal_minor==8000 and q.currency=="BDT"

def test_fulfillment_fails_for_stale_supplier(database):
    db,product,supplier=database
    offer=db.query(SupplierOffer).filter_by(product_id=product.id).one()
    offer.synced_at=datetime.now(timezone.utc)-timedelta(days=1)
    db.commit()
    q=quote(db,QuoteRequest(items=[{"product_id":product.id,"quantity":1}]))
    assert not q.can_checkout
    assert "availability" in q.lines[0].reason

def test_order_idempotency_ownership_and_outbox(database):
    db,product,_=database
    alice,bob=uuid4(),uuid4()
    order=OrderRequest(items=[{"product_id":product.id,"quantity":2}],idempotency_key="safe-key-0000000001")
    first=create_pending_order(db,alice,order)
    second=create_pending_order(db,alice,order)
    assert first.order_id==second.order_id
    assert first.total_minor==8000 and first.status=="pending_payment"
    assert db.query(Order).count()==1
    assert db.query(OutboxEvent).count()==1
    assert db.query(AuditEvent).count()==1
    assert owned_order(db,first.order_id,alice).order_id==first.order_id
    with pytest.raises(HTTPException) as failure:
        owned_order(db,first.order_id,bob)
    assert failure.value.status_code==404
    with pytest.raises(HTTPException) as conflict:
        create_pending_order(db,bob,order)
    assert conflict.value.status_code==409
