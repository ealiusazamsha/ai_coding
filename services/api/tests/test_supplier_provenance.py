"""Manual offers must not create verified stock or a purchasable order."""
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.models import Base, Tenant, Product, Supplier, SupplierOffer
from app.config import DEMO_TENANT
from app.commerce import listing, quote
from app.schemas import QuoteRequest


def test_unverified_offer_does_not_claim_stock():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        execution_options={"schema_translate_map": {"aacp": None}},
    )
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(Tenant(id=DEMO_TENANT, name="Test merchant"))
        supplier = Supplier(tenant_id=DEMO_TENANT, name="Manual operator entry",
                            approved=True, integration_type="manual")
        product = Product(tenant_id=DEMO_TENANT, sku="SKU-100", name="Test headphones",
                          status="active", sale_price_minor=4500, currency="BDT")
        db.add_all([supplier, product])
        db.flush()
        offer = SupplierOffer(
            tenant_id=DEMO_TENANT, supplier_id=supplier.id, product_id=product.id,
            supplier_sku="TEST-1", unit_cost_minor=3000, currency="BDT",
            quantity=8, synced_at=datetime.now(timezone.utc), source_verified=False,
        )
        db.add(offer)
        db.commit()
        request = QuoteRequest(items=[{"product_id": product.id, "quantity": 1}])
        assert not quote(db, request).can_checkout
        assert not listing(db)[0].in_stock
        offer.source_verified = True  # Simulated trusted provider confirmation, not exposed via API.
        db.commit()
        assert quote(db, request).can_checkout
        assert listing(db)[0].in_stock


def test_schema_has_immutable_source_provenance_fields():
    fields = set(SupplierOffer.__table__.columns.keys())
    assert {"source_verified", "source_reference", "source_verified_at"} <= fields
