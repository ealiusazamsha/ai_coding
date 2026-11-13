# AACP — Autonomous Agentic Commerce Platform

**Development release | Not production-ready**

AACP is a supplier-fulfilled commerce platform, initially serving Bangladesh and approved international corridors, with future tenant-isolated SaaS capabilities.

## Technology

- **Frontend:** Next.js + React + TypeScript, responsive light-theme UI.
- **Backend:** Python 3.12 / FastAPI / SQLAlchemy, REST and WebSocket.
- **Database target:** dedicated Supabase Cloud PostgreSQL project `bborikhazomedjzihyiv` in AACP Commerce.
- **Local deployment:** Docker Compose, port `3000` storefront / `8001` API.
- **Workflow:** Build here in ChatGPT → GitHub `main` → pull locally → Docker build + test. No Codex required.

## Features in source

| Module | Implementation | Availability |
|---|---|---|
| Catalog, search, categories | Next.js and FastAPI | Demo available; database mode pending migration |
| Product details, stock labels | Next.js and direct API lookup | Stock shown only when source-verified |
| Preview cart | Client-side interactive UI | No checkout or payment |
| Demo shopping assistant | Deterministic sample catalog | Available in demo |
| Grounded database assistant | Tenant-scoped published listings | Database mode only; not an external LLM |
| Operations / merchant administration | Product drafts, publishing, supplier approval, manual offers | Authenticated operators, database mode |
| Customer account | Supabase Auth login, own order history, support cases | Database mode only |
| Merchant support queue | Case status and audit records | Database mode only |
| Order creation, idempotency | Pending-payment records with stock checks | Database mode; no payment captured |
| Demo WebSocket | Public heartbeat, no private data | Demo mode only |
| Customer WebSocket | Token authentication and owner-scoped on-demand status snapshots | Database mode; not durable push/fanout |
| Auditing and outbox | Persist events for supported writes | Dispatcher and external delivery pending |
| Supplier stock provenance | Manual offers never verified | Requires real supplier adapter for verified stock |

Do not treat **registered API routes** as proof of successful cloud integration. The user previously verified the original Docker demo as healthy; newer feature code still requires local build and tests.

## Quick start — Windows PowerShell

```powershell
git clone https://github.com/ealiusazamsha/ai_coding.git
cd ai_coding

# Isolated backend unit and SQLite integration tests
docker build --target tests --progress=plain -t aacp-api-tests ./services/api

# Run demo containers (no DB credentials needed)
docker compose -f infra/docker-compose.yml up --build -d
docker compose -f infra/docker-compose.yml ps

# HTTP smoke checks
powershell -ExecutionPolicy Bypass -File scripts/verify-local.ps1
```

Open:
- Storefront: http://localhost:3000
- API docs: http://localhost:8001/docs
- Merchant preview: http://localhost:3000/operations
- Customer preview: http://localhost:3000/account

The bottom-left indicator should show **Demo WebSocket connected** in demo mode. The browser does not use WebSocket to connect directly to PostgreSQL.

For later updates, run `git pull origin main` then rebuild. Your private `.env` files remain local and must not be committed.

## Cloud database activation

The Supabase project exists but this ChatGPT conversation **does not have an authorized database connection**, so **no migrations have been run here**. Read [Supabase setup](docs/SUPABASE_SETUP.md) before proceeding.

Apply these four migration files, **in order and only to the AACP project**:

1. `supabase/migrations/202611130001_aacp_core.sql`
2. `supabase/migrations/202611140001_aacp_commerce_extensions.sql`
3. `supabase/migrations/202611140002_aacp_supplier_provenance.sql`
4. `supabase/migrations/202611140003_aacp_support_cases.sql`

Then provision a tenant and an authenticated operator, configure backend-only PostgreSQL credentials in `services/api/.env`, configure the public publishable key in `infra/.env`, and explicitly set `AACP_DEMO_MODE=false`.

**Never migrate into the unrelated CareerFlow / Global Job Agent project.**

## Major unfinished production capabilities

- A legally eligible and approved payment provider, signed verified webhooks, actual checkout, reconciliation and refunds.
- Real supplier API integration, authorized procurement, verified stock sources and shipment/courier tracking.
- Durable event workers, email/SMS delivery, idempotent retries, dead-letter handling and multi-instance realtime fanout.
- Autonomous AI agents with real LLM integration, permissioned tools, budgets, human approvals and audit.
- Product variants, real licensed media, customer policies, tax/customs and return flows.
- Multitenant self-service SaaS subscription/billing, recovery, monitoring and production security review.

**Keep all actual payment collection, procurement and automatic refunds disabled until independently verified and approved.**

## Documentation

- [Product requirements](docs/PRS.md) · [Software requirements](docs/SRS.md)
- [Architecture](docs/ARCHITECTURE.md) · [Implementation status](docs/IMPLEMENTATION_STATUS.md)
- [Local Docker and WebSocket](docs/LOCAL_DOCKER.md) · [Local tests](docs/LOCAL_TESTING.md)
- [Supabase setup](docs/SUPABASE_SETUP.md) · [Deployment gates](docs/DEPLOYMENT.md)
