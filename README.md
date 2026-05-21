🤖 AI Floating Panel (Ctrl + 5) gets its own dedicated section at the very top of the features list, described as the crown feature, with a clear explanation of what it does and why it's special.
📥 EXE Download Guide has a dedicated numbered step-by-step section directing users to the output/ folder, explaining how to download and run it, including the Windows SmartScreen tip.
Everything else included:

Badges for Python, PyQt6, License, and Platform at the top
Full keyboard shortcuts table with Ctrl+5 bold and starred
Project folder structure
Build-from-source instructions using both PyInstaller and build_installer.ps1
Test instructions
Incremental process model summary
ReadmeDocument · MD DownloadYou said: IN CHATIN CHAT8:15 PMClaude responded: Here's your README — paste this directly into your GitHub repo:Here's your README — paste this directly into your GitHub repo:

🌐 Nova Browser
A modern, AI-powered desktop web browser built with Python & PyQt6
Show Image Show Image Show Image Show Image

✨ Features
🤖 AI Floating Panel — Ctrl + 5

The crown feature of Nova Browser.

Press Ctrl + 5 at any time while browsing to instantly summon a floating AI assistant panel. It appears as an overlay on top of your current page — no tab switching, no interruptions.

Instant access — one keystroke, anywhere in the browser
Context-aware — the AI can read and discuss the current page
Floating overlay — stays on top while you keep browsing
Dismiss anytime — press Ctrl + 5 again or click outside to close
Ask anything — summarize pages, explain content, translate, or just chat

🗂️ Tabbed Browsing
Full Chrome-style multi-tab support — open, close, reorder. Ctrl+T new tab, Ctrl+W close tab.
🔖 Bookmarks Manager
Save and organize favourite sites with one-click toolbar access and persistent storage across sessions.
🕑 Browsing History
Full persistent history log with search and one-click clear.
⬇️ Download Manager
Built-in download queue with progress tracking, resume, and cancel support.
🧭 Smart Address Bar
URL auto-completion, search engine fallback, and HTTP/HTTPS security indicator.
⚡ Hardware-Accelerated Rendering
OpenGL shared context, High-DPI support, and Chromium engine (QtWebEngine) under the hood.

📥 Download the EXE (No Python Required)
A pre-built Windows executable lives in the output/ folder of this repo.

Go to output/ on GitHub
Click the .exe file
Click the ⬇️ Download raw file button (top-right of the file preview)
Run the downloaded file — no installation needed


⚠️ Windows may show a SmartScreen warning. Click "More info" → "Run anyway" to proceed.


🛠️ Build the EXE Yourself
bashgit clone https://github.com/Haseeb-code1/web-browser-.git
cd web-browser-
pip install -r requirements.txt
pyinstaller --onefile --windowed main.py
# Output → dist/main.exe
Or on Windows use the provided script:
powershell.\build_installer.ps1

🚀 Run from Source
bashgit clone https://github.com/Haseeb-code1/web-browser-.git
cd web-browser-
pip install -r requirements.txt
python main.py
Windows users can also double-click run.bat.

⌨️ Keyboard Shortcuts
ShortcutActionCtrl + 5✨ Toggle AI Floating PanelCtrl + TNew TabCtrl + WClose TabCtrl + LFocus Address BarCtrl + RReload PageAlt + ←Go BackAlt + →Go ForwardCtrl + DBookmark PageCtrl + HHistoryCtrl + JDownloads

🧪 Tests
bashpytest tests/

📜 License
MIT — Made with ❤️ by Haseeb
