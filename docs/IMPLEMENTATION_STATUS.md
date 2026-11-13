# AACP delivery and verification matrix

**Updated 2026-11-14.** Source code committed to GitHub. AACP is **not production-ready**.

| Area | Implemented in source | Verified evidence / blockers |
|---|---|---|
| UI storefront, product details, demo catalog/cart | Yes | User confirmed original localhost:3000 baseline healthy; new feature build pending |
| Python FastAPI, REST and WebSocket demo | Yes | User confirmed API healthy and demo WebSocket connected |
| Port 8001 Docker Compose config | Yes | User confirmed container health |
| AACP Cloud project identity | Yes, browser-verified | Healthy Tokyo region, Free organization |
| Cloud database migrations | Four versioned SQL files | **Not executed or tested on Supabase**; connector access unavailable |
| Tenant-specific product and offer listing | Yes | Backend code; cloud integration pending |
| Supplier registration, approval, manual offers | Yes | Backend + protected operations UI; requires DB mode |
| Verified stock provenance | Yes | Manual offers cannot authorize stock; real supplier adapter pending |
| Backend auth via Supabase Auth /user | Yes | Live auth integration pending |
| Merchant access allowlist | Yes | Requires operator UUID and backend env |
| Customer-owned orders | Yes | SQLite/local tests pending new code validation |
| Customer support cases | Yes | Backend, account page and merchant support queue; cloud integration pending |
| Merchant support queue and audit/outbox records | Yes | Database and UI integration tests pending |
| AI agent orchestration | No | Deterministic demo and grounded catalog advisor only; no external model/tool execution |
| Payment gateway, verified callbacks and refunds | No | Requires merchant approval and provider selection |
| Supplier order submission and courier integration | No | Requires approved suppliers/contracts/credentials |
| Durable outbox dispatch, retries and notification delivery | No | Only transactional outbox persistence model |
| Production multi-instance WebSocket event fanout | No | Authenticated on-demand customer status snapshots added; durable event push not built |
| Multitenant SaaS billing and subscriptions | No | Schema isolation groundwork only |
| CI workflow execution | Configured but **failing** | GitHub job details unavailable; isolated Docker pytest build stage added but unverified |
| Production release | No | Requires end-to-end tests, security/compliance and external integrations |

## Local verification commands
```powershell
git pull origin main
docker compose -f infra/docker-compose.yml up --build -d
docker compose -f infra/docker-compose.yml ps
powershell -ExecutionPolicy Bypass -File scripts/verify-local.ps1
```

During demo mode, /operations and /account intentionally explain that cloud mode is not active. In live database mode the demo WebSocket will be disabled for security. Do not switch to non-demo until migrations and proper backend/private environment are configured.

## Strict completion gates
1. Re-authorize Supabase plugin or apply reviewed migrations through the dedicated AACP project's SQL Editor, then verify RLS/tenant isolation and full PostgreSQL integration.
2. Pass CI, Docker rebuild, Python tests and storefront builds.
3. Configure and test verified supplier API feeds, region compliance and merchant stock policy.
4. Integrate an eligible payment provider with signed webhooks, settlement and reconciliation tests. Do not enable checkout before this.
5. Build a durable outbox consumer with delivery acknowledgement, retry and dead-letter handling.
6. Implement authenticated WebSocket event authorization and fanout across API instances.
7. Implement real policy-scoped AI agents, monitoring, human approvals, abuse controls and incident shutdown.
8. Complete privacy, returns/refunds, taxes/importer-of-record and production backups/restore drills.

Source delivery is useful progress, but should not be conflated with a ready-to-sell automated e-commerce business.
