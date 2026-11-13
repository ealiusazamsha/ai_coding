# AACP — Autonomous Agentic Commerce Platform

**Phase: development foundation / not production ready.** Python FastAPI backend, Next.js 16 storefront, dedicated Supabase Cloud PostgreSQL database design. Scope: supplier-fulfilled commerce in Bangladesh and approved international markets, with an extensible SaaS control plane later.

## Development workflow\nCode is authored here in ChatGPT, committed to GitHub, then pulled locally and run through Docker Compose. No Codex requirement. See [Local Docker + WebSocket runbook](docs/LOCAL_DOCKER.md) and [Workflow](docs/WORKFLOW.md).\n\n## Implemented
- Responsive light-theme storefront with catalog filtering/search, preview cart and interactive **deterministic demo assistant**.
- Illustrative operations preview (no real merchant data), clear demo/production capability indicators.
- FastAPI health/readiness/capabilities, typed catalog and quote APIs, owner-scoped order read/write API.
- Supabase Auth access-token validation via trusted Auth endpoint.
- Server-derived price quotes and supplier-stock freshness/margin/approval checks.
- Idempotency-key and request fingerprint validation for creating **pending-payment** orders.
- SQLAlchemy models, business audit/outbox writes, migration for a dedicated Supabase schema, defensive tenant foreign-key constraints.
- Tests for API safety, policies and deterministic business rules; GitHub Actions for Python tests and Next.js build.

## Absolutely NOT implemented
No connected Supabase Cloud AACP project, no live payment checkout or gateway verification, no real supplier purchase order submission or fulfillment, no external LLM agent orchestration, no worker delivery system or merchant-accessible admin dashboard. The preview basket never submits orders or stores card details. The product prices and stock are illustrative.

## Project structure
```text
apps/storefront/          Next.js responsive UI and operations preview
services/api/app/         FastAPI + domain, models, auth, catalog, quotes and orders
services/api/tests/       API and policy tests
supabase/migrations/      Dedicated cloud database schema migrations
packages/contracts/      Versioned event envelope contract
packages/design-tokens/  Visual system design tokens
media/                   Source and reviewed optimized media conventions
docs/                    SRS, PRS, architecture, asset and database setup docs
infra/                   Deployment and secrets guidance
.github/workflows/        Backend and frontend checks
```

## Local Docker preview\n\n```powershell\ngit clone https://github.com/ealiusazamsha/ai_coding.git\ncd ai_coding\ndocker compose -f infra/docker-compose.yml up --build -d\n```\n\nThe browser demo WebSocket connects to `ws://localhost:8000/ws/v1/demo`; it does not represent real orders or payments.\n\n## Local development
Requirements: Python 3.12+, Node.js 22+.
```bash
cd services/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
pytest -q
```
PowerShell virtual environment activation: `.venv\\Scripts\\Activate.ps1`.
In another terminal:
```bash
cd apps/storefront
npm install
npm run dev
```
Open http://localhost:3000. With no DB configured, the demo catalog appears; there is no checkout. For production connection use environment variables below and apply migrations.

## Supabase Cloud connection
**Do not deploy to the existing CareerFlow/Global Job Agent database.** Provision a fresh Supabase project approved for AACP. Run, in order:
1. `supabase/migrations/202611130001_aacp_core.sql`
2. `supabase/migrations/202611140001_aacp_commerce_extensions.sql`

Set backend-only `DATABASE_URL`, `AACP_DEFAULT_TENANT_ID`, `SUPABASE_URL`, and `SUPABASE_PUBLISHABLE_KEY`. Set `AACP_DEMO_MODE=false` only after a dedicated DB and approved merchant setup exist. Never add service-role keys to browser code. Do not run migrations or seed example tenants into unrelated projects. See [Supabase setup](docs/SUPABASE_SETUP.md).

## Launch checklist
- Select initial supplier and verify real stock/purchase-order API.
- Approve legal merchant entity and payment acquiring/settlement.
- Implement real payment checkout, signed provider callbacks and reconciliation.
- Implement durable transaction outbox consumer and supplier adapter.
- Configure Supabase Auth + operator access policies and storage permissions.
- Run end-to-end integration, concurrency, security, recovery, and cost tests before any production purchase.

## Documentation
[Software requirements](docs/SRS.md) · [Product requirements](docs/PRS.md) · [Architecture](docs/ARCHITECTURE.md) · [Media](docs/MEDIA.md) · [Cloud database](docs/SUPABASE_SETUP.md).
