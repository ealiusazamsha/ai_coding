# Supabase Cloud connection for AACP

## Verified project identity (browser read-only view, 2026-11-14)
- **Organization:** AACP Commerce (Free); organization ID `mofxvnsmwyhparhesykz`
- **Project display name:** ealiusazamsha's Project
- **Project reference:** `bborikhazomedjzihyiv`
- **Project API URL:** https://bborikhazomedjzihyiv.supabase.co
- **Dashboard:** https://supabase.com/dashboard/project/bborikhazomedjzihyiv
- **Database region:** Tokyo, `ap-northeast-1`
- **Dashboard health indicator:** Healthy
- **GitHub integration displayed:** `ealiusazamsha/ai_coding`
- **Last migration indicator:** No migrations at time of dashboard inspection.

**Important distinction:** The dashboard is accessible to the browser session, but the Supabase plugin connected to this ChatGPT conversation is **not authorized** for organization `mofxvnsmwyhparhesykz` or the selected project. The plugin reports **You do not have permission to perform this action**, and `list_projects` only shows the unrelated Global Job Agent/CareerFlow project. Thus the AACP schema has **not been applied or verified** from this conversation. Browser tab read access does not confer database write access.

## Grant connector access for AACP
1. Open **ChatGPT → Settings → Plugins → Supabase** and reconnect/reauthorize it to the Supabase account with membership in **AACP Commerce**.
2. Ensure the OAuth/project access scope includes the specific project `bborikhazomedjzihyiv`; the browser being signed in is not sufficient.
3. Retry Supabase `list_organizations`, `list_projects`, and `get_project`. Confirm `AACP Commerce` and `bborikhazomedjzihyiv` appear **before changing any database**.
4. Do **not** send database passwords, service-role keys or access tokens through chat or GitHub source.

## Deployment sequence after authorization
1. Inspect existing schemas, tables and migration history; stop if unrelated application data is present.
2. Apply in order to this dedicated AACP project:
   - `supabase/migrations/202611130001_aacp_core.sql`
   - `supabase/migrations/202611140001_aacp_commerce_extensions.sql`
3. Check `aacp` schema tables, tenant-scoped foreign keys, RLS, grants and indexes; run Supabase security advisors.
4. Create a dedicated merchant tenant and store its UUID as `AACP_DEFAULT_TENANT_ID` on the backend; do not expose private schema to anon/authenticated.
5. Configure backend-only `DATABASE_URL`, `SUPABASE_URL=https://bborikhazomedjzihyiv.supabase.co` and `SUPABASE_PUBLISHABLE_KEY` via secret storage. Obtain actual connection URL from the dashboard's Connect dialog, never guess a host.
6. Run authenticated FastAPI staging checks, backend /ready and database-backed quote/order tests.
7. Keep real payment capture, supplier procurement and autonomous agent write tools disabled until external integrations, approvals and replay tests are complete.

## Isolation
The existing Global Job Agent/CareerFlow project is not the AACP target and must not be changed. `aacp` is a private schema with defensive RLS and no client-role grants by default. All backend queries must also enforce trusted tenant context and user ownership.

Official resources: https://supabase.com/docs/guides/database/connecting-to-postgres and https://supabase.com/docs/guides/database/secure-data
