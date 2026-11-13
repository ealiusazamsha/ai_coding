# AACP — Dedicated Supabase setup and activation

## Project target and access limitation
- Project reference: `bborikhazomedjzihyiv`
- Public API URL: https://bborikhazomedjzihyiv.supabase.co
- Organization: **AACP Commerce**, Free tier
- Region observed in dashboard: **Tokyo** (`ap-northeast-1`)
- Browser dashboard: https://supabase.com/dashboard/project/bborikhazomedjzihyiv
- GitHub: https://github.com/ealiusazamsha/ai_coding

The browser dashboard was verified healthy, but **this conversation does not currently have an authorized Supabase database connector**. The connector reports `link_id must identify an eligible linked account`. No SQL migration, tenant provisioning or cloud database integration has been executed here. **Never apply these migrations to the existing CareerFlow or Global Job Agent database.**

## 1. Deploy reviewed migrations to the dedicated AACP database
In the AACP project's **SQL Editor**, apply each file in order, exactly once, after reviewing it. Read SQL files directly from the GitHub repository's `supabase/migrations/` directory:

1. `202611130001_aacp_core.sql` — tenants, suppliers, catalog, orders, payments, audit, outbox; private schema and RLS.
2. `202611140001_aacp_commerce_extensions.sql` — prices, indexes, composite foreign keys.
3. `202611140002_aacp_supplier_provenance.sql` — manually entered stock is not verified.
4. `202611140003_aacp_support_cases.sql` — customer-owned support requests.

The original extension migration adds foreign-key constraints without `IF NOT EXISTS`. Do not rerun it blindly; review the database's migration history before a retry.

**Read-only verification query:**

```sql
select schemaname, tablename, rowsecurity
from pg_tables
where schemaname = 'aacp'
order by tablename;

select
 has_schema_privilege('anon', 'aacp', 'USAGE') as anon_has_aacp_usage,
 has_schema_privilege('authenticated', 'aacp', 'USAGE') as authenticated_has_aacp_usage;
```

Expected: all AACP tables have row security enabled; both schema usage checks return false. Confirm the `source_verified` column exists on `aacp.supplier_offers`. Run the Supabase security advisor and review findings.

## 2. Provision a merchant tenant
**Only after migrations succeed**, execute in the same AACP project's SQL Editor:

```sql
insert into aacp.tenants(name, status)
values ('AACP Commerce', 'active')
returning id;
```

Record the returned tenant UUID privately. Do not re-run the INSERT unless you deliberately want another tenant.

## 3. Configure an operator identity
Create or identify an authorized adult operator account under the target project's Supabase Authentication → Users. Use the verified `auth.users.id` UUID for that user, **not an email or unverified JWT claim**, in `AACP_OPERATOR_USER_IDS`. The dashboard itself does not create an operator; the backend relies on this explicit allowlist.

Use only the **publishable** Supabase API key in browser settings. Never expose `service_role` / secret keys, database credentials or card data.

## 4. Set local Docker environment
Copy `services/api/.env.example` to `services/api/.env` (gitignored). Set the following values to their actual **private** configuration:

```dotenv
AACP_ENV=development
SUPABASE_URL=https://bborikhazomedjzihyiv.supabase.co
SUPABASE_PUBLISHABLE_KEY=YOUR_SUPABASE_PUBLISHABLE_KEY
DATABASE_URL=postgresql+psycopg://YOUR_USER:YOUR_PASSWORD@THE_ACTUAL_HOST:5432/postgres?sslmode=require
AACP_DEFAULT_TENANT_ID=UUID_RETURNED_FROM_SQL
AACP_OPERATOR_USER_IDS=YOUR_SUPABASE_AUTH_USER_UUID
```

**Do not copy the above placeholders as if they were working connection credentials.** From the AACP project's **Connect** panel, copy the correct PostgreSQL connection hostname and pooler mode (session pooler is often appropriate for Windows networks without IPv6 direct access). SQLAlchemy uses the `postgresql+psycopg://` dialect; ensure TLS/hostname verification according to the connection method.

Copy `infra/.env.example` to `infra/.env` (gitignored) and set:

```dotenv
AACP_API_HOST_PORT=8001
AACP_WEB_HOST_PORT=3000
AACP_PUBLIC_API_URL=http://localhost:8001
AACP_PUBLIC_WS_URL=ws://localhost:8001/ws/v1/demo
AACP_ALLOWED_ORIGINS=http://localhost:3000
AACP_DEMO_MODE=false
AACP_SUPABASE_PUBLIC_URL=https://bborikhazomedjzihyiv.supabase.co
AACP_SUPABASE_PUBLIC_KEY=YOUR_SUPABASE_PUBLISHABLE_KEY
```

`AACP_DEMO_MODE=false` in `infra/.env` overrides the backend image's safe demo default. `infra/docker-compose.yml` reads `services/api/.env` as an optional backend-only environment file. Frontend public values are **built into** the Next.js image; rebuild it when changing API/WS/URL/publishable-key values. The publishable key is public; the database URL and credentials must remain backend-only.

Restart:

```powershell
docker compose -f infra/docker-compose.yml up --build -d
docker compose -f infra/docker-compose.yml ps
Invoke-RestMethod http://localhost:8001/health
Invoke-RestMethod http://localhost:8001/ready
```

`/ready` checks only basic database connectivity, not migration completeness. Verify tables and permissions separately. In database mode:
- `/api/v1/products` reads tenant-scoped published products (stock shows true only for verified fresh supplier offers).
- `/operations` provides Supabase Auth sign-in for allowlisted merchant operators, supplier/product/offers and support queues.
- `/account` provides existing Supabase Auth customers their own order history and support cases.

**Note:** the demo WebSocket `/ws/v1/demo` is intentionally disabled in database mode; its connected indicator therefore changes to offline. A production/authenticated WebSocket event channel is a separate implementation prerequisite, not an error with SQL.

## 5. Integration safety
- Never run database mutations on the unrelated Global Job Agent/CareerFlow project.
- Customer-to-customer access and tenant boundaries are enforced at the Python API level and private-schema permissions; still validate with real Postgres integration tests.
- Operator approval of a supplier does **not** validate manually entered stock. The supplier provenance flag defaults false and cannot be set by the admin API.
- Payments, callbacks, supplier purchase orders and automatic refunds are **not live**. Do not infer real transactions from HTTP demo modes or synthetic test cases.
- Credentials must not be shared in chat, source, browser public variables, or diagnostic logs.

Official docs: https://supabase.com/docs/guides/database/connecting-to-postgres
