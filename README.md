# Autonomous Agentic Commerce Platform (AACP)

> **Status:** Implementation foundation / pre-production. This repository is not a production-ready fully autonomous store.

AACP is a Bangladesh-first, internationally extensible, supplier-fulfilled commerce system. A deterministic transactional core handles catalog, orders, inventory, payment confirmation and fulfillment; bounded AI agents assist customers and coordinate authorized operations.

## Documentation
- [Product Requirements (PRD)](docs/requirements/PRD.md)
- [Software Requirements (SRS)](docs/requirements/SRS.md)
- [Architecture](docs/architecture/OVERVIEW.md)
- [Media and assets](docs/MEDIA-GUIDE.md)
- [MVP delivery plan](docs/planning/MVP-PLAN.md)
- [Security model](docs/security/SECURITY.md)

## Monorepo layout
- `apps/storefront` — Next.js storefront, cart and AI-assistant interface
- `services/api` — FastAPI commerce endpoints and payments boundary
- `services/agents` — typed agent policies and deterministic MVP assistant
- `packages/contracts` — cross-service API schemas and payload examples
- `integrations/suppliers` — supplier adapter specification and fixtures
- `assets` — controlled source media (never customer personal data)
- `infra` — Docker Compose and deployment examples
- `docs` — requirements, architecture, operations and backlog
- `.github/workflows` — continuous integration

## Local quick start
```bash
cp .env.example .env
docker compose up --build
```
Storefront: http://localhost:3000 · API docs: http://localhost:8000/docs

The demo provides sample catalog data, checkout order creation and a **sandbox-only** payment event flow. No real payment capture or supplier purchase is enabled. Do not deploy the demo configuration to production.

## Initial scope
AACP v0.1 includes a working integration foundation and a simulated supplier. Real payment gateways, authenticated checkout, real supplier APIs, production-grade fulfillment, third-party messaging and multi-tenant SaaS provisioning remain planned milestones. See [MVP plan](docs/planning/MVP-PLAN.md) and [known gaps](docs/KNOWN-GAPS.md).

## Development
```bash
cd services/api
python -m pip install -r requirements-dev.txt
pytest
```

Use environment variables and managed secrets; never commit live credentials, personal information, or payment card data.

## Ownership
Project maintained by repository owner. No open-source license has been granted by inclusion in this public repository.
