# Supabase Cloud integration

**Important:** The connected Supabase project discovered on 2026-11-13 already hosts CareerFlow/job_agent tables. It is NOT an approved AACP database and was not modified.

## New isolated project
1. Create a dedicated Supabase Cloud project named `aacp-commerce` in the intended organization and region after confirming any cost.
2. Obtain the connection string from the Supabase **Connect** dialog. Do not reconstruct a pooler hostname.
3. Apply reviewed migration in `supabase/migrations/202611130001_aacp_core.sql` using Supabase migrations/SQL editor.
4. Configure `DATABASE_URL` on the Python backend only; use SSL and a non-superuser restricted role in production.
5. Keep Supabase secret/service-role keys exclusively in backend secret management, never in `NEXT_PUBLIC_*` variables.
6. Configure Supabase Auth and verified role/ownership policies before exposing customer APIs.
7. Configure RLS and storage policies before public uploads or API exposure.
8. Validate table existence, RLS, unique constraints, migration history, connection pool capacity and backup restore.

For persistent backends use direct IPv6 or session-pooler connection; for serverless choose transaction pooler with appropriate driver configuration. See https://supabase.com/docs/guides/database/connecting-to-postgres

The demo API can run without a database, but no real transaction is possible in demo mode.
