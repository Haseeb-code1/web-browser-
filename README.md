<h1 align="center">
  🌐 Nova Browser (API Test Studio)
</h1>
<p align="center">
  <strong>A modern, AI-powered desktop web browser built with Python and PyQt6.</strong>
  <strong>A highly sophisticated, AI-powered desktop web browser engineered with Python and PyQt6 (QtWebEngine).</strong>
</p>
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/PyQt6-QtWebEngine-green.svg" alt="PyQt6">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Mac-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status">
</p>
---
## ✨ Key Features
## ✨ Comprehensive Feature Set
- **🤖 AI Floating Panel** (`CTRL + 5`): Instantly access our state-of-the-art AI assistant overlay from any web page. Just press `CTRL + 5` to toggle the panel and get smart insights, summaries, and answers on the fly!
- **📑 Multi-Tab Browsing**: Seamlessly browse multiple websites simultaneously with a modern tabbed interface.
- **🔖 Bookmarks & History**: Easily save your favorite sites and manage your browsing history.
- **⬇️ Download Manager**: Built-in, reliable file downloader.
- **⚡ Hardware Acceleration**: Smooth performance and rendering powered by QtWebEngine.
Nova Browser is not just another wrapper; it is built with extensive functionality mirroring modern browsers alongside cutting-edge AI integrations.
### 🤖 Intelligent AI Capabilities
- **Floating AI Assistant (`CTRL + 5`)**: Instantly toggle a transparent, floating AI panel over any web page. This assistant can read page contexts, summarize articles, and answer queries directly without interrupting your workflow.
- **Multi-Model Routing**: Supports switching between models (Gemini, Groq, local Ollama) based on your needs.
- **Smart Selection Watcher**: Highlights text and instantly pulls contextual insights through the AI integration.
### 🌐 Core Browser Functionality
- **Dynamic Multi-Tab Management**: Seamlessly add, remove, and navigate between multiple concurrent web pages. 
- **Robust Bookmarking System**: Save your favorite pages and access them via a dedicated bookmark bar.
- **Persistent History Tracking**: Automatically logs your browsing journey, accessible via a beautifully styled dialog.
- **Built-in Download Manager**: Handle file downloads natively, tracking progress and managing files within the application.
- **Hardware Acceleration**: Built on `QtWebEngine` (Chromium core), delivering smooth animations and accelerated rendering.
- **Ad & Tracker Blocking**: An integrated core engine (`ad_blocker.py`) filters malicious domains.
---
## 🚀 Getting Started (Easiest Way)
## 🚀 Getting Started (The Easy Way)
You don't need to install Python or set up a development environment to use Nova Browser! We have provided a pre-compiled, ready-to-use executable file.
For non-developers who want to use the browser immediately, we provide a standalone executable.
### 📥 How to Download & Run
### 📥 Downloading and Running the Application
1. Navigate to the `output/` folder in this repository.
2. Click on the `NovaBrowser.exe` file and download it to your computer.
3. Double-click the downloaded `.exe` file to launch the browser immediately. 
*(No installation required—it works straight out of the box!)*
1. Navigate to the `output/` folder located at the root of this repository.
2. Locate the **`NovaBrowser.exe`** file.
3. Download it to your computer.
4. **Double-click** the executable to run the browser. 
*(No Python installation or command-line setup is required!)*
---
## 💻 For Developers
## 💻 Developer Setup & Building
If you want to run the browser directly from the source code or contribute to the project, follow these steps:
If you wish to explore the code or contribute to the project:
### Prerequisites
- Python 3.11 or higher
- **Python 3.11+**
- Git
### Installation
### 1. Installation
```bash
# Clone the repository
git clone https://github.com/Haseeb-code1/web-browser-.git
cd web-browser-
# Install the required dependencies
pip install -r requirements.txt
```
### Running the App
### 2. Running Locally
Run the main script to launch the UI:
```bash
python main.py
```
*(Alternatively, you can use the `run.bat` script provided in the root directory, which supports Docker containerized execution.)*
### Running Tests
Ensure everything is working correctly by running the test suite:
### 3. Compiling the Executable
If you modify the source code and want to generate your own `.exe`:
```bash
pytest tests/
pyinstaller --onefile --windowed main.py
```
The newly compiled executable will be placed in the `dist/` folder.
### Building your own EXE
If you make code changes and want to compile your own standalone executable:
```bash
pyinstaller --onefile --windowed main.py
---
## 🏗️ Project Architecture & Structure
Nova Browser is highly modularizing, separating the UI layer from the core logic and AI engines.
```text
API-TEST-STUDIO/
├── main.py                   # Application entry point & SplashScreen launcher
├── requirements.txt          # Python dependencies
├── run.bat                   # Docker execution script
├── Dockerfile                # Containerization config
├── docker-compose.yml        # Docker compose configuration
│
├── scripts/                  # Automation & DevOps scripts
│   ├── build_installer.ps1   # Builds the .exe and installer
│   └── github_setup.py       # CI/CD and repository setup scripts
│
└── src/                      # Source Code Directory
    ├── ai_assistant/         # 🧠 AI Integration Layer
    │   ├── floating_bot.py   # Floating UI panel logic (CTRL + 5)
    │   ├── model_router.py   # Routes requests between Groq, Gemini, Ollama
    │   └── selection_watcher.py 
    │
    ├── core/                 # ⚙️ Core Browser Logic
    │   ├── history.py        # SQLite/JSON history tracking
    │   ├── bookmarks.py      # Bookmark manager
    │   └── ad_blocker.py     # Network interception and ad blocking
    │
    ├── ui/                   # 🎨 User Interface & Components
    │   ├── browser_window.py # Main window layout & QtWebEngineView configuration
    │   ├── tab_manager.py    # Multi-tab logic
    │   ├── components/       # Reusable UI widgets (Toolbar, Address Bar, etc.)
    │   └── dialogs/          # Popups for Downloads, History, and Settings
    │
    └── utils/                # 🛠️ Helpers
        └── exception_logger.py # Centralized error handling
```
*(Your new executable will be generated in the `dist/` folder.)*
---
## 🏗️ Architecture & Software Engineering
## ⚙️ How It Works (Engineering Principles)
This project is built using the **Incremental Process Model**. Each increment added a fully working feature set: 
`navigation -> tabs -> bookmarks -> history -> downloads -> testing -> refactoring`. 
This allowed for solo development with continuous testing and stabilization at each stage.
### Architecture
Nova Browser utilizes **PyQt6's `QWebEngineView`**, which embeds a fully functional Chromium browser engine inside the Python application. The UI elements (Address Bar, Tabs) are strictly separated from the core Chromium processes, communicating via Qt's powerful Signal/Slot event loop system.
**Lehman's Laws Applied:**
- **Continuing Change:** Browser features grew dynamically with each increment, adapting to new requirements like downloads and history.
- **Increasing Complexity:** The codebase naturally evolved from a single script to a structured, multi-file module system.
- **Self Regulation:** Each increment was rigorously reviewed and unit-tested before starting the next.
- **Conservation of Familiarity:** The familiar, Chrome-like UX (tabs, address bar, navigation) was consistently maintained throughout the lifecycle.
### Software Development Lifecycle
This project strictly adheres to the **Incremental Process Model**:
- **Phase 1**: Basic navigation and Chromium rendering.
- **Phase 2**: Multi-tab support and UI components.
- **Phase 3**: Persistence layers (Bookmarks, History, Downloads).
- **Phase 4**: Advanced features (AI Integration via `CTRL + 5`).
By building in increments, the codebase remains stable, and unit tests (via `pytest`) are easily written for each module before moving to the next.
### Lehman's Laws of Software Evolution
- **Continuing Change:** The browser is continuously adapting to user requirements (like the addition of the Groq/Gemini AI backend).
- **Increasing Complexity:** The file structure deliberately evolved from a single `main.py` into the highly modular `src/` directory tree to manage complexity efficiently.
- **Conservation of Familiarity:** Standard browser UX paradigms (tabs at the top, address bar below) were preserved to ensure the browser remains intuitive.
---
<p align="center">
  Developed by <a href="https://github.com/Haseeb-code1">Haseeb-code1</a> 🚀
  Developed with ❤️ by <a href="https://github.com/Haseeb-code1">Haseeb-code1</a>
</p>
