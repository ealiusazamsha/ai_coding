"""The catalog advisor is deterministic and never claims a payment or shipment."""
from unittest.mock import Mock
from app.assistant import catalog_answer
from app.schemas import ProductOut

def test_grounded_answer_only_lists_catalog_matches(monkeypatch):
    import app.assistant as module
    monkeypatch.setattr(module, "listing", lambda db: [
        ProductOut(id="id-1",name="Wireless Headphones",category="Audio",price_minor=2500,currency="BDT",
                   description="Wireless listening",in_stock=False),
        ProductOut(id="id-2",name="Desk Lamp",category="Home",price_minor=1200,currency="BDT",
                   description="LED light",in_stock=False)
    ])
    answer = catalog_answer(Mock(), "Show me headphones")
    assert answer.mode == "catalog-grounded"
    assert answer.suggested_product_ids == ["id-1"]
    assert "checkout" in answer.reply.lower()
    assert "Desk Lamp" not in answer.reply

def test_unmatched_question_does_not_hallucinate():
    import app.assistant as module
    from unittest.mock import patch
    with patch.object(module, "listing", return_value=[]):
        answer = catalog_answer(Mock(), "Do you deliver a flying car tomorrow?")
    assert not answer.suggested_product_ids
    assert "No delivery" in answer.reply
