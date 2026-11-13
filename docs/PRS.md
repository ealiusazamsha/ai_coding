# AACP — Product Requirements Specification
Version: 1.0 · 2026-11-13 · Proposed baseline

## Vision
An AI-operated supplier-fulfilled store for Bangladesh and legally supported international markets, eventually offered as tenant-isolated SaaS. The platform automates routine shopping assistance, sourcing, order orchestration, support and notifications, while deterministic backend services handle security, inventory commitments and financial correctness.

## Personas
**Shopper:** search, compare, pay, track and ask for help.
**Merchant:** configure approved suppliers, product margins, regions, agents and risk policies.
**Supplier:** accept orders, report availability and shipments.
**Operator:** resolve failed payments, fraud, delayed shipments and blocked agent actions.
**Future SaaS tenant:** provision and operate an independent merchant store.

## MVP goals
1. Accessible, responsive Next.js storefront with polished light visual system.
2. Python FastAPI API and domain services.
3. Supabase-managed Postgres database in a **dedicated project**.
4. Catalog/product/supplier-offer normalization and freshness rules.
5. Cart, quotes and checkout integration with verified payment adapters.
6. Durable order workflow with supplier routing and exception queue.
7. AI sales, catalog, operations and support tools with explicit permissions.
8. Agent audit, operations dashboard and emergency stop.
9. Media pipeline with thumbnails, alt text, license and access policies.

## Initial delivery sequence
Discovery and merchant/supplier/payment feasibility → foundation → supplier and payments → AI coordination → end-to-end testing → controlled pilot → SaaS provisioning and billing.

## Market constraints
Bangladesh and international markets require separate merchant acquiring, currencies, tax/customs handling, importer-of-record decisions and supplier settlement approval. A provider's global brand does not imply a Bangladeshi entity is eligible. No simulated gateway must be enabled in production.

## Success targets (not measured outcomes)
At least 90% autonomous processing of **eligible** routine orders; no duplicate payments or supplier orders on replay; 100% payment confirmation via verified provider status; observable and auditable agent actions; target 99.9% production availability after hardening.

## Decisions required
First category and product restrictions; first supplier with API; merchant legal entity; Bangladesh payment provider; first international destination corridor; return/refund terms; shipping partners.
