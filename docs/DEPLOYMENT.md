# Deployment readiness and runbook

## Demonstration (no real commerce)
Build the FastAPI and Next.js containers. `docker compose -f infra/docker-compose.yml up --build` launches a demo storefront on port 3000 and API on port 8000. Do not advertise this as a live store. CI and deployment evidence are separate.

## Cloud deployment prerequisites
1. Dedicated AACP Supabase organization/project choice and permitted cost.
2. Apply both SQL migrations; verify RLS and schema isolation, and configure correct database privileges.
3. Create production tenant and configure verified Supabase Auth.
4. Deploy FastAPI behind TLS with stored secrets and strict CORS.
5. Build Next.js with public API URL matching deployment.
6. Define provider adapters and contract tests for approved payment, supplier, courier services.
7. Implement and test payment verification, settlement, fulfillment outbox processing, distributed idempotency, customer support and refunds.
8. Set media storage buckets, RLS, malware validation, license metadata and signed/private access.
9. Run end-to-end payment/supplier tests, resilience drills, security scans, observability and rollback verification.

**Current deployment blocker:** No dedicated AACP Supabase project or approved provider credentials. Live payment and supplier procurement MUST remain disabled.
