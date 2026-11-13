-- Apply to a fresh, dedicated AACP Supabase project AFTER 202611130001_aacp_core.sql
-- Extend product and order metadata needed by Python API; no production checkout is enabled.
alter table aacp.products add column if not exists sale_price_minor bigint not null default 0 check(sale_price_minor >= 0);
alter table aacp.products add column if not exists currency char(3) not null default 'BDT';
alter table aacp.products add column if not exists media_path text;
alter table aacp.orders add column if not exists request_hash varchar(64) not null default '';
create index if not exists aacp_products_tenant_status_idx on aacp.products(tenant_id, status);
create index if not exists aacp_supplier_offers_freshness_idx on aacp.supplier_offers(tenant_id, product_id, synced_at desc);
create index if not exists aacp_orders_customer_idx on aacp.orders(tenant_id, customer_user_id, created_at desc);
create index if not exists aacp_outbox_unprocessed_idx on aacp.outbox_events(created_at) where processed_at is null;

-- Cross-tenant foreign-key constraints, preventing mismatched supplier/product/order references.
alter table aacp.suppliers add constraint aacp_suppliers_tenant_id_unique unique (tenant_id,id);
alter table aacp.products add constraint aacp_products_tenant_id_unique unique (tenant_id,id);
alter table aacp.orders add constraint aacp_orders_tenant_id_unique unique (tenant_id,id);
alter table aacp.supplier_offers add constraint aacp_offers_supplier_tenant_fk foreign key (tenant_id,supplier_id) references aacp.suppliers(tenant_id,id);
alter table aacp.supplier_offers add constraint aacp_offers_product_tenant_fk foreign key (tenant_id,product_id) references aacp.products(tenant_id,id);
alter table aacp.order_items add constraint aacp_items_order_tenant_fk foreign key (tenant_id,order_id) references aacp.orders(tenant_id,id);
alter table aacp.order_items add constraint aacp_items_product_tenant_fk foreign key (tenant_id,product_id) references aacp.products(tenant_id,id);
alter table aacp.payments add constraint aacp_payments_order_tenant_fk foreign key (tenant_id,order_id) references aacp.orders(tenant_id,id);
alter table aacp.supplier_purchase_orders add constraint aacp_po_order_tenant_fk foreign key (tenant_id,order_id) references aacp.orders(tenant_id,id);
alter table aacp.supplier_purchase_orders add constraint aacp_po_supplier_tenant_fk foreign key (tenant_id,supplier_id) references aacp.suppliers(tenant_id,id);
