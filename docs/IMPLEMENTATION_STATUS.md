# AACP implementation status

Updated 2026-11-14. Source code is committed; this is **not** a production deployment.

| Item | Status | Evidence |
|---|---|---|
| Product/software requirements | Authored | docs/PRS.md, docs/SRS.md |
| Python FastAPI | Development foundation committed | services/api/app/ |
| Next.js storefront | Demo preview committed | apps/storefront/ |
| Database migrations | Prepared, **not deployed** | supabase/migrations/ |
| Target Supabase endpoint | Supplied by user, **not yet authorized** | https://bborikhazomedjzihyiv.supabase.co |
| Supabase project metadata | **Permission denied** for ref `bborikhazomedjzihyiv` | Supabase connector get_project |
| Cloud database tables | **Not verified** | Requires Supabase project access |
| Public demo catalog and chat | Development-only | apps/storefront/app/page.tsx |
| Real supplier sync/PO submission | Not implemented | Requires approved supplier API |
| Real payment provider | Not implemented | Requires approved merchant and gateway |
| Supabase Auth token verification | Prepared; requires integration tests | services/api/app/security.py |
| Pending-payment order foundation | Prepared; requires database integration tests | services/api/app/commerce.py |
| Durable outbox dispatcher | Not implemented | Only event persistence model exists |
| AI agent orchestration | Not implemented | Only deterministic demo and policy functions |
| SaaS merchant onboarding | Not implemented | Tenant-aware schema groundwork |
| CI | Workflows configured; most recent reported failed (no usable execution logs) | .github/workflows/ |
| Production deployment | Not performed | Requires Supabase authorization, provider approvals and CI verification |

**Next action:** Reconnect Supabase to the account/organization that owns `bborikhazomedjzihyiv` via ChatGPT Settings → Plugins; then inspect, migrate and verify only that target. Do not use or modify the existing CareerFlow/job_agent project.
