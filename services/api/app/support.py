"""Authenticated customer support; strict tenant and customer ownership checks."""
from datetime import datetime, timezone
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .admin import current_operator
from .config import DEMO_TENANT, settings
from .database import get_db
from .models import AuditEvent, OutboxEvent, SupportCase
from .security import current_user

router = APIRouter(prefix="/api/v1/support", tags=["customer-support"])


def require_database() -> None:
    config = settings()
    if config.demo_mode or not config.database_url or config.tenant_id == DEMO_TENANT:
        raise HTTPException(status_code=503, detail="Customer support requires a provisioned AACP database")


class CaseCreate(BaseModel):
    subject: str = Field(min_length=4, max_length=160)
    message: str = Field(min_length=10, max_length=3000)


class CaseStatus(BaseModel):
    status: str = Field(pattern="^(open|reviewing|resolved)$")


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    subject: str
    message: str
    status: str
    created_at: datetime
    updated_at: datetime


def owned_case(db: Session, case_id: UUID, user_id: UUID) -> SupportCase:
    row = db.scalar(select(SupportCase).where(
        SupportCase.id == case_id,
        SupportCase.tenant_id == settings().tenant_id,
        SupportCase.customer_user_id == user_id,
    ))
    if row is None:
        raise HTTPException(status_code=404, detail="Support case not found")
    return row


def audit(db: Session, user_id: UUID, event: str, case_id: UUID) -> None:
    correlation = str(uuid4())
    tenant = settings().tenant_id
    db.add(AuditEvent(tenant_id=tenant, actor_type="user", action=event,
                      resource_type="support_case", resource_id=str(case_id),
                      correlation_id=correlation,
                      details={"actor_user_id": str(user_id)}))
    # Only event metadata enters the outbox; never include customer message content.
    db.add(OutboxEvent(tenant_id=tenant, event_type=event,
                       aggregate_id=str(case_id), correlation_id=correlation,
                       payload={"resource_type": "support_case"}))


@router.get("/cases", response_model=list[CaseOut], dependencies=[Depends(require_database)])
def my_cases(user: UUID = Depends(current_user), db: Session = Depends(get_db)):
    return db.scalars(select(SupportCase).where(
        SupportCase.tenant_id == settings().tenant_id,
        SupportCase.customer_user_id == user
    ).order_by(SupportCase.created_at.desc()).limit(100)).all()


@router.post("/cases", response_model=CaseOut, status_code=201, dependencies=[Depends(require_database)])
def create_case(payload: CaseCreate, user: UUID = Depends(current_user), db: Session = Depends(get_db)):
    record = SupportCase(tenant_id=settings().tenant_id, customer_user_id=user,
                         subject=payload.subject.strip(), message=payload.message.strip(),
                         status="open")
    db.add(record)
    db.flush()
    audit(db, user, "support.case.created", record.id)
    db.commit()
    db.refresh(record)
    return record


@router.get("/cases/{case_id}", response_model=CaseOut, dependencies=[Depends(require_database)])
def my_case(case_id: UUID, user: UUID = Depends(current_user), db: Session = Depends(get_db)):
    return owned_case(db, case_id, user)


@router.get("/admin/cases", response_model=list[CaseOut], dependencies=[Depends(require_database)])
def operator_cases(_operator: UUID = Depends(current_operator),
                   limit: int = Query(default=80, ge=1, le=100),
                   db: Session = Depends(get_db)):
    return db.scalars(select(SupportCase).where(
        SupportCase.tenant_id == settings().tenant_id
    ).order_by(SupportCase.created_at.desc()).limit(limit)).all()


@router.patch("/admin/cases/{case_id}/status", response_model=CaseOut, dependencies=[Depends(require_database)])
def update_case(case_id: UUID, payload: CaseStatus, operator: UUID = Depends(current_operator),
                db: Session = Depends(get_db)):
    row = db.scalar(select(SupportCase).where(
        SupportCase.id == case_id,
        SupportCase.tenant_id == settings().tenant_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Support case not found")
    if row.status != payload.status:
        row.status = payload.status
        row.updated_at = datetime.now(timezone.utc)
        audit(db, operator, "support.case.status_changed", row.id)
        db.commit()
        db.refresh(row)
    return row
