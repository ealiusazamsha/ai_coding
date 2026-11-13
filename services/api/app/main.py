"""AACP API. No live checkout, supplier purchases or gateway callbacks until approved integrations."""
from uuid import UUID
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .config import settings
from .realtime import router as realtime_router
from .admin import router as admin_router
from .support import router as support_router
from .database import get_db
from .security import current_user
from .demo import PRODUCTS
from .commerce import listing, quote, create_pending_order, owned_order, owned_orders
from .schemas import ProductOut, QuoteRequest, QuoteResponse, OrderRequest, OrderOut, AssistantRequest, AssistantResponse

config = settings()
app = FastAPI(title="AACP Commerce API", version="0.2.0", description="Python-native commerce foundation; live checkout disabled")
app.include_router(realtime_router)
app.include_router(admin_router)
app.include_router(support_router)
app.add_middleware(CORSMiddleware,
                   allow_origins=[s.strip() for s in __import__("os").getenv("AACP_ALLOWED_ORIGINS", "http://localhost:3000").split(",") if s.strip()],
                   allow_methods=["GET","POST"], allow_headers=["Authorization","Content-Type","Idempotency-Key"])

def optional_catalog_db():
    if config.demo_mode:
        yield None
    else:
        yield from get_db()

@app.get("/health")
def health():
    return {"status":"ok","environment":config.environment,"demo":config.demo_mode}

@app.get("/ready")
def ready():
    if not config.database_url:
        raise HTTPException(status_code=503, detail="Dedicated Supabase database connection is not configured")
    from sqlalchemy import text
    from .database import engine
    try:
        with engine().connect() as connection:
            connection.execute(text("select 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {"status":"ready"}

@app.get("/api/v1/capabilities")
def capabilities():
    return {"catalog_mode":"demo" if config.demo_mode else "database",
            "live_checkout":False,"supplier_procurement":False,"payment_gateway":False,
            "assistant_mode":"deterministic-demo" if config.demo_mode else "not-configured"}

@app.get("/api/v1/products", response_model=list[ProductOut])
def products(search: str = Query(default="", max_length=120), category: str = Query(default="", max_length=80),
             db: Session | None = Depends(optional_catalog_db)):
    if config.demo_mode:
        return [p for p in PRODUCTS if (not search or search.lower() in (p.name+" "+p.description).lower())
                and (not category or p.category.lower()==category.lower())]
    return listing(db, search, category)

@app.get("/api/v1/products/{product_id}", response_model=ProductOut)
def product(product_id: str, db: Session | None = Depends(optional_catalog_db)):
    if config.demo_mode:
        item = next((p for p in PRODUCTS if p.id == product_id), None)
    else:
        item = next((p for p in listing(db) if p.id == product_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Product not found")
    return item

@app.post("/api/v1/quotes", response_model=QuoteResponse)
def quote_cart(request: QuoteRequest, db: Session | None = Depends(optional_catalog_db)):
    if config.demo_mode:
        raise HTTPException(status_code=503, detail="Demo products have no verified supplier stock")
    return quote(db, request)

@app.get("/api/v1/orders", response_model=list[OrderOut])
def list_orders(user: UUID = Depends(current_user), db: Session = Depends(get_db)):
    if config.demo_mode:
        raise HTTPException(status_code=503, detail="Orders disabled in demo mode")
    return owned_orders(db, user)


@app.post("/api/v1/orders", response_model=OrderOut, status_code=201)
def create_order(request: OrderRequest, user: UUID = Depends(current_user),
                 db: Session = Depends(get_db)):
    if config.demo_mode:
        raise HTTPException(status_code=503, detail="Order creation disabled in demo mode")
    return create_pending_order(db, user, request)

@app.get("/api/v1/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: UUID, user: UUID = Depends(current_user),
              db: Session = Depends(get_db)):
    if config.demo_mode:
        raise HTTPException(status_code=503, detail="Orders disabled in demo mode")
    return owned_order(db, order_id, user)

@app.post("/api/v1/checkout", status_code=503)
def checkout_disabled():
    raise HTTPException(status_code=503, detail="Checkout disabled until verified payment provider is configured")

@app.post("/api/v1/assistant/demo", response_model=AssistantResponse)
def assistant(request: AssistantRequest):
    if not config.demo_mode:
        raise HTTPException(status_code=404, detail="Demo assistant disabled")
    terms = [w for w in request.question.lower().split() if len(w)>3]
    matching = [p for p in PRODUCTS if any(t in (p.name+" "+p.category).lower() for t in terms)]
    selected = (matching or PRODUCTS)[:2]
    names = ", ".join(p.name for p in selected)
    return AssistantResponse(reply=f"Preview assistant (not live AI): Based on the sample catalog, explore {names}. Stock, delivery and purchase eligibility are not verified.",
                             suggested_product_ids=[p.id for p in selected])
