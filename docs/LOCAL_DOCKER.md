# Windows Docker — local AACP + WebSocket preview

## Fix: port 8000 already allocated
The default host port for FastAPI is now **8001**, so an existing local app may continue to use 8000. The container itself still listens on 8000. Next.js is preconfigured at image BUILD time to connect to `http://localhost:8001` and `ws://localhost:8001/ws/v1/demo`.

### Step 1: update and restart
In **PowerShell**, from your existing AACP repository folder:

```powershell
git pull origin main
docker compose -f infra/docker-compose.yml down
docker compose -f infra/docker-compose.yml config
docker compose -f infra/docker-compose.yml up --build -d
docker compose -f infra/docker-compose.yml ps
```

Use `docker compose -f infra/docker-compose.yml logs --tail=100 api storefront` if a container fails. Avoid `down -v` and `docker system prune` unless you intentionally want to remove data or unused resources.

### Step 2: check expected endpoints
- Storefront: http://localhost:3000
- API health: http://localhost:8001/health
- API documentation: http://localhost:8001/docs
- Development WebSocket: ws://localhost:8001/ws/v1/demo

The homepage displays `Demo WebSocket connected` after the FastAPI demo handshake. In Chrome DevTools → Network → WS, inspect `system.connected` and `ping` / `pong` frames. This is a **development socket**, not real payments, inventory sync or customer/order event delivery.

### Step 3: identify another port conflict
```powershell
docker ps --format "table {{.Names}}\t{{.Ports}}"
Get-NetTCPConnection -LocalPort 8001 -State Listen |
  Select-Object LocalAddress, LocalPort, OwningProcess
```
If another process owns 8001, do **not** kill it blindly. Choose a free host port, e.g. 8010, by setting these together **before the build**:

```powershell
$env:AACP_API_HOST_PORT="8010"
$env:AACP_PUBLIC_API_URL="http://localhost:8010"
$env:AACP_PUBLIC_WS_URL="ws://localhost:8010/ws/v1/demo"
docker compose -f infra/docker-compose.yml up --build -d
```

The frontend is compiled with browser URLs: setting only the host port is insufficient. To restore defaults in your current PowerShell session:
```powershell
Remove-Item Env:AACP_API_HOST_PORT,Env:AACP_PUBLIC_API_URL,Env:AACP_PUBLIC_WS_URL -ErrorAction SilentlyContinue
```

If port 3000 is in use too, set `$env:AACP_WEB_HOST_PORT="3001"` and `$env:AACP_ALLOWED_ORIGINS="http://localhost:3001"`; open http://localhost:3001. FastAPI WebSocket origin checks require the changed origin. These settings can also be placed in `infra/.env` or passed via an explicit Compose `--env-file`; do not commit credential-bearing environment files.

## Architecture and security
```text
Browser http://localhost:3000
  ├── HTTPS/HTTP REST ───────────────► FastAPI http://localhost:8001/api/v1/*
  └── WebSocket demo heartbeat ──────► FastAPI ws://localhost:8001/ws/v1/demo

Docker internal: API listens on port 8000, Next.js on port 3000.
Supabase Cloud PostgreSQL is a separate TLS database connection for Python.
```

**WebSocket is not a database connection.** The standalone demo works without Supabase. Cloud migrations have not yet been applied by this conversation because the ChatGPT Supabase plugin lacks project permission.

## Repeat updates
```powershell
git pull origin main
docker compose -f infra/docker-compose.yml up --build -d
docker compose -f infra/docker-compose.yml ps
```

## More details
- Containers resolve each other by service DNS name, e.g. `api:8000`; browser JavaScript does **not** resolve that Docker DNS.
- `NEXT_PUBLIC_*` URLs are embedded at build time and require a frontend image rebuild when changed.
- Ports bind to `127.0.0.1` by default to prevent exposing the unfinished service on your LAN/Internet.
- Public HTTPS deployments need WSS, real authentication and tenancy authorization. The current WebSocket is limited to development preview events.
- See `docs/DEPLOYMENT.md` and `docs/SUPABASE_SETUP.md` for production prerequisites.

## WebSocket stays at "Connecting demo channel…"
A healthy FastAPI HTTP endpoint is **not** sufficient to prove WebSocket protocol support. The API requires `uvicorn[standard]`, which includes the WebSocket protocol implementation. The API Dockerfile now checks that dependency and imports the FastAPI application during the build.

To pull and rebuild **only the API** after this fix:

```powershell
git pull origin main
docker compose -f infra/docker-compose.yml up --build -d api
docker compose -f infra/docker-compose.yml up -d storefront
docker compose -f infra/docker-compose.yml ps
docker compose -f infra/docker-compose.yml logs --tail=80 api
```

Refresh http://localhost:3000 with Ctrl+F5. The indicator should show `Demo WebSocket connected` when the API sends its `system.connected` message.

If it is still connecting, inspect Chrome DevTools → Network → WS, or use this read-only browser-console probe from the storefront page:

```javascript
const ws = new WebSocket("ws://localhost:8001/ws/v1/demo");
ws.onmessage = (event) => console.log("AACP socket message:", event.data);
ws.onopen = () => console.log("AACP socket opened");
ws.onerror = (event) => console.error("AACP socket error", event);
ws.onclose = (event) => console.log("AACP socket closed", event.code, event.reason);
```

If you see a 403, check the browser origin (`http://localhost:3000`) against `AACP_ALLOWED_ORIGINS`. If the Network panel shows a connection to port 8000 instead of 8001, ensure the storefront image was rebuilt with the updated Next.js build args. Use `docker compose -f infra/docker-compose.yml up --build -d` in that case.

**No production/private order WebSocket authorization is implemented.** This test channel must remain local and in development mode.
