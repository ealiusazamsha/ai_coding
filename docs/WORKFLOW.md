# AACP project workflow

**The project is developed in ChatGPT and committed directly to GitHub, without Codex.**

1. Define and review requirements and code changes in this conversation.
2. Commit the implementation to `ealiusazamsha/ai_coding` on GitHub.
3. On the local workstation, `git pull origin main`.
4. Build and run Docker Compose from the repository root.
5. Validate REST, WebSocket and UI in the local Docker environment.
6. Report exact test results, errors and logs back in this chat; fix and push the next commit.

The runtime stack is **Next.js frontend + Python FastAPI HTTP/WebSocket backend + separate Supabase Cloud PostgreSQL**. Use WebSocket for asynchronous server-to-browser events, not for direct access to Supabase database. The initial socket is demo-only and does not transmit private data.

Do not assume GitHub commits, CI failures or local Docker states are equivalent to successful deployment. Verify actual running containers and database connections before claiming completion.

See `docs/LOCAL_DOCKER.md`.
