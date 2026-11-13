"""Read-only, catalog-grounded shopping guidance.

This is a deterministic advisor, not an LLM or autonomous purchasing agent.
It uses only approved, published tenant-scoped catalog records and never asserts
unverified stock, delivery dates or guaranteed prices.
"""
import re
from sqlalchemy.orm import Session
from .commerce import listing
from .schemas import AssistantResponse

STOP = {"what","show","help","with","from","this","that","some","best","find",
        "want","need","have","about","please","products","items","looking"}

def catalog_answer(db: Session, question: str) -> AssistantResponse:
    words = [w.lower() for w in re.findall(r"[\w]+", question) if len(w) > 2]
    terms = [w for w in words if w not in STOP]
    products = listing(db)
    if not terms:
        matches = products[:3]
    else:
        matches = [p for p in products if any(
            term in (p.name + " " + p.description + " " + p.category).lower()
            for term in terms)][:3]
    if matches:
        names = ", ".join(p.name for p in matches)
        reply = ("Here are relevant published catalog listings: " + names
                 + ". Inventory is available only where independently verified; "
                   "checkout and delivery commitments are not activated.")
    else:
        reply = ("I could not find matching published catalog listings. "
                 "Try a product name or category. No delivery or stock guarantees are available.")
    return AssistantResponse(
        reply=reply, mode="catalog-grounded",
        suggested_product_ids=[p.id for p in matches]
    )
