"""Pure deterministic policies that an LLM cannot override."""
from datetime import datetime, timedelta, timezone

ORDER_TRANSITIONS = {
    "pending_payment": {"confirmed", "cancelled"},
    "confirmed": {"processing", "cancelled"},
    "processing": {"partially_fulfilled", "fulfilled", "cancelled"},
    "partially_fulfilled": {"fulfilled", "cancelled"},
    "fulfilled": {"completed"},
    "completed": set(),
    "cancelled": set(),
}

def can_transition(current: str, future: str) -> bool:
    return future in ORDER_TRANSITIONS.get(current, set())

def is_fresh(synced_at: datetime, max_age_minutes: int = 15, now: datetime | None = None) -> bool:
    now = now or datetime.now(timezone.utc)
    if synced_at.tzinfo is None:
        synced_at = synced_at.replace(tzinfo=timezone.utc)
    age = now - synced_at
    return timedelta(0) <= age <= timedelta(minutes=max_age_minutes)

def offer_eligible(quantity: int, required: int, synced_at: datetime, approved: bool, cost_minor: int, selling_minor: int, min_margin_minor: int = 0) -> bool:
    return (approved and required > 0 and quantity >= required
            and cost_minor >= 0 and selling_minor >= cost_minor + min_margin_minor
            and is_fresh(synced_at))

def check_agent_tool(agent_type: str, tool_name: str) -> bool:
    tools = {
        "sales": {"search_products", "get_product", "prepare_cart"},
        "catalog": {"read_supplier_catalog", "propose_catalog_update"},
        "order": {"get_order", "get_supplier_offers", "propose_fulfillment"},
        "support": {"get_authorized_order", "create_support_case"},
        "supervisor": {"route_task", "read_agent_status"},
    }
    return tool_name in tools.get(agent_type, set())
