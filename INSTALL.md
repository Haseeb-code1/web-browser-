# Nova Browser - Docker Installation & Launcher Guide

Welcome to the **Nova Browser** containerized environment! We have created automated launcher scripts to make running and setup as simple as a single click.

---

## ⚡ Quick Start (One-Click Launcher)

We have provided two double-clickable helper scripts in the root directory:

*   **`run.bat`** (Windows Batch - **Recommended**): Simply open your project directory in Windows Explorer, and double-click `run.bat`.
*   **`run.ps1`** (Windows PowerShell): A PowerShell script that automates the same process from a terminal interface.

### What the Launcher Script Does:
1.  **Checks** if Docker Desktop is installed and running on your host machine.
2.  **Gracefully stops** any legacy container sessions to clean up ports and X11 graphics locks.
3.  **Launches** the container in detached background mode (`docker compose up -d`).
4.  **Automatically opens** your default Windows web browser (Chrome, Edge, Firefox, Brave) straight to:
    ```text
    http://localhost:6080/vnc.html
    ```

---

## 📦 Prerequisites

Before running the launcher, make sure you have:
*   [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/) installed and running (with the WSL2 backend).

---

## 🛠️ Manual CLI Commands

If you prefer using the command line, navigate to this directory in your terminal and run:

```powershell
# Build/Rebuild the container image (extremely fast cache checks)
docker compose build --pull=false

# Start the container in detached mode
docker compose up -d

# Check running status (verify port 6080 and 5900 are mapped)
docker ps

# Follow container console outputs
docker compose logs -f

# Shut down and stop the container
docker compose down
```

---

## 🖥️ Graphical View Port Access

Once the container is active, you can access the application through either method:

### 1. Web Browser (Recommended)
Open Chrome/Edge/Firefox on your Windows host and go to:
👉 **[http://localhost:6080/vnc.html](http://localhost:6080/vnc.html)** (Click "Connect" - no password required).

### 2. Standalone VNC Client
Open any VNC Viewer client on your host and connect to:
👉 **`localhost:5900`** (Password is blank).
