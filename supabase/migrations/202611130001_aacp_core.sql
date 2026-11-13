-- AACP foundation — apply ONLY to a dedicated AACP Supabase project.
-- Internal schema is not exposed to anon or authenticated Data API roles.
create schema if not exists aacp;
revoke all on schema aacp from public, anon, authenticated;
create extension if not exists pgcrypto;

create table if not exists aacp.tenants (
 id uuid primary key default gen_random_uuid(),
 name text not null,
 status text not null default 'active' check (status in ('active','suspended')),
 created_at timestamptz not null default now()
);
create table if not exists aacp.suppliers (
 id uuid primary key default gen_random_uuid(),
 tenant_id uuid not null references aacp.tenants(id),
 name text not null,
 integration_type text not null check (integration_type in ('api','file','manual')),
 approved boolean not null default false,
 created_at timestamptz not null default now(),
 unique(tenant_id,name)
);
create table if not exists aacp.products (
 id uuid primary key default gen_random_uuid(),
 tenant_id uuid not null references aacp.tenants(id),
 sku text not null,
 name text not null,
 description text not null default '',
 category text not null default 'General',
 status text not null default 'draft' check(status in ('draft','active','archived')),
 created_at timestamptz not null default now(),
 unique(tenant_id,sku)
);
create table if not exists aacp.supplier_offers (
 id uuid primary key default gen_random_uuid(),
 tenant_id uuid not null references aacp.tenants(id),
 supplier_id uuid not null references aacp.suppliers(id),
 product_id uuid not null references aacp.products(id),
 supplier_sku text not null,
 unit_cost_minor bigint not null check (unit_cost_minor >= 0),
 currency char(3) not null,
 quantity integer not null check(quantity >= 0),
 synced_at timestamptz not null,
 unique(tenant_id,supplier_id,supplier_sku)
);
create table if not exists aacp.orders (
 id uuid primary key default gen_random_uuid(),
 tenant_id uuid not null references aacp.tenants(id),
 customer_user_id uuid not null,
 status text not null default 'pending_payment' check (status in ('pending_payment','confirmed','processing','partially_fulfilled','fulfilled','completed','cancelled')),
 currency char(3) not null,
 total_minor bigint not null check(total_minor >= 0),
 idempotency_key text not null,
 created_at timestamptz not null default now(),
 unique(tenant_id,idempotency_key)
);
create table if not exists aacp.order_items (
 id uuid primary key default gen_random_uuid(),
 tenant_id uuid not null references aacp.tenants(id),
 order_id uuid not null references aacp.orders(id),
 product_id uuid not null references aacp.products(id),
 quantity integer not null check(quantity > 0),
 unit_price_minor bigint not null check(unit_price_minor >= 0),
 currency char(3) not null
);
create table if not exists aacp.payments (
 id uuid primary key default gen_random_uuid(),
 tenant_id uuid not null references aacp.tenants(id),
 order_id uuid not null references aacp.orders(id),
 provider text not null,
 provider_payment_id text,
 status text not null default 'initiated' check(status in ('initiated','pending','authorized','captured','failed','partially_refunded','refunded','disputed')),
 amount_minor bigint not null check(amount_minor >= 0),
 currency char(3) not null,
 created_at timestamptz not null default now(),
 unique(provider,provider_payment_id)
);
create table if not exists aacp.supplier_purchase_orders (
 id uuid primary key default gen_random_uuid(),
 tenant_id uuid not null references aacp.tenants(id),
 order_id uuid not null references aacp.orders(id),
 supplier_id uuid not null references aacp.suppliers(id),
 state text not null default 'unassigned' check(state in ('unassigned','submitting','submitted','accepted','rejected','shipped','cancelled')),
 idempotency_key text not null,
 external_ref text,
 created_at timestamptz not null default now(),
 unique(tenant_id,idempotency_key)
);
create table if not exists aacp.agent_runs (
 id uuid primary key default gen_random_uuid(),
 tenant_id uuid not null references aacp.tenants(id),
 agent_type text not null,
 status text not null,
 correlation_id text not null,
 created_at timestamptz not null default now()
);
create table if not exists aacp.audit_events (
 id uuid primary key default gen_random_uuid(),
 tenant_id uuid not null references aacp.tenants(id),
 actor_type text not null,
 action text not null,
 resource_type text not null,
 resource_id text not null,
 correlation_id text not null,
 occurred_at timestamptz not null default now(),
 details jsonb not null default '{}'::jsonb
);
create table if not exists aacp.outbox_events (
 id uuid primary key default gen_random_uuid(),
 tenant_id uuid not null references aacp.tenants(id),
 event_type text not null,
 aggregate_id text not null,
 correlation_id text not null,
 payload jsonb not null default '{}'::jsonb,
 created_at timestamptz not null default now(),
 processed_at timestamptz
);
-- Defense-in-depth: NO client role access. All service queries must also enforce tenant context.
alter table aacp.tenants enable row level security;
alter table aacp.suppliers enable row level security;
alter table aacp.products enable row level security;
alter table aacp.supplier_offers enable row level security;
alter table aacp.orders enable row level security;
alter table aacp.order_items enable row level security;
alter table aacp.payments enable row level security;
alter table aacp.supplier_purchase_orders enable row level security;
alter table aacp.agent_runs enable row level security;
alter table aacp.audit_events enable row level security;
alter table aacp.outbox_events enable row level security;
-- Future authenticated policies must use verified ownership/tenant membership;
-- do not use user_metadata as an authorization source.
