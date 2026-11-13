# AACP — Software Requirements Specification (SRS)
Version: 1.0 | Date: 2026-11-13 | Status: engineering baseline, not approved for production

## 1. Purpose, actors and boundaries
AACP is a dropshipping / supplier-fulfilled commerce platform with a Python FastAPI backend, Next.js frontend and Supabase Cloud PostgreSQL. It initially operates a single merchant serving Bangladesh and a validated international corridor, and is designed for future tenant-isolated SaaS.

Actors: customer, merchant operator, supervisor agent, specialist agents, suppliers, couriers, payment gateways, exception reviewer, SaaS platform administrator.
Scope: catalog, shopping assistant, checkout, verified payments, supplier selection, inventory freshness, order processing, tracking, support, policy-limited agent orchestration, operations dashboard, audit. Not in initial MVP: multi-vendor marketplace, international gateway activation without legal approval, unrestricted autonomous refunds, mobile apps, self-service SaaS billing.

## 2. Functional requirements
| ID | Priority | Requirement | Verification |
|---|---|---|---|
| FR-001 | P0 | Catalog supports product variants, search and category/region filters | API + UI tests |
| FR-002 | P0 | Product page displays verified market price, current offer and stock freshness | Catalog acceptance |
| FR-003 | P0 | Agent recommends catalog items without fabricated prices, delivery or stock guarantees | Agent evaluations |
| FR-004 | P0 | Customer can create/edit cart, must consent before checkout | Checkout tests |
| FR-005 | P0 | Validate price snapshot, market, margin, stock freshness and eligibility before order | Rules tests |
| FR-006 | P0 | Order preserves immutable currency/price/supplier-cost snapshot | DB test |
| FR-007 | P0 | Payment is recognized only after trusted server-side provider verification | Forged webhook tests |
| FR-008 | P0 | Eligible paid order creates no more than one supplier PO | Replay/integration |
| FR-009 | P0 | Supplier rejection triggers policy-compliant fallback or refund/escalation | Scenario tests |
| FR-010 | P0 | Inventory feed has timestamp, expiry threshold and safety buffer | Stale feed test |
| FR-011 | P0 | Tracking updates generate retriable customer notifications | Event tests |
| FR-012 | P0 | Customers can view only their own orders and support cases | Auth tests |
| FR-013 | P0 | Every agent tool call and transaction action is logged with correlation ID | Audit tests |
| FR-014 | P0 | Human can pause procurement, agent execution or supplier adapter | Control tests |
| FR-015 | P0 | Refunds require verified transaction, policy limits and authorization | Refund tests |
| FR-016 | P0 | Events are deduplicated; durable retry and dead-letter recovery supported | Failure tests |
| FR-017 | P1 | Supplier ranking uses delivery area, costs, SLAs, reliability and availability | Routing tests |
| FR-018 | P1 | Support additional approved cross-border acquirers and logistics providers | Adapter tests |
| FR-019 | P1 | Returns, marketing and financial reconciliation automation | Business acceptance |
| FR-020 | P2 | Tenant provisioning, metering, subscriptions and branded storefronts | SaaS tests |

## 3. Quality and security
NFR-001 target 99.9% uptime once production-ready.
NFR-002 p95 internal catalog request under 500 ms excluding external API/LLM.
NFR-003 tenant, user and resource authorization for every read/write/tool operation.
NFR-004 financial minor units/NUMERIC, never float; idempotency for charges and purchasing.
NFR-005 Supabase in dedicated cloud project; backend-only privileged credentials.
NFR-006 strict row-level security on exposed tables and tenant isolation for retrieval/media/logs.
NFR-007 TLS, rotating secrets, signed webhooks, least privilege, no card data storage.
NFR-008 observability with audit, metrics, trace, alarms and cost budgets.
NFR-009 proposed RPO <=15m and RTO <=4h; tested restore needed.
NFR-010 accessibility WCAG 2.2 AA target, English/Bangla support.
NFR-011 CI tests, pin dependencies, contract/version validation and supply-chain scanning.

## 4. Lifecycle
Order: draft → pending_payment → confirmed → processing → partially_fulfilled/fulfilled → completed/cancelled.
Payment: initiated → pending/authorized → captured/failed; captured → partially_refunded/refunded/disputed.
Supplier PO: unassigned → submitting → submitted → accepted/rejected → shipped/cancelled.
Shipment: label_created → in_transit → delivered/exception/returned.
Return: requested → reviewing → approved/rejected → received → resolved.
All transitions validated and audited; orders, payments, supplier POs and shipments have independent states.

## 5. Agent responsibilities
Supervisor: classify and route. Sales: catalog-grounded help and carts. Catalog: normalize supplier data. Order: propose routing and handle bounded exceptions. Support: order information and customer inquiries. Later: marketing, fraud/finance, business intelligence. Tool calls require server-side permissions; agent text is not an authority. Untrusted supplier data cannot grant execution privileges.

## 6. Supplier workflow
Catalog mapping → fresh offer validation → destination, margin, restrictions and supplier approval → payment verified → submit PO with unique idempotency key → record supplier acknowledgment → tracking updates. On timeout, reconcile remote status before resubmission. Internal reservation is not an external supplier stock hold.

## 7. Payments and compliance
Hosted payment checkout through approved local/cross-border provider adapters. Verify signatures, amount, order, currency and provider's authoritative status. A browser redirect alone is not proof of payment. No secrets or card details in frontend or logs. Cash-on-delivery needs separate collection accounting. International sales require merchant/acquirer eligibility, seller/importer-of-record, taxes/duties, refund and supplier settlement approval.

## 8. Supabase database
Use dedicated Supabase Cloud PostgreSQL instance. Schema `aacp` holds tenants, products, supplier offers, orders, items, payments, supplier POs, events, agent runs and audit. Internal tables are not granted to anon/authenticated; all tables enable RLS for defense in depth. Future customer policies use verified auth.uid() and resource ownership, not user metadata. No service_role key in client. Store media via private/public Supabase Storage buckets with explicit policies. See `supabase/migrations/`.

## 9. API requirements
GET /health; GET /api/v1/products; GET /api/v1/products/{id}; POST /api/v1/assistant/demo (development-only). Later protected routes: /cart, /checkout, /orders, /supplier-offers, /agent-runs, /approvals and signed /webhooks/{provider}. Version all contracts and events.

## 10. Business event envelope
`event_id`, `schema_version`, `tenant_id`, `aggregate_id`, `correlation_id`, `occurred_at`, `payload`. Events: payment.verified, order.confirmed, supplier.order.accepted, supplier.order.rejected, shipment.status.changed, refund.completed, agent.approval.requested. Transactional outbox + idempotent consumers.

## 11. Acceptance gates
- Demo API returns typed catalog and does not pretend to take payment.
- Auth tests prove orders and media cannot cross customer/tenant boundaries.
- Unverified/duplicate payment callbacks never cause order payment or duplicate supplier PO.
- Stock expiry blocks unsafe checkout; supplier failure escalates safely.
- Refunds cannot exceed verified payment or approved policy.
- Every tool and state transition has an immutable audit reference.
- Restore, outage simulations, performance and privacy checks pass before live launch.

## 12. Outstanding decisions
Product category; named supplier/integration docs; legal merchant identity; approved acquiring and settlement; initial overseas corridor; shipping/returns policy; deployment region and auth-provider choice. Do not expose live checkout before these are resolved.
