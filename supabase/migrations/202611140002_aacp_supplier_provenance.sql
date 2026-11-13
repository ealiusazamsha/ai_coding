-- Apply ONLY in AACP project bborikhazomedjzihyiv, after the two prior migrations.
-- A manually entered offer is NOT a verified supplier inventory feed.
-- This prevents operator-supplied stock numbers from being treated as a stock guarantee.
alter table aacp.supplier_offers
  add column if not exists source_verified boolean not null default false;
alter table aacp.supplier_offers
  add column if not exists source_reference text;
alter table aacp.supplier_offers
  add column if not exists source_verified_at timestamptz;
create index if not exists aacp_offer_verified_idx
  on aacp.supplier_offers (tenant_id, product_id, synced_at desc)
  where source_verified = true;
-- Disable client role access even if a future environment adds broad grants.
revoke all on aacp.supplier_offers from anon, authenticated;
alter table aacp.supplier_offers enable row level security;
