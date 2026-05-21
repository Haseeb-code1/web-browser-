<h1 align="center">🌐 Nova Browser</h1>

<p align="center">
  <strong>A highly sophisticated, AI-powered desktop web browser engineered with Python and PyQt6 (QtWebEngine).</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/PyQt6-QtWebEngine-green.svg" alt="PyQt6">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status">
</p>

---

## ✨ Features

### 🤖 AI Floating Panel — `Ctrl + 5`
> **The crown feature of Nova Browser.**

Press `Ctrl + 5` at any time to instantly toggle a transparent floating AI assistant over any web page — no tab switching, no interruptions.

- **Instant access** — one keystroke from anywhere in the browser
- **Context-aware** — reads and summarizes the current page on demand
- **Multi-model routing** — switch between Gemini, Groq, and local Ollama
- **Smart Selection Watcher** — highlight any text for instant AI insights
- **Dismiss anytime** — press `Ctrl + 5` again or click outside to close

### 🌐 Core Browser Features

- **Multi-Tab Browsing** — add, remove, and navigate tabs seamlessly
- **Bookmarks Manager** — save favourite pages with persistent storage
- **Browsing History** — auto-logged, searchable, with one-click clear
- **Download Manager** — built-in queue with progress tracking and cancel support
- **Ad & Tracker Blocking** — integrated domain filter via `ad_blocker.py`
- **Hardware Acceleration** — Chromium core (QtWebEngine) for smooth rendering and High-DPI support

---

## 📥 Download & Run (No Python Required)

A pre-built Windows executable is ready in the **`output/`** folder.

1. Go to the [`output/`](https://github.com/Haseeb-code1/web-browser-/tree/main/output) folder in this repo
2. Click `NovaBrowser.exe`
3. Click **⬇️ Download raw file** (top-right of the file preview)
4. Double-click the downloaded file to launch — no setup needed

> ⚠️ Windows SmartScreen may appear. Click **"More info" → "Run anyway"** to proceed.

---

## 💻 Developer Setup

### Prerequisites
- Python 3.11+
- Git

### 1. Clone & Install

```bash
git clone https://github.com/Haseeb-code1/web-browser-.git
cd web-browser-
pip install -r requirements.txt
```

### 2. Run Locally

```bash
python main.py
```

Windows users can also double-click `run.bat`.

### 3. Run Tests

```bash
pytest tests/
```

### 4. Build Your Own EXE

```bash
pyinstaller --onefile --windowed main.py
# Output → dist/main.exe
```

Or use the provided PowerShell script:

```powershell
.\build_installer.ps1
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| **`Ctrl + 5`** | **✨ Toggle AI Floating Panel** |
| `Ctrl + T` | New Tab |
| `Ctrl + W` | Close Tab |
| `Ctrl + L` | Focus Address Bar |
| `Ctrl + R` | Reload Page |
| `Alt + ←` | Go Back |
| `Alt + →` | Go Forward |
| `Ctrl + D` | Bookmark Page |
| `Ctrl + H` | History |
| `Ctrl + J` | Downloads |

---

## 🏗️ Project Structure

```text
web-browser-/
├── main.py                     # Entry point & splash screen launcher
├── requirements.txt            # Python dependencies
├── run.bat                     # Quick launch script
├── Dockerfile                  # Containerization config
├── docker-compose.yml
│
├── scripts/
│   ├── build_installer.ps1     # Builds the .exe and installer
│   └── github_setup.py         # CI/CD and repo setup
│
└── src/
    ├── ai_assistant/           # 🧠 AI Integration Layer
    │   ├── floating_bot.py     # Floating panel logic (Ctrl + 5)
    │   ├── model_router.py     # Routes between Groq, Gemini, Ollama
    │   └── selection_watcher.py
    │
    ├── core/                   # ⚙️ Core Browser Logic
    │   ├── history.py
    │   ├── bookmarks.py
    │   └── ad_blocker.py
    │
    ├── ui/                     # 🎨 User Interface
    │   ├── browser_window.py
    │   ├── tab_manager.py
    │   ├── components/         # Toolbar, Address Bar, etc.
    │   └── dialogs/            # Downloads, History, Settings
    │
    └── utils/
        └── exception_logger.py
```

---

## ⚙️ Engineering Principles

Built using the **Incremental Process Model** — each phase delivered a stable, tested feature set:

| Phase | Deliverable |
|---|---|
| 1 | Basic navigation & Chromium rendering |
| 2 | Multi-tab support & UI components |
| 3 | Persistence — bookmarks, history, downloads |
| 4 | AI Integration — floating panel via `Ctrl + 5` |

**Lehman's Laws applied:** the codebase continuously evolved from a single `main.py` into a modular `src/` structure, with each increment unit-tested before the next phase began. Standard browser UX (tabs, address bar) was preserved throughout for familiarity.

---

<p align="center">Developed with ❤️ by <a href="https://github.com/Haseeb-code1">Haseeb-code1</a></p>
