"""Backend-only database access; Supabase URL never reaches a browser."""
from functools import lru_cache
from typing import Generator
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .config import settings

@lru_cache(maxsize=1)
def engine():
    config = settings()
    if not config.database_url:
        return None
    return create_engine(config.database_url, pool_pre_ping=True)

def get_db() -> Generator[Session, None, None]:
    bind = engine()
    if bind is None:
        raise HTTPException(status_code=503, detail="Database not configured; commerce operations unavailable")
    with Session(bind) as session:
        yield session
