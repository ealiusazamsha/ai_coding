# AACP implementation status

Updated 2026-11-14. This repository is a development foundation, not a live commerce deployment.

| Workstream | Status | Evidence |
|---|---|---|
| Product/software requirements | Authored | `docs/PRS.md`, `docs/SRS.md` |
| Python FastAPI foundation | Committed | `services/api/app/` |
| Next.js storefront | Development preview | `apps/storefront/` |
| Supabase schema migrations | Prepared **but not applied** | `supabase/migrations/` |
| Target Supabase project | **Verified in browser view**: AACP Commerce, Free, healthy, Tokyo | https://supabase.com/dashboard/project/bborikhazomedjzihyiv |
| Target GitHub integration | Displayed in dashboard | `ealiusazamsha/ai_coding` |
| Supabase ChatGPT plugin access | **Denied**, OAuth connection still sees only Global Job Agent | `get_project` permission denied |
| Database tables and migration execution | **Unverified / not executed through this chat** | Requires target project plugin access |
| Browser catalog and shopping assistant | Demonstration only | `apps/storefront/app/page.tsx` |
| Real payment provider | Not implemented | Gateway/merchant prerequisites |
| Supplier purchase submission | Not implemented | Supplier integration prerequisites |
| Supabase Auth verification | Source prepared, integration tests pending | `services/api/app/security.py` |
| Pending-payment order services | Source prepared, cloud tests pending | `services/api/app/commerce.py` |
| Agent orchestration | Not implemented | Only deterministic preview and policy rules |
| GitHub CI | Workflows configured; earlier runs failed without usable logs | `.github/workflows/` |
| Local WebSocket demo | Implemented with origin checks; standalone tests passed; Docker not verified | `services/api/app/realtime.py`, `tests/test_realtime.py` |\n| Docker Compose and frontend WebSocket status | Configuration committed; local Docker run not verified | `infra/docker-compose.yml`, `apps/storefront/components/ConnectionStatus.tsx` |\n| Development workflow | ChatGPT → GitHub → local Docker, **not Codex** | `docs/WORKFLOW.md` |\n| Production deployment | Not performed | Cloud DB connection, providers, CI pending |

**Next prerequisite:** Reconnect Supabase plugin with account/project access to AACP Commerce `mofxvnsmwyhparhesykz`, target `bborikhazomedjzihyiv`. Never migrate the unrelated CareerFlow database.

The legacy project-scoped Codex MCP files were removed because Codex is not in the development workflow. Local Docker and WebSocket execution still require verification on the user's machine.\n