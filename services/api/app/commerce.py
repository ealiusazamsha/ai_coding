"""Commerce rules: no amount, tenant or payment status accepted from client."""
import hashlib
import json
from datetime import datetime, timezone
from uuid import UUID, uuid4
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .config import settings
from .domain import offer_eligible
from .models import Product, SupplierOffer, Supplier, Order, OrderItem, AuditEvent, OutboxEvent
from .schemas import QuoteRequest, QuoteResponse, QuoteLine, OrderRequest, OrderOut, ProductOut

def listing(db: Session, search: str = "", category: str = "") -> list[ProductOut]:
    tenant = settings().tenant_id
    statement = select(Product).where(Product.tenant_id == tenant, Product.status == "active")
    if category:
        statement = statement.where(Product.category == category)
    items = db.scalars(statement.order_by(Product.name).limit(100)).all()
    if search:
        items = [p for p in items if search.lower() in (p.name+" "+p.description).lower()]
    # Only source-verified, fresh offers from approved suppliers can signal availability.
    available: set[UUID] = set()
    if items:
        product_map = {p.id: p for p in items}
        offers = db.execute(
            select(SupplierOffer, Supplier)
            .join(Supplier, (Supplier.id == SupplierOffer.supplier_id) &
                  (Supplier.tenant_id == tenant))
            .where(SupplierOffer.tenant_id == tenant,
                   SupplierOffer.product_id.in_(list(product_map)),
                   SupplierOffer.source_verified.is_(True))
        ).all()
        for offer, supplier in offers:
            product = product_map.get(offer.product_id)
            if (product is not None and offer.currency == product.currency
                    and product.sale_price_minor > 0 and offer_eligible(
                        offer.quantity, 1, offer.synced_at, supplier.approved,
                        offer.unit_cost_minor, product.sale_price_minor)):
                available.add(product.id)
    return [ProductOut(id=str(p.id), name=p.name, category=p.category,
                       description=p.description, price_minor=p.sale_price_minor,
                       currency=p.currency, in_stock=p.id in available, emoji="🛍️") for p in items]

def quote(db: Session, request: QuoteRequest) -> QuoteResponse:
    tenant = settings().tenant_id
    amounts: list[QuoteLine] = []
    currency: str | None = None
    for line in request.items:
        product = db.scalar(select(Product).where(Product.id == line.product_id, Product.tenant_id == tenant, Product.status == "active"))
        if product is None:
            raise HTTPException(status_code=422, detail=f"Product unavailable: {line.product_id}")
        if currency is not None and product.currency != currency:
            raise HTTPException(status_code=422, detail="Mixed-currency carts not supported")
        currency = product.currency
        offers = db.execute(
            select(SupplierOffer, Supplier)
            .join(Supplier, (Supplier.id == SupplierOffer.supplier_id) & (Supplier.tenant_id == tenant))
            .where(SupplierOffer.product_id == product.id, SupplierOffer.tenant_id == tenant)
        ).all()
        eligible = any(
            offer.source_verified and offer.currency == product.currency and offer_eligible(
                offer.quantity, line.quantity, offer.synced_at, supplier.approved,
                offer.unit_cost_minor, product.sale_price_minor)
            for offer, supplier in offers
        )
        amounts.append(QuoteLine(
            product_id=str(product.id), quantity=line.quantity, price_minor=product.sale_price_minor,
            subtotal_minor=product.sale_price_minor * line.quantity,
            available=eligible, reason=None if eligible else "No verified recent supplier availability"
        ))
    subtotal = sum(line.subtotal_minor for line in amounts)
    return QuoteResponse(currency=currency or "BDT", lines=amounts, subtotal_minor=subtotal,
                         can_checkout=all(line.available for line in amounts),
                         disclaimer="Quote excludes tax, customs and shipping. Payment integration is not active.")

def request_fingerprint(request: OrderRequest, user_id: UUID) -> str:
    canonical = {
        "user": str(user_id),
        "items": sorted([{"id":str(line.product_id),"qty":line.quantity} for line in request.items], key=lambda v:(v["id"],v["qty"])),
    }
    return hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",",":")).encode()).hexdigest()

def create_pending_order(db: Session, user_id: UUID, request: OrderRequest) -> OrderOut:
    tenant = settings().tenant_id
    digest = request_fingerprint(request, user_id)
    existing = db.scalar(select(Order).where(Order.tenant_id == tenant, Order.idempotency_key == request.idempotency_key))
    if existing:
        if existing.customer_user_id != user_id or existing.request_hash != digest:
            raise HTTPException(status_code=409, detail="Idempotency key already used for a different order")
        return OrderOut(order_id=existing.id, status=existing.status, currency=existing.currency, total_minor=existing.total_minor)
    if len({item.product_id for item in request.items}) != len(request.items):
        raise HTTPException(status_code=422, detail="Duplicate product lines must be combined")
    result = quote(db, request)
    if not result.can_checkout:
        raise HTTPException(status_code=409, detail="Supplier stock unavailable or stale")
    order = Order(tenant_id=tenant, customer_user_id=user_id, status="pending_payment",
                  currency=result.currency, total_minor=result.subtotal_minor,
                  idempotency_key=request.idempotency_key, request_hash=digest)
    db.add(order)
    db.flush()
    for line in result.lines:
        db.add(OrderItem(tenant_id=tenant, order_id=order.id, product_id=UUID(line.product_id),
                         quantity=line.quantity, unit_price_minor=line.price_minor, currency=result.currency))
    correlation = str(uuid4())
    db.add(AuditEvent(tenant_id=tenant, actor_type="customer", action="order.created",
                      resource_type="order", resource_id=str(order.id), correlation_id=correlation,
                      details={"status": "pending_payment"}))
    db.add(OutboxEvent(tenant_id=tenant, event_type="order.created", aggregate_id=str(order.id),
                       correlation_id=correlation, payload={"status":"pending_payment"}))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        concurrent = db.scalar(select(Order).where(Order.tenant_id == tenant, Order.idempotency_key == request.idempotency_key))
        if concurrent and concurrent.customer_user_id == user_id and concurrent.request_hash == digest:
            return OrderOut(order_id=concurrent.id, status=concurrent.status, currency=concurrent.currency, total_minor=concurrent.total_minor)
        raise HTTPException(status_code=409, detail="Order conflict")
    return OrderOut(order_id=order.id, status=order.status, currency=order.currency, total_minor=order.total_minor)

def owned_order(db: Session, order_id: UUID, user_id: UUID) -> OrderOut:
    order = db.scalar(select(Order).where(Order.id == order_id, Order.tenant_id == settings().tenant_id, Order.customer_user_id == user_id))
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderOut(order_id=order.id, status=order.status, currency=order.currency, total_minor=order.total_minor)

def owned_orders(db: Session, user_id: UUID) -> list[OrderOut]:
    """Only return the authenticated customer's orders for the active tenant."""
    rows = db.scalars(select(Order).where(
        Order.tenant_id == settings().tenant_id, Order.customer_user_id == user_id
    ).order_by(Order.created_at.desc()).limit(100)).all()
    return [OrderOut(order_id=o.id, status=o.status, currency=o.currency,
                     total_minor=o.total_minor) for o in rows]
