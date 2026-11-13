"""SQLite verifies customer ownership is tenant-scoped for support cases."""
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
import pytest

from app.config import DEMO_TENANT
from app.models import Base, SupportCase, Tenant
from app.support import CaseCreate, CaseStatus, owned_case


def test_case_contract_rejects_invalid_state_and_short_message():
    with pytest.raises(Exception):
        CaseStatus(status="purchased")
    with pytest.raises(Exception):
        CaseCreate(subject="Hi", message="short")


def test_support_cases_are_owner_scoped():
    engine = create_engine("sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        execution_options={"schema_translate_map": {"aacp": None}})
    Base.metadata.create_all(engine)
    alice, bob = uuid4(), uuid4()
    with Session(engine, expire_on_commit=False) as db:
        db.add(Tenant(id=DEMO_TENANT, name="Test tenant"))
        ticket = SupportCase(tenant_id=DEMO_TENANT, customer_user_id=alice,
                             subject="Delivery question", message="Where can I see the delivery window?",
                             status="open")
        db.add(ticket)
        db.commit()
        assert owned_case(db, ticket.id, alice).id == ticket.id
        with pytest.raises(HTTPException) as exc:
            owned_case(db, ticket.id, bob)
        assert exc.value.status_code == 404
