"""Tenant-scoped merchant operations.

Every route requires a verified Supabase user ID in the operator allowlist.
Manual supplier offers are NEVER marked source-verified, so they cannot
authorize a purchase or a stock claim.
"""
import os
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db
from .models import AuditEvent, Order, OutboxEvent, Product, Supplier, SupplierOffer
from .security import current_user

router = APIRouter(prefix="/api/v1/admin", tags=["merchant-operations"])


class SupplierCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    integration_type: str = Field(pattern="^(api|file|manual)$")


class SupplierApproval(BaseModel):
    approved: bool


class SupplierOut(BaseModel):
    id: UUID
    name: str
    integration_type: str
    approved: bool


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=128)
    name: str = Field(min_length=2, max_length=200)
    description: str = Field(default="", max_length=3000)
    category: str = Field(default="General", min_length=2, max_length=120)
    sale_price_minor: int = Field(ge=0, le=10**13)
    currency: str = Field(default="BDT", pattern="^[A-Z]{3}$")


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=3000)
    category: str | None = Field(default=None, min_length=2, max_length=120)
    sale_price_minor: int | None = Field(default=None, ge=0, le=10**13)
    status: str | None = Field(default=None, pattern="^(draft|active|archived)$")


class ProductAdminOut(BaseModel):
    id: UUID
    sku: str
    name: str
    description: str
    category: str
    status: str
    sale_price_minor: int
    currency: str


class OfferUpsert(BaseModel):
    product_id: UUID
    supplier_id: UUID
    supplier_sku: str = Field(min_length=1, max_length=200)
    unit_cost_minor: int = Field(ge=0, le=10**13)
    currency: str = Field(pattern="^[A-Z]{3}$")
    quantity: int = Field(ge=0, le=1000000)


class OfferOut(BaseModel):
    id: UUID
    product_id: UUID
    supplier_id: UUID
    supplier_sku: str
    unit_cost_minor: int
    currency: str
    quantity: int
    synced_at: datetime
    source_verified: bool


def current_operator(user: UUID = Depends(current_user)) -> UUID:
    if settings().demo_mode:
        raise HTTPException(status_code=503, detail="Merchant operations require database mode")
    configured = os.getenv("AACP_OPERATOR_USER_IDS", "")
    if not configured.strip():
        raise HTTPException(status_code=503, detail="Operator allowlist is not configured")
    try:
        allowed = {UUID(entry.strip()) for entry in configured.split(",") if entry.strip()}
    except ValueError:
        raise HTTPException(status_code=503, detail="Operator allowlist is invalid")
    if user not in allowed:
        raise HTTPException(status_code=403, detail="Operator access denied")
    return user


def tenant() -> UUID:
    value = settings().tenant_id
    if str(value) == "00000000-0000-0000-0000-000000000001":
        raise HTTPException(status_code=503, detail="AACP tenant has not been provisioned")
    return value


def log_event(db: Session, user: UUID, action: str, resource: str, resource_id: UUID) -> None:
    correlation = str(uuid4())
    db.add(AuditEvent(
        tenant_id=tenant(), actor_type="operator", action=action,
        resource_type=resource, resource_id=str(resource_id),
        correlation_id=correlation,
        details={"actor_user_id": str(user)},
    ))
    db.add(OutboxEvent(
        tenant_id=tenant(), event_type=action,
        aggregate_id=str(resource_id), correlation_id=correlation,
        payload={"resource_type": resource},
    ))


def save(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflict with existing merchant record")


def get_supplier(db: Session, supplier_id: UUID) -> Supplier:
    obj = db.scalar(select(Supplier).where(Supplier.id == supplier_id, Supplier.tenant_id == tenant()))
    if obj is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return obj


def get_product(db: Session, product_id: UUID) -> Product:
    obj = db.scalar(select(Product).where(Product.id == product_id, Product.tenant_id == tenant()))
    if obj is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return obj


@router.get("/summary")
def summary(_user: UUID = Depends(current_operator), db: Session = Depends(get_db)):
    key = tenant()
    def count(model, *filters):
        return db.scalar(select(func.count()).select_from(model).where(model.tenant_id == key, *filters)) or 0
    return {
        "products": count(Product),
        "published_products": count(Product, Product.status == "active"),
        "suppliers": count(Supplier),
        "approved_suppliers": count(Supplier, Supplier.approved.is_(True)),
        "unverified_offers": count(SupplierOffer, SupplierOffer.source_verified.is_(False)),
        "pending_orders": count(Order, Order.status == "pending_payment"),
        "payment_processing_enabled": False,
        "supplier_purchasing_enabled": False,
    }


@router.get("/suppliers", response_model=list[SupplierOut])
def suppliers(_user: UUID = Depends(current_operator), db: Session = Depends(get_db)):
    return db.scalars(select(Supplier).where(Supplier.tenant_id == tenant()).order_by(Supplier.name).limit(300)).all()


@router.post("/suppliers", response_model=SupplierOut, status_code=201)
def create_supplier(payload: SupplierCreate, user: UUID = Depends(current_operator), db: Session = Depends(get_db)):
    obj = Supplier(tenant_id=tenant(), name=payload.name.strip(), integration_type=payload.integration_type, approved=False)
    db.add(obj)
    db.flush()
    log_event(db, user, "supplier.created", "supplier", obj.id)
    save(db)
    db.refresh(obj)
    return obj


@router.patch("/suppliers/{supplier_id}/approval", response_model=SupplierOut)
def approve_supplier(supplier_id: UUID, payload: SupplierApproval,
                     user: UUID = Depends(current_operator), db: Session = Depends(get_db)):
    obj = get_supplier(db, supplier_id)
    obj.approved = payload.approved
    log_event(db, user, "supplier.approval.changed", "supplier", obj.id)
    save(db)
    db.refresh(obj)
    return obj


@router.get("/products", response_model=list[ProductAdminOut])
def products(_user: UUID = Depends(current_operator), db: Session = Depends(get_db)):
    return db.scalars(select(Product).where(Product.tenant_id == tenant()).order_by(Product.name).limit(300)).all()


@router.post("/products", response_model=ProductAdminOut, status_code=201)
def create_product(payload: ProductCreate, user: UUID = Depends(current_operator), db: Session = Depends(get_db)):
    obj = Product(
        tenant_id=tenant(), sku=payload.sku.strip(), name=payload.name.strip(),
        description=payload.description, category=payload.category.strip(),
        status="draft", sale_price_minor=payload.sale_price_minor, currency=payload.currency,
    )
    db.add(obj)
    db.flush()
    log_event(db, user, "product.created", "product", obj.id)
    save(db)
    db.refresh(obj)
    return obj


@router.patch("/products/{product_id}", response_model=ProductAdminOut)
def update_product(product_id: UUID, payload: ProductUpdate,
                   user: UUID = Depends(current_operator), db: Session = Depends(get_db)):
    obj = get_product(db, product_id)
    changes = payload.model_dump(exclude_unset=True)
    for attr, value in changes.items():
        if value is None:
            raise HTTPException(status_code=422, detail=f"{attr} cannot be null")
        setattr(obj, attr, value.strip() if isinstance(value, str) else value)
    if "status" in changes and changes["status"] == "active" and obj.sale_price_minor < 1:
        raise HTTPException(status_code=422, detail="Published products require a positive price")
    log_event(db, user, "product.updated", "product", obj.id)
    save(db)
    db.refresh(obj)
    return obj


@router.get("/offers", response_model=list[OfferOut])
def offers(_user: UUID = Depends(current_operator), db: Session = Depends(get_db)):
    return db.scalars(select(SupplierOffer).where(SupplierOffer.tenant_id == tenant())
                      .order_by(SupplierOffer.synced_at.desc()).limit(300)).all()


@router.post("/offers", response_model=OfferOut, status_code=201)
def add_manual_offer(payload: OfferUpsert, user: UUID = Depends(current_operator), db: Session = Depends(get_db)):
    supplier = get_supplier(db, payload.supplier_id)
    product = get_product(db, payload.product_id)
    if supplier.integration_type not in {"manual", "file", "api"}:
        raise HTTPException(status_code=422, detail="Supplier integration type invalid")
    if product.currency != payload.currency:
        raise HTTPException(status_code=422, detail="Offer currency does not match product")
    if payload.unit_cost_minor > product.sale_price_minor:
        raise HTTPException(status_code=422, detail="Supplier cost exceeds current sale price")
    existing = db.scalar(select(SupplierOffer).where(
        SupplierOffer.tenant_id == tenant(), SupplierOffer.supplier_id == supplier.id,
        SupplierOffer.supplier_sku == payload.supplier_sku,
    ))
    if existing is None:
        existing = SupplierOffer(
            tenant_id=tenant(), supplier_id=supplier.id, product_id=product.id,
            supplier_sku=payload.supplier_sku, unit_cost_minor=payload.unit_cost_minor,
            currency=payload.currency, quantity=payload.quantity,
            synced_at=datetime.now(timezone.utc), source_verified=False,
        )
        db.add(existing)
    else:
        existing.product_id = product.id
        existing.unit_cost_minor = payload.unit_cost_minor
        existing.currency = payload.currency
        existing.quantity = payload.quantity
        existing.synced_at = datetime.now(timezone.utc)
        existing.source_verified = False  # operator edits invalidate upstream verification
    db.flush()
    log_event(db, user, "supplier.offer.manually_recorded", "supplier_offer", existing.id)
    save(db)
    db.refresh(existing)
    return existing


@router.get("/audit")
def audit(limit: int = Query(default=30, ge=1, le=100),
          _user: UUID = Depends(current_operator), db: Session = Depends(get_db)):
    rows = db.scalars(select(AuditEvent).where(AuditEvent.tenant_id == tenant())
                      .order_by(AuditEvent.occurred_at.desc()).limit(limit)).all()
    return [
        {"id": str(event.id), "action": event.action,
         "resource_type": event.resource_type, "resource_id": event.resource_id,
         "occurred_at": event.occurred_at.isoformat(), "correlation_id": event.correlation_id}
        for event in rows
    ]
