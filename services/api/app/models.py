"""ORM mappings for the private aacp PostgreSQL schema.

For SQLite unit tests only, use schema_translate_map={'aacp': None}.
"""
from datetime import datetime, timezone
from uuid import UUID, uuid4
from sqlalchemy import BigInteger, Boolean, CheckConstraint, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class Base(DeclarativeBase):
    pass

def uid():
    return mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)

class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "aacp"}
    id: Mapped[UUID] = uid()
    name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)

class Supplier(Base):
    __tablename__ = "suppliers"
    __table_args__ = (UniqueConstraint("tenant_id", "name"), {"schema": "aacp"})
    id: Mapped[UUID] = uid()
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.tenants.id"), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    integration_type: Mapped[str] = mapped_column(String(20), nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

class Product(Base):
    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("tenant_id", "sku"), {"schema": "aacp"})
    id: Mapped[UUID] = uid()
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.tenants.id"), nullable=False)
    sku: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    category: Mapped[str] = mapped_column(Text, default="General", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    sale_price_minor: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="BDT")
    media_path: Mapped[str | None] = mapped_column(Text, nullable=True)

class SupplierOffer(Base):
    __tablename__ = "supplier_offers"
    __table_args__ = (UniqueConstraint("tenant_id", "supplier_id", "supplier_sku"), {"schema": "aacp"})
    id: Mapped[UUID] = uid()
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.tenants.id"), nullable=False)
    supplier_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.suppliers.id"), nullable=False)
    product_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.products.id"), nullable=False)
    supplier_sku: Mapped[str] = mapped_column(Text, nullable=False)
    unit_cost_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    synced_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source_reference: Mapped[str | None] = mapped_column(Text)
    source_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (UniqueConstraint("tenant_id", "idempotency_key"), {"schema": "aacp"})
    id: Mapped[UUID] = uid()
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.tenants.id"), nullable=False)
    customer_user_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    status: Mapped[str] = mapped_column(String(28), nullable=False, default="pending_payment")
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    total_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    request_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = {"schema": "aacp"}
    id: Mapped[UUID] = uid()
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.tenants.id"), nullable=False)
    order_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.orders.id"), nullable=False)
    product_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (UniqueConstraint("provider", "provider_payment_id"), {"schema": "aacp"})
    id: Mapped[UUID] = uid()
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.tenants.id"), nullable=False)
    order_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.orders.id"), nullable=False)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    provider_payment_id: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    amount_minor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)

class SupplierPurchaseOrder(Base):
    __tablename__ = "supplier_purchase_orders"
    __table_args__ = (UniqueConstraint("tenant_id", "idempotency_key"), {"schema": "aacp"})
    id: Mapped[UUID] = uid()
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.tenants.id"), nullable=False)
    order_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.orders.id"), nullable=False)
    supplier_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.suppliers.id"), nullable=False)
    state: Mapped[str] = mapped_column(String(22), nullable=False, default="unassigned")
    idempotency_key: Mapped[str] = mapped_column(String(128), nullable=False)
    external_ref: Mapped[str | None] = mapped_column(Text)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = {"schema": "aacp"}
    id: Mapped[UUID] = uid()
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.tenants.id"), nullable=False)
    actor_type: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    resource_type: Mapped[str] = mapped_column(Text, nullable=False)
    resource_id: Mapped[str] = mapped_column(Text, nullable=False)
    correlation_id: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class OutboxEvent(Base):
    __tablename__ = "outbox_events"
    __table_args__ = {"schema": "aacp"}
    id: Mapped[UUID] = uid()
    tenant_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("aacp.tenants.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    aggregate_id: Mapped[str] = mapped_column(Text, nullable=False)
    correlation_id: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
