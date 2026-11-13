# Connect Codex to AACP Supabase MCP

The repository contains project-scoped Codex configuration at `.codex/config.toml`. This selects the dedicated Supabase AACP project reference `bborikhazomedjzihyiv` and the feature set supplied by the project owner.

## Quick start (run in your local Codex terminal)
1. Clone or pull `https://github.com/ealiusazamsha/ai_coding.git` and open the repository root with Codex. **Trust this specific project** when prompted so its `.codex/config.toml` is loaded.
2. Authenticate the Supabase MCP server: `codex mcp login supabase`. In the browser OAuth flow, sign in to the Supabase account owning the **AACP Commerce** organization and approve the requested access.
3. Verify registration using `codex mcp list` (or `codex mcp get supabase`) and test a **read-only** question: "List schemas and migration history for project bborikhazomedjzihyiv. Do not execute DDL."
4. Only after verifying the project reference, organization and existing schema, review and apply the migrations in `supabase/migrations/`, recording evidence.

## Alternative global Codex CLI registration
If the project-scoped configuration is not loaded, you may register the same server on your own machine with:

```bash
codex mcp add supabase --url "https://mcp.supabase.com/mcp?project_ref=bborikhazomedjzihyiv&features=docs%2Caccount%2Cdatabase%2Cdebugging%2Cdevelopment%2Cfunctions%2Cbranching%2Cfeedback%2Cnotebooks"
codex mcp login supabase
codex mcp list
```

**Quote the entire URL.** In bash/zsh, an unquoted `&` sends part of the command into the background; an unquoted `?` may also be treated as a glob pattern. Do not duplicate registration unnecessarily; the repository-specific `.codex/config.toml` already declares the endpoint.

## Scope, security and platform distinction
- `project_ref=bborikhazomedjzihyiv` restricts Supabase MCP to AACP. This does **not** authorize other Supabase projects.
- Supabase disables account-level tools when project scope is selected, even if `account` appears in the feature list.
- The supplied feature groups include database modification capability. Review and approve migrations and any destructive changes; do not deploy payment or purchasing workflows without separate explicit approval.
- OAuth credentials remain in your local MCP client, not in GitHub.
- **Codex CLI MCP configuration is independent of ChatGPT's Supabase plugin connection.** Adding this server to Codex does not fix the ChatGPT plugin's prior permission denial. Reauthorize that plugin separately if migrations should be executed directly from this conversation.
- Never commit `DATABASE_URL`, Supabase secret/service-role keys, access tokens, customer data or uploaded invoices.

Official references:
- https://supabase.com/docs/guides/ai-tools/mcp
- https://learn.chatgpt.com/docs/cli/reference
- https://learn.chatgpt.com/docs/config-file/config-basic
