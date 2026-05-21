@echo off
title API Test Studio - Container Launcher
color 0B

:: Check if Docker CLI is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed or not in your PATH.
    echo Please install Docker Desktop for Windows: https://www.docker.com/products/docker-desktop/
    echo.
    pause
    exit /b 1
)

:: Check if Docker Desktop daemon is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker Desktop is installed but NOT running.
    echo Please start Docker Desktop from your Start Menu first, then run this file again.
    echo.
    pause
    exit /b 1
)

echo [1/4] Cleaning up any old container sessions...
docker compose down

echo.

echo [2/4] Building Nova Browser container image...
docker compose build

echo.

echo [3/4] Launching Nova Browser container in background...
docker compose up -d
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Failed to start container. Check the Docker compose error above.
    echo.
    pause
    exit /b 1
)

echo.

echo [4/4] Warming up display server and launching web portal...
timeout /t 5 /nobreak >nul
start "" "http://localhost:6080/vnc.html"

echo.

echo ===================================================
echo   SUCCESS! Nova Browser is running in Docker.
echo   Your default web browser has been opened to:
echo   http://localhost:6080/vnc.html
echo ===================================================
echo.
pause
