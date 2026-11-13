# AACP — Autonomous Agentic Commerce Platform

**Status: runnable local development scaffold, not a production commerce system.**

Python FastAPI + Next.js + Supabase Cloud PostgreSQL. Designed for Bangladesh and approved international dropshipping markets. The initial version deliberately uses demo-only products and never captures payment or submits real supplier orders.

## Project layout
- `docs/SRS.md`: requirements, acceptance criteria, non-functional constraints.
- `docs/PRS.md`: product scope, milestones and market decisions.
- `docs/ARCHITECTURE.md`: service and agent architecture.
- `docs/MEDIA.md`: product assets and private media policies.
- `apps/storefront/`: accessible, light-theme Next.js storefront.
- `services/api/`: Python FastAPI typed catalog API and read-only assistant.
- `supabase/migrations/`: **dedicated AACP schema** for deployment to a new Supabase project.
- `packages/contracts/`: versioned cross-service event contract.
- `packages/design-tokens/`: color, typography, spacing specification.
- `infra/`: local container instructions and configuration.
- `media/`: source asset and licensing conventions.

## Run locally
Backend (Python 3.12+):
```bash
cd services/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
pytest -q
```
Windows activation: `.venv\Scripts\Activate.ps1`.

Frontend (Node 20+):
```bash
cd apps/storefront
npm install
npm run dev
```
Open http://localhost:3000.

The backend displays harmless demo catalog items when `DATABASE_URL` is not configured; these are clearly marked as demonstration data. To use Supabase Cloud, create a **new dedicated Supabase project** (do not reuse CareerFlow/HCRE), apply the reviewed SQL migration from `supabase/migrations/`, and set `DATABASE_URL` in the backend's secret store. Never commit credentials. For persistent production deployments use a direct connection or session pooler, depending on IPv6/network support. For serverless use the documented transaction pooler settings.

## Implementation remaining before live commerce
Production auth and authorization; live supplier integration; verified payment provider; durable order workflow, transactional outbox, audit and idempotency; customer checkout; upload scanning; agent evaluation, observability and security testing. None is represented as complete.

## Safety
This publicly accessible GitHub repository must never contain database passwords, Supabase service keys, payment tokens, customer data, raw uploaded invoices or proprietary supplier media.
