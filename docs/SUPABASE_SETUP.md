# Supabase Cloud connection

## Current state
One connected organization appears as **Global Job Agent**. The available Supabase project hosts existing CareerFlow / job_agent tables. AACP migrations have **not** been applied to it.

A new independent project requires explicit organization selection and any applicable cost approval before provisioning. The current quoted project charge was $0/month, but billing/usage may change.

## Recommended approach
1. Select the Supabase organization, region, and appropriate merchant-data residency.
2. Provision new project `aacp-commerce`. Do not reuse existing CareerFlow database.
3. In the new project's SQL editor or migration tooling apply the migration files in chronological order.
4. Create a tenant row in `aacp.tenants` and configure its UUID as `AACP_DEFAULT_TENANT_ID` on the backend (never from untrusted request input).
5. Import only approved supplier offers with legitimate stock timestamps, approved supplier records, and active products.
6. Copy the actual **connection URL** from the new project's Connect dialog. Use `postgresql+psycopg://...` for SQLAlchemy, with SSL enforced; do not guess pooler hostnames.
7. Set backend secrets `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` via secret management; frontend needs only `NEXT_PUBLIC_API_BASE_URL`.
8. Keep schema `aacp` out of Data API exposure until scoped policies and explicit grants have been reviewed. RLS enabled for all tables; currently no anonymous/authenticated access.
9. Verify via GET /ready and trusted SQL queries; inspect Supabase advisors and test backups/restores.
10. Activate payment and supplier adapters only after testing idempotency and callbacks.

## Connection modes
Persistent FastAPI services: direct or session pooler, depending on IPv6 availability. Stateless/serverless: carefully configured transaction pooler. Supabase direct server credentials must not be included in browser assets or GitHub commits. Authentication is verified against Supabase Auth's /auth/v1/user endpoint.

Documentation: https://supabase.com/docs/guides/database/connecting-to-postgres and https://supabase.com/docs/guides/database/secure-data
