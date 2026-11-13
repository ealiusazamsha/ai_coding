# Supabase Cloud connection for AACP

## Selected project (provided by user, awaiting access)
- Public API URL: `https://bborikhazomedjzihyiv.supabase.co`
- Project reference: `bborikhazomedjzihyiv`
- Project dashboard: https://supabase.com/dashboard/project/bborikhazomedjzihyiv
- Status (2026-11-14): **not accessible through the currently connected Supabase integration**. Project details and ownership are therefore not yet verified. Supabase returned a permission-denied error when attempting project lookup. **No migrations have been applied.**

The currently connected account can see only the `Global Job Agent` organization and its existing CareerFlow/job_agent database. Do not migrate AACP tables into that other project.

## Grant appropriate connector access
1. Sign in to Supabase in your browser and ensure the target project is accessible in the dashboard: https://supabase.com/dashboard/project/bborikhazomedjzihyiv.
2. In ChatGPT **Settings → Plugins**, open the Supabase connection and reconnect or authorize the account that belongs to the target project's organization, granting project access as appropriate.
3. If the project is owned by a different Supabase user, authorize the correct account or invite the connected account with the necessary access.
4. Retry `list_projects` and `get_project` to validate that the target is available before making any database changes.
5. Do not send Supabase database passwords, service-role keys, access tokens or payment credentials through chat or GitHub source control.

## Apply migrations after authorization
1. Verify target project name, organization, region and database health.
2. Ensure it is a **dedicated AACP project** with no unrelated production application data.
3. Inspect existing tables/schemas and migration history to avoid collisions.
4. Apply in order:
   - `supabase/migrations/202611130001_aacp_core.sql`
   - `supabase/migrations/202611140001_aacp_commerce_extensions.sql`
5. Verify `aacp` schema and tables, RLS, grants, indexes, foreign keys, and Supabase security advisors.
6. Create one AACP tenant and securely configure its UUID as `AACP_DEFAULT_TENANT_ID` in the backend.
7. Obtain the real `DATABASE_URL` from the project's **Connect** dialog. Use `postgresql+psycopg` format for SQLAlchemy with SSL. Do not guess a pooler host, username or password.
8. Set `SUPABASE_URL=https://bborikhazomedjzihyiv.supabase.co`, `SUPABASE_PUBLISHABLE_KEY`, `AACP_DEFAULT_TENANT_ID`, and `DATABASE_URL` via backend secret configuration.
9. Validate GET `/ready` and database-backed API queries using an approved staging environment.
10. Keep payments, supplier procurement and real AI tool execution disabled until their separate security and integration acceptance tests pass.

## Isolation and security
The `aacp` schema is intended to be private; currently no anonymous/authenticated Data API permissions should be granted. RLS is defense in depth, not a substitute for authorized service roles and tenant-aware business logic. Never expose privileged Supabase keys in `NEXT_PUBLIC_*` environment variables.

## Connection modes
For a persistent FastAPI deployment, use a direct or session-pooler connection as supported by the deployment network; for serverless choose a supported transaction pooler with appropriate driver configuration. Store credentials in a secret manager and enable appropriate certificate verification.

Official documentation: https://supabase.com/docs/guides/database/connecting-to-postgres and https://supabase.com/docs/guides/database/secure-data
