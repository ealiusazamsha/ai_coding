-- Customer-owned support tickets, private aacp schema.
-- Apply only to the AACP Commerce project after migration 202611140002.
create table if not exists aacp.support_cases (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references aacp.tenants(id),
  customer_user_id uuid not null,
  subject text not null check (char_length(subject) between 4 and 160),
  message text not null check (char_length(message) between 10 and 3000),
  status text not null default 'open'
    check (status in ('open','reviewing','resolved')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists aacp_support_customer_idx
  on aacp.support_cases(tenant_id,customer_user_id,created_at desc);
create index if not exists aacp_support_open_idx
  on aacp.support_cases(tenant_id,status,updated_at desc);
alter table aacp.support_cases enable row level security;
revoke all on aacp.support_cases from public, anon, authenticated;
