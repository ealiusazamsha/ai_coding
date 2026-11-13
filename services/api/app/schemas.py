"""Validated public contracts; no client-controlled totals or tenant IDs."""
from uuid import UUID
from pydantic import BaseModel, Field

class ProductOut(BaseModel):
    id: str
    name: str
    category: str
    price_minor: int = Field(ge=0)
    currency: str
    description: str
    in_stock: bool
    emoji: str = "🛍️"
    demo: bool = False

class CartLine(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1, le=20)

class QuoteRequest(BaseModel):
    items: list[CartLine] = Field(min_length=1, max_length=30)

class QuoteLine(BaseModel):
    product_id: str
    quantity: int
    price_minor: int
    subtotal_minor: int
    available: bool
    reason: str | None = None

class QuoteResponse(BaseModel):
    currency: str
    lines: list[QuoteLine]
    subtotal_minor: int
    can_checkout: bool
    disclaimer: str

class OrderRequest(QuoteRequest):
    idempotency_key: str = Field(min_length=12, max_length=128, pattern=r"^[A-Za-z0-9_:-]+$")

class OrderOut(BaseModel):
    order_id: UUID
    status: str
    currency: str
    total_minor: int
    payment_enabled: bool = False

class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)

class AssistantResponse(BaseModel):
    reply: str
    mode: str = "deterministic-demo"
    suggested_product_ids: list[str]
