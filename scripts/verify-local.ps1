# AACP local smoke verification. Compatible with Windows PowerShell 5.1.
# No environment variables, credentials or tokens are printed.
param(
    [int]$ApiPort = 8001,
    [int]$WebPort = 3000
)
$ErrorActionPreference = "Stop"
$api = "http://localhost:$ApiPort"
$site = "http://localhost:$WebPort"
Write-Host "Verifying AACP Docker runtime..." -ForegroundColor Cyan
docker compose -f infra/docker-compose.yml ps
if ($LASTEXITCODE -ne 0) { throw "Docker Compose status failed" }

$health = Invoke-RestMethod -Uri "$api/health" -TimeoutSec 10
if ($health.status -ne "ok") { throw "API /health did not return ok" }
Write-Host ("FastAPI health: {0}, environment: {1}, demo: {2}" -f $health.status, $health.environment, $health.demo)

$caps = Invoke-RestMethod -Uri "$api/api/v1/capabilities" -TimeoutSec 10
Write-Host ("Catalog: {0}; live checkout: {1}; supplier procurement: {2}" -f $caps.catalog_mode, $caps.live_checkout, $caps.supplier_procurement)
if ($caps.live_checkout -eq $true -or $caps.supplier_procurement -eq $true) {
    throw "This local smoke test expects unsafe live integrations to remain disabled"
}

$catalog = Invoke-RestMethod -Uri "$api/api/v1/products" -TimeoutSec 10
Write-Host ("Catalog returned {0} product(s)" -f @($catalog).Count)

$page = Invoke-WebRequest -Uri $site -UseBasicParsing -TimeoutSec 15
if ($page.StatusCode -ne 200) { throw "Storefront failed with HTTP $($page.StatusCode)" }
Write-Host ("Next.js storefront: HTTP {0}" -f $page.StatusCode) -ForegroundColor Green
Write-Host "HTTP checks passed. Verify the WebSocket indicator in browser DevTools." -ForegroundColor Green
Write-Host "This does not verify cloud migrations, authenticated merchant functions or real purchases."
