# AACP local acceptance tests (without GitHub Actions)

The GitHub Actions jobs currently report failure without usable step logs. **Do not treat a successful Docker image build as proof of a passing test suite.**

## 1. Run backend unit / SQLite tests in an isolated Docker build stage
From your repository root:

```powershell
git pull origin main
docker build --target tests --progress=plain -t aacp-api-tests ./services/api
```

The build stage installs `requirements-dev.txt`, compiles the app and tests, and executes `pytest -q`. If the stage fails, the complete test traceback is available in the PowerShell output without requiring changes to the running API container.

## 2. Build both runtime containers
```powershell
docker compose -f infra/docker-compose.yml up --build -d
docker compose -f infra/docker-compose.yml ps
powershell -ExecutionPolicy Bypass -File scripts/verify-local.ps1
```

The smoke checks verify HTTP health, capabilities, catalog and frontend response.

## 3. WebSocket
In `AACP_DEMO_MODE=true`, check the browser's status indicator: **Demo WebSocket connected**. In Cloud database mode the anonymous demo socket is intentionally disabled: the indicator becomes **Private live updates not enabled**.

## 4. Cloud database acceptance
After applying all four SQL migrations in the verified AACP project, test live PostgreSQL `/ready`, merchant credentials, user ownership, row security and operator actions manually. Do not enable real procurement or payments until provider-specific integration tests exist.

## 5. If something fails
Collect targeted logs (avoid secrets):

```powershell
docker compose -f infra/docker-compose.yml logs --tail=120 api storefront
```

Do not remove volumes or run Docker-wide prune as part of routine troubleshooting.
