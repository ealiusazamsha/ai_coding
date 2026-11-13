# Local Docker + WebSocket workflow (no Codex)

## Architecture

```text
Browser http://localhost:3000
  ├── HTTP REST ────────────────────► FastAPI http://localhost:8000/api/v1/*
  └── WebSocket (demo heartbeat) ───► FastAPI ws://localhost:8000/ws/v1/demo

FastAPI ───► Supabase Cloud PostgreSQL via TLS (future environment configuration)
```

**WebSocket is for live event delivery, not database connectivity.** Postgres connections use a secure PostgreSQL protocol connection from the Python backend to Supabase Cloud. The current WebSocket is a small, development-only heartbeat/catalog-preview channel, not authenticated order notifications.

## Windows / PowerShell steps

Prerequisites: Git, Docker Desktop with Compose v2, Docker Desktop running.

```powershell
git clone https://github.com/ealiusazamsha/ai_coding.git
cd ai_coding
docker compose -f infra/docker-compose.yml up --build -d
docker compose -f infra/docker-compose.yml ps
```

Open:
- Storefront: http://localhost:3000
- FastAPI health: http://localhost:8000/health
- FastAPI docs: http://localhost:8000/docs
- WebSocket: ws://localhost:8000/ws/v1/demo

The storefront shows **Demo WebSocket connected** when the handshake succeeds. WebSocket servers cannot be tested using a normal HTTP browser address bar. The page opens the browser WebSocket connection automatically.

Verify from browser DevTools -> Network -> WS and inspect the `system.connected` message and subsequent `ping`/`pong` frames.

## Updates

```powershell
git pull origin main
docker compose -f infra/docker-compose.yml up --build -d
docker compose -f infra/docker-compose.yml logs -f --tail=100
```

Stop containers with `docker compose -f infra/docker-compose.yml down`.

## Docker networking

- Browsers on your Windows machine reach published ports using `localhost:3000` / `localhost:8000`.
- Containers communicate via Compose DNS names, such as `api:8000`; **browser JavaScript cannot resolve `api`**.
- Next.js `NEXT_PUBLIC_*` URLs are embedded when the image is built, not set by container runtime environment. Changing public API or WS URLs requires rebuilding the storefront image.
- Default Compose port bindings use `127.0.0.1` for local-only access; do **not** expose an unauthenticated development API to the public internet.
- For a trusted LAN machine, first change Compose's port bindings and the two public build args to a reachable host IP; then add the exact frontend origin to FastAPI's `AACP_ALLOWED_ORIGINS`. Secure and authenticate before any internet-facing deployment.
- For HTTPS deployment, WebSocket URLs must start with `wss://`.

## Local server development without Docker

```bash
# terminal 1
cd services/api
python -m venv .venv
# Windows: .venv\\Scripts\\Activate.ps1
# Unix: source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# terminal 2
cd apps/storefront
npm install
npm run dev
```

## Supabase status

Target AACP project: `bborikhazomedjzihyiv` in organization **AACP Commerce** (Free). Project appeared healthy in the signed-in dashboard, but the Supabase connector in ChatGPT lacked write access on last check. Do not copy DB credentials into GitHub, Next.js browser settings, or Docker build args. Apply the SQL migrations only after privileged project access and review. The Docker demo operates without the database.

## Production blockers

No real supplier integration, payments, production auth-bound WebSocket subscriptions, Redis/pubsub cross-instance fanout, durable outbox consumer or validated cloud migrations yet. The current WebSocket is not a secure channel for private orders or customer information.
