from datetime import datetime, timedelta, timezone
from uuid import UUID
from app.domain import is_fresh, offer_eligible, can_transition, check_agent_tool
from app.commerce import request_fingerprint
from app.schemas import OrderRequest

def test_time_and_supplier_guardrails():
    now = datetime.now(timezone.utc)
    assert is_fresh(now)
    assert not is_fresh(now - timedelta(minutes=25))
    assert not is_fresh(now + timedelta(minutes=3))
    assert offer_eligible(4,2,now,True,2000,4000)
    assert not offer_eligible(4,2,now,False,2000,4000)
    assert not offer_eligible(4,2,now,True,5000,4000)
    assert not offer_eligible(1,2,now,True,2000,4000)

def test_agent_cannot_perform_payment_actions():
    assert check_agent_tool("sales","search_products")
    assert not check_agent_tool("sales","capture_payment")
    assert not check_agent_tool("supervisor","purchase_supplier_stock")
    assert not check_agent_tool("unknown","route_task")

def test_order_state_machine():
    assert can_transition("pending_payment","confirmed")
    assert not can_transition("pending_payment","fulfilled")
    assert not can_transition("cancelled","confirmed")

def test_fingerprint_is_stable_and_bound_to_customer():
    request=OrderRequest(items=[{"product_id":"00000000-0000-0000-0000-000000000003","quantity":2}],idempotency_key="test-request-0001")
    alice=UUID("00000000-0000-0000-0000-000000000001")
    bob=UUID("00000000-0000-0000-0000-000000000002")
    assert request_fingerprint(request,alice)==request_fingerprint(request,alice)
    assert request_fingerprint(request,alice)!=request_fingerprint(request,bob)
