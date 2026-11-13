# AACP implementation status

Updated 2026-11-14. This is a source-code delivery checkpoint, not a production deployment.

| Item | Status | Evidence |
|---|---|---|
| SRS and PRS | Authored | docs/SRS.md and docs/PRS.md |
| Python FastAPI | Source implemented | services/api/app |
| Next.js storefront | Source implemented | apps/storefront |
| Supabase schema | Prepared, not deployed | supabase/migrations |
| Browser demo cart and assistant | Implemented for preview | apps/storefront/app/page.tsx |
| Real supplier inventory sync | Not implemented | Requires approved supplier API |
| Real payment gateway verification | Not implemented | Requires approved merchant and gateway |
| Supplier purchase submission | Not implemented | Cannot be enabled before verified payment |
| Supabase Auth verification | Backend code prepared; not integration tested | app/security.py |
| Pending-payment order creation | Backend code prepared; not cloud integration tested | app/commerce.py |
| Outbox dispatch worker | Not implemented | Only outbox records exist |
| Real AI agent orchestration | Not implemented | Only deterministic preview and permission policies |
| Tenant-safe SaaS merchant onboarding | Not implemented | Data model groundwork only |
| GitHub Actions | Configured | .github/workflows/ |
| Production deployment | Not performed | No approved AACP infrastructure/secrets |

Critical blocker: Supabase organization selection for new dedicated project, even if current project quote is $0/month. Existing project contains CareerFlow/job_agent data and must not be repurposed without explicit authorization.
