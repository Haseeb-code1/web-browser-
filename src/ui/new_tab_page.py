"""
New Tab Landing Page for Nova Browser.
Generates an advanced HTML/CSS landing page that gets injected into QWebEngineView.
"""

def get_new_tab_html() -> str:
    """Return complete responsive space-dark HTML/CSS template for the browser home tab."""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nova Home</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;500;700&family=Plus+Jakarta+Sans:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0D0F1A;
            --accent-primary: #6C63FF;
            --accent-secondary: #00D4FF;
            --text-primary: #E8E9F3;
            --text-secondary: #8B8FA8;
            --card-bg: rgba(31, 34, 53, 0.45);
            --card-border: rgba(255, 255, 255, 0.06);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            user-select: none;
        }

        body {
            background-color: var(--bg-primary);
            font-family: 'Plus Jakarta Sans', sans-serif;
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            position: relative;
        }

        /* --- Dynamic Moving Space Gradient Background --- */
        .bg-glow-1 {
            position: absolute;
            width: 600px;
            height: 600px;
            background: radial-gradient(circle, rgba(108, 99, 255, 0.15) 0%, rgba(0,0,0,0) 70%);
            top: -200px;
            left: -200px;
            filter: blur(80px);
            animation: float 25s infinite alternate;
            z-index: 1;
        }

        .bg-glow-2 {
            position: absolute;
            width: 700px;
            height: 700px;
            background: radial-gradient(circle, rgba(0, 212, 255, 0.12) 0%, rgba(0,0,0,0) 70%);
            bottom: -250px;
            right: -200px;
            filter: blur(100px);
            animation: float 30s infinite alternate-reverse;
            z-index: 1;
        }

        @keyframes float {
            0% { transform: translate(0, 0) scale(1); }
            100% { transform: translate(150px, 100px) scale(1.2); }
        }

        .container {
            z-index: 10;
            width: 100%;
            max-width: 720px;
            padding: 40px 20px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 36px;
        }

        /* --- Header Brand --- */
        .logo-wrap {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }

        .logo-title {
            font-family: 'Outfit', sans-serif;
            font-size: 56px;
            font-weight: 700;
            letter-spacing: 4px;
            background: linear-gradient(135deg, var(--accent-primary) 30%, var(--accent-secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 20px rgba(108, 99, 255, 0.3));
            animation: glow-pulsing 4s infinite alternate;
        }

        .logo-subtitle {
            color: var(--text-secondary);
            font-size: 14px;
            letter-spacing: 1px;
        }

        /* --- Search Widget --- */
        .search-container {
            width: 100%;
            max-width: 580px;
            position: relative;
        }

        .search-box {
            width: 100%;
            height: 52px;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 99px;
            padding: 0 24px 0 54px;
            font-family: inherit;
            font-size: 15px;
            color: #FFFFFF;
            outline: none;
            backdrop-filter: blur(16px);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }

        .search-box:focus {
            border-color: var(--accent-primary);
            background: rgba(31, 34, 53, 0.7);
            box-shadow: 0 0 24px rgba(108, 99, 255, 0.25);
        }

        .search-icon {
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
            font-size: 18px;
            pointer-events: none;
        }

        /* --- Speed Dials --- */
        .shortcuts-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            width: 100%;
            max-width: 580px;
        }

        .shortcut-card {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            backdrop-filter: blur(12px);
            transition: all 0.25s cubic-bezier(0.25, 0.8, 0.25, 1);
            text-decoration: none;
            color: inherit;
        }

        .shortcut-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-primary);
            background: rgba(108, 99, 255, 0.1);
            box-shadow: 0 8px 24px rgba(108, 99, 255, 0.15);
        }

        .shortcut-icon {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.05);
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 16px;
            font-weight: bold;
            color: var(--accent-secondary);
        }

        .shortcut-name {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-primary);
        }

        /* --- AI Query Box --- */
        .ai-assistant-widget {
            background: linear-gradient(135deg, rgba(108, 99, 255, 0.08) 0%, rgba(31, 34, 53, 0.3) 100%);
            border: 1px solid rgba(108, 99, 255, 0.15);
            border-radius: 16px;
            padding: 20px;
            width: 100%;
            max-width: 580px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            backdrop-filter: blur(16px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35);
        }

        .ai-header {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            font-weight: 700;
            color: var(--accent-secondary);
            letter-spacing: 0.5px;
        }

        .ai-prompt-input {
            width: 100%;
            height: 40px;
            background: rgba(13, 15, 26, 0.6);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            padding: 0 16px;
            font-family: inherit;
            font-size: 13px;
            color: #FFFFFF;
            outline: none;
            transition: border-color 0.25s;
        }

        .ai-prompt-input:focus {
            border-color: var(--accent-secondary);
        }

        .prompt-pills {
            display: flex;
            justify-content: center;
            gap: 8px;
            flex-wrap: wrap;
        }

        .prompt-pill {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 5px 12px;
            font-size: 11px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: all 0.2s;
        }

        .prompt-pill:hover {
            background: rgba(0, 212, 255, 0.1);
            color: var(--accent-secondary);
            border-color: rgba(0, 212, 255, 0.3);
        }

        @keyframes glow-pulsing {
            0% { filter: drop-shadow(0 0 10px rgba(108, 99, 255, 0.2)); }
            100% { filter: drop-shadow(0 0 25px rgba(108, 99, 255, 0.5)); }
        }
    </style>
</head>
<body>
    <div class="bg-glow-1"></div>
    <div class="bg-glow-2"></div>

    <div class="container">
        <!-- Logo -->
        <div class="logo-wrap">
            <div class="logo-title">NOVA</div>
            <div class="logo-subtitle">TRANSCEIVER DESKTOP PORTAL</div>
        </div>

        <!-- Search Bar -->
        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" class="search-box" id="search-input" placeholder="Search the web or type a URL..." autofocus>
        </div>

        <!-- Speed Dial Grid -->
        <div class="shortcuts-grid">
            <a href="https://github.com" class="shortcut-card">
                <div class="shortcut-icon" style="color: #6C63FF; background: rgba(108, 99, 255, 0.1);">GH</div>
                <div class="shortcut-name">GitHub</div>
            </a>
            <a href="https://google.com" class="shortcut-card">
                <div class="shortcut-icon" style="color: #00D4FF; background: rgba(0, 212, 255, 0.1);">G</div>
                <div class="shortcut-name">Google</div>
            </a>
            <a href="https://youtube.com" class="shortcut-card">
                <div class="shortcut-icon" style="color: #FF4757; background: rgba(255, 71, 87, 0.1);">YT</div>
                <div class="shortcut-name">YouTube</div>
            </a>
            <a href="https://reddit.com" class="shortcut-card">
                <div class="shortcut-icon" style="color: #FFB830; background: rgba(255, 184, 48, 0.1);">RD</div>
                <div class="shortcut-name">Reddit</div>
            </a>
        </div>

        <!-- AI Panel Widget -->
        <div class="ai-assistant-widget">
            <div class="ai-header">
                <span>✦</span> AI LOCAL COMPANION
            </div>
            <input type="text" class="ai-prompt-input" id="ai-input" placeholder="Ask Ollama / local LLM anything...">
            <div class="prompt-pills">
                <div class="prompt-pill" onclick="fillPrompt('Explain Quantum Computing briefly')">Quantum Computing</div>
                <div class="prompt-pill" onclick="fillPrompt('Draft an introductory professional email')">Draft email</div>
                <div class="prompt-pill" onclick="fillPrompt('Write a quick Python script for file renaming')">Python helper</div>
            </div>
        </div>
    </div>

    <script>
        // Handle Search Bar navigation
        const searchInput = document.getElementById('search-input');
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const query = searchInput.value.trim();
                if (query) {
                    if (query.includes('.') && !query.includes(' ')) {
                        // Navigate to URL
                        window.location.href = query.startsWith('http') ? query : 'https://' + query;
                    } else {
                        // Google Search
                        window.location.href = 'https://www.google.com/search?q=' + encodeURIComponent(query);
                    }
                }
            }
        });

        // AI Input dispatching
        const aiInput = document.getElementById('ai-input');
        aiInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const query = aiInput.value.trim();
                if (query) {
                    // Send message request back to PyQt window channel
                    window.chrome.webview.postMessage(JSON.stringify({
                        action: "ask_ai",
                        prompt: query
                    }));
                }
            }
        });

        function fillPrompt(text) {
            aiInput.value = text;
            aiInput.focus();
        }
    </script>
</body>
</html>
"""
