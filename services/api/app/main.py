"""AACP local prototype: read-only product catalog and deterministic assistant.

Not a checkout, payment processing, or fulfillment implementation.
"""
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ENV = os.getenv("AACP_ENV", "development")
DEMO = os.getenv("AACP_DEMO_MODE", "true").lower() == "true"
if ENV == "production" and DEMO:
    raise RuntimeError("Demo mode is prohibited in production")
app = FastAPI(title="AACP API", version="0.1.0", description="Read-only development prototype")
origins = [s.strip() for s in os.getenv("AACP_ALLOWED_ORIGINS", "http://localhost:3000").split(",") if s.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

class Product(BaseModel):
    id: str
    name: str
    category: str
    price_minor: int = Field(ge=0)
    currency: str
    description: str
    in_stock: bool
    emoji: str

class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)

class AssistantResponse(BaseModel):
    reply: str
    mode: str = "deterministic-demo"
    suggested_product_ids: list[str]

CATALOG = [
    Product(id="demo-headphones", name="Studio Wireless Headphones", category="Audio", price_minor=285000, currency="BDT", description="Comfortable over-ear listening with a clean minimalist design.", in_stock=True, emoji="🎧"),
    Product(id="demo-bag", name="Everyday Travel Backpack", category="Lifestyle", price_minor=420000, currency="BDT", description="Spacious, organized everyday carry for work and travel.", in_stock=True, emoji="🎒"),
    Product(id="demo-lamp", name="Ambient Desk Light", category="Home", price_minor=195000, currency="BDT", description="Soft desk lighting for a comfortable creative workspace.", in_stock=True, emoji="💡"),
    Product(id="demo-watch", name="Minimal Smart Watch", category="Tech", price_minor=620000, currency="BDT", description="Modern wearable style with everyday utility.", in_stock=True, emoji="⌚"),
]

@app.get("/health")
def health():
    return {"status": "ok", "environment": ENV, "demo": DEMO}

@app.get("/api/v1/products", response_model=list[Product])
def products(search: str = "", category: str = ""):
    if not DEMO:
        raise HTTPException(status_code=503, detail="Live catalog repository has not been configured")
    return [p for p in CATALOG if (not search or search.lower() in (p.name + " " + p.description).lower()) and (not category or p.category.lower() == category.lower())]

@app.get("/api/v1/products/{product_id}", response_model=Product)
def product(product_id: str):
    if not DEMO:
        raise HTTPException(status_code=503, detail="Live catalog repository has not been configured")
    for p in CATALOG:
        if p.id == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

@app.post("/api/v1/assistant/demo", response_model=AssistantResponse)
def assistant(request: AssistantRequest):
    if not DEMO:
        raise HTTPException(status_code=404, detail="Demo assistant disabled")
    q = request.question.lower()
    matches = [p for p in CATALOG if any(word in (p.name + " " + p.category).lower() for word in q.split() if len(word) > 3)]
    selected = matches[:2] if matches else CATALOG[:2]
    names = ", ".join(p.name for p in selected)
    return AssistantResponse(reply=f"This is a preview assistant, not a live AI agent. Based on our sample catalog, you might explore: {names}. Product availability and delivery are not verified.", suggested_product_ids=[p.id for p in selected])
