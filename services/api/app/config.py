"""Typed runtime configuration. No credentials are stored in source control."""
import os
from dataclasses import dataclass
from uuid import UUID

DEMO_TENANT = UUID("00000000-0000-0000-0000-000000000001")

@dataclass(frozen=True)
class Settings:
    environment: str
    demo_mode: bool
    database_url: str | None
    tenant_id: UUID
    supabase_url: str
    supabase_publishable_key: str

def settings() -> Settings:
    environment = os.getenv("AACP_ENV", "development").lower()
    demo_mode = os.getenv("AACP_DEMO_MODE", "true").lower() == "true"
    database_url = os.getenv("DATABASE_URL")
    tenant_id = UUID(os.getenv("AACP_DEFAULT_TENANT_ID", str(DEMO_TENANT)))
    result = Settings(environment, demo_mode, database_url, tenant_id,
                      os.getenv("SUPABASE_URL", "").rstrip("/"),
                      os.getenv("SUPABASE_PUBLISHABLE_KEY", ""))
    if environment == "production":
        if demo_mode:
            raise RuntimeError("AACP_DEMO_MODE must be false in production")
        if not database_url or not database_url.startswith(("postgresql+psycopg://", "postgresql://")):
            raise RuntimeError("Production requires a dedicated PostgreSQL DATABASE_URL")
        if tenant_id == DEMO_TENANT or not result.supabase_url or not result.supabase_publishable_key:
            raise RuntimeError("Production tenant and Supabase Auth configuration required")
    return result
