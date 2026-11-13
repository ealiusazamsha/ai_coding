# AACP Deployment and release gates

## Current verified local baseline
User verified Docker Compose healthy for Next.js on http://localhost:3000, FastAPI on http://localhost:8001, and the development WebSocket handshake. These findings relate to the preceding demo baseline; the newest merchant/customer code still needs a local rebuild and tests.

## Local development
```powershell
git pull origin main
docker compose -f infra/docker-compose.yml up --build -d
powershell -ExecutionPolicy Bypass -File scripts/verify-local.ps1
```

The demo does not require Supabase. This is **not** a production commerce deployment.

## Cloud migration and operator configuration
Read `docs/SUPABASE_SETUP.md` for four SQL migration files, project isolation, tenant setup, operator allowlist and private database credentials. Use **only** Supabase project `bborikhazomedjzihyiv`. The connected Supabase plugin in this conversation currently cannot execute SQL.

## Production prerequisites
- Verified cloud migrations, PostgreSQL tests and secure secret management.
- Hosted TLS/HTTPS, browser WSS, authenticated tenant-scoped WebSocket authorization.
- Official supplier feed and procurement API with written authorization and replay safety.
- Approved merchant-of-record/payment provider, verified webhook signatures and refunds/reconciliation.
- Bounded AI agent tool execution, support escalation, immutable audit and durable outbox consumers.
- RLS and cross-tenant isolation tests, PCI/data privacy review, restore drills and metrics.
- All CI suites green, rate limiting/abuse and dependency security scanning.

Disable live payments, supplier purchase submission and refunds until their explicit acceptance gates are fulfilled.
