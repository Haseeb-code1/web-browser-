# API Test Studio / Nova Browser - PowerShell Launcher
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  API Test Studio / Nova Browser - Container Launcher" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker CLI is installed
if (-not (Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Docker is not installed or not in your Windows PATH." -ForegroundColor Red
    Write-Host "Please install Docker Desktop for Windows: https://www.docker.com/products/docker-desktop/" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Docker Desktop daemon is running
docker info >$null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Docker Desktop is installed but NOT running." -ForegroundColor Red
    Write-Host "Please start Docker Desktop from your Start Menu first, then run this script again." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[1/3] Cleaning up any old container sessions..." -ForegroundColor Yellow
docker compose down

Write-Host ""
Write-Host "[2/3] Launching Nova Browser container in background..." -ForegroundColor Yellow
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "[ERROR] Failed to start container. Check the compose log above." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[3/3] Warming up display server and launching web portal..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Start-Process "http://localhost:6080/vnc.html"

Write-Host ""
Write-Host "===================================================" -ForegroundColor Green
Write-Host "  SUCCESS! Nova Browser is running in Docker." -ForegroundColor Green
Write-Host "  Your default web browser has been opened to:" -ForegroundColor Green
Write-Host "  http://localhost:6080/vnc.html" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to finish"
