"""
Extension Manager
=================
Simulates a Chrome-compatible extension loader for the Python Web Browser.

Architecture
------------
* Each "extension" is stored as a folder under  data/extensions/<ext-id>/
* The folder MUST contain  manifest.json  (Chrome Extension Manifest V2/V3 subset)
* Optional:  content_scripts/  directory with .js files that get injected into pages
* Optional:  background/  directory (logged / acknowledged, not fully sandboxed)
* Optional:  icon.png  used in the UI

Manifest fields supported
-------------------------
  name, version, description, permissions, content_scripts, browser_action/action
"""

import os
import json
import zipfile
import shutil
from typing import List, Dict, Optional
from PyQt6.QtWebEngineCore import QWebEngineScript


from src.utils.paths import get_data_file_path


# ── Paths ──────────────────────────────────────────────────────────────────────
def get_extensions_dir() -> str:
    return get_data_file_path("extensions")

def get_registry_path() -> str:
    return get_data_file_path("extensions_registry.json")


def _ensure_dirs():
    os.makedirs(get_extensions_dir(), exist_ok=True)


# ── Built-in / curated extension catalogue ────────────────────────────────────
CATALOGUE: List[Dict] = [
    {
        "id":          "dark-reader",
        "name":        "Dark Reader",
        "version":     "4.9.0",
        "description": "Inverts page brightness for comfortable dark-mode reading on any website.",
        "icon":        "🌙",
        "permissions": ["tabs", "storage", "http://*/*", "https://*/*"],
        "content_scripts": [{
            "matches": ["<all_urls>"],
            "js_code": """
(function(){
  if (document.getElementById('__python_dark_reader__')) return;
  const s = document.createElement('style');
  s.id = '__python_dark_reader__';
  s.textContent = `
    html { filter: invert(90%) hue-rotate(180deg) !important; }
    img, video, canvas, svg, [style*="background-image"] {
      filter: invert(100%) hue-rotate(180deg) !important;
    }`;
  document.documentElement.appendChild(s);
  console.log('[Dark Reader] Injected');
})();
"""
        }]
    },
    {
        "id":          "ublock-origin",
        "name":        "uBlock Origin",
        "version":     "1.52.0",
        "description": "Efficient, wide-spectrum content blocker. Works on top of the built-in AdGuard layer.",
        "icon":        "🛡️",
        "permissions": ["tabs", "webRequest", "webRequestBlocking", "http://*/*", "https://*/*"],
        "content_scripts": [{
            "matches": ["<all_urls>"],
            "js_code": """
(function(){
  // Hide common ad selectors as a lightweight CSS-based block
  const css = [
    '#ad','#ads','#advert','.ad','.ads','.advert','.advertisement',
    '.banner-ad','.ad-wrapper','[class*="ad-unit"]','[id*="google_ad"]',
    'iframe[src*="doubleclick"]','iframe[src*="googlesyndication"]',
    '[data-ad-unit]','[data-google-av-cxn]',
    '.dfp-ad','.adsbox','#adsense','#adsbygoogle'
  ].join(',');
  if (!document.getElementById('__ubo_css__')) {
    const st = document.createElement('style');
    st.id = '__ubo_css__';
    st.textContent = css + '{display:none!important;visibility:hidden!important;height:0!important;overflow:hidden!important;}';
    document.documentElement.appendChild(st);
  }
  console.log('[uBlock Origin] CSS-level block injected');
})();
"""
        }]
    },
    {
        "id":          "grammarly",
        "name":        "Grammarly",
        "version":     "14.1.0",
        "description": "Adds a writing-quality hint bar to text areas (UI demo — no cloud call).",
        "icon":        "✍️",
        "permissions": ["tabs", "storage"],
        "content_scripts": [{
            "matches": ["<all_urls>"],
            "js_code": """
(function(){
  if (document.getElementById('__grammarly_bar__')) return;
  const observe = () => {
    document.querySelectorAll('textarea, [contenteditable=true]').forEach(el => {
      if (el.dataset.grammarlyAttached) return;
      el.dataset.grammarlyAttached = '1';
      el.addEventListener('focus', () => {
        let bar = document.getElementById('__grammarly_bar__');
        if (!bar){
          bar = document.createElement('div');
          bar.id = '__grammarly_bar__';
          bar.style.cssText='position:fixed;bottom:12px;right:12px;background:#15c39a;color:#fff;'+
            'padding:6px 14px;border-radius:20px;font:bold 13px sans-serif;z-index:2147483647;'+
            'box-shadow:0 2px 8px rgba(0,0,0,.3);cursor:default;';
          bar.textContent='✓ Grammarly Active';
          document.body.appendChild(bar);
          setTimeout(()=>{ if(bar) bar.remove(); }, 3000);
        }
      });
    });
  };
  observe();
  new MutationObserver(observe).observe(document.body||document.documentElement,{childList:true,subtree:true});
})();
"""
        }]
    },
    {
        "id":          "video-speed",
        "name":        "Video Speed Controller",
        "version":     "0.6.3",
        "description": "Adds a floating speed-control HUD to every HTML5 video.",
        "icon":        "⏩",
        "permissions": ["tabs"],
        "content_scripts": [{
            "matches": ["<all_urls>"],
            "js_code": """
(function(){
  const attach = (v) => {
    if (v.dataset.vscAttached) return;
    v.dataset.vscAttached = '1';
    v.playbackRate = 1.0;
    const hud = document.createElement('div');
    hud.style.cssText='position:absolute;top:8px;left:8px;background:rgba(0,0,0,.65);'+
      'color:#fff;padding:3px 10px;border-radius:4px;font:bold 13px monospace;'+
      'z-index:2147483647;pointer-events:all;cursor:default;';
    hud.textContent='1.00×';
    const wrap = v.parentElement;
    if (wrap){ wrap.style.position='relative'; wrap.appendChild(hud); }
    const update = () => { hud.textContent=v.playbackRate.toFixed(2)+'×'; };
    hud.addEventListener('wheel', e => {
      e.preventDefault();
      v.playbackRate = Math.max(0.25, Math.min(4, v.playbackRate + (e.deltaY<0?.25:-.25)));
      update();
    });
    hud.title='Scroll to change speed';
  };
  const scanVideos = () => document.querySelectorAll('video').forEach(attach);
  scanVideos();
  new MutationObserver(scanVideos).observe(document,{childList:true,subtree:true});
})();
"""
        }]
    },
    {
        "id":          "reader-mode",
        "name":        "Reader Mode",
        "version":     "1.0.0",
        "description": "Strips clutter from articles and renders clean, readable text.",
        "icon":        "📖",
        "permissions": ["tabs", "activeTab"],
        "content_scripts": [{
            "matches": ["<all_urls>"],
            "js_code": """
(function(){
  // Inject a floating "Reader" button
  if (document.getElementById('__reader_btn__')) return;
  const btn = document.createElement('button');
  btn.id = '__reader_btn__';
  btn.textContent = '📖';
  btn.title = 'Toggle Reader Mode';
  btn.style.cssText='position:fixed;bottom:60px;right:14px;width:42px;height:42px;'+
    'border-radius:50%;border:none;background:#4F8EF7;color:#fff;font-size:20px;'+
    'cursor:pointer;z-index:2147483647;box-shadow:0 2px 8px rgba(0,0,0,.4);';
  let active=false, orig=null;
  btn.onclick=()=>{
    if(!active){
      orig=document.body.innerHTML;
      const art=document.querySelector('article, main, [role=main], .post-content, .article-body');
      const src=art||document.body;
      const text=src.innerText.replace(/\\n{3,}/g,'\\n\\n');
      document.body.innerHTML='<div style="max-width:720px;margin:40px auto;font:18px/1.7 Georgia,serif;'+
        'color:#222;padding:0 20px;background:#faf9f7;min-height:100vh;"><h2 style="color:#333">Reader Mode</h2>'+
        '<pre style="white-space:pre-wrap;font:inherit">'+text+'</pre></div>';
      document.body.appendChild(btn);
      active=true; btn.title='Exit Reader Mode';
    } else {
      document.body.innerHTML=orig; document.body.appendChild(btn); active=false;
      btn.title='Toggle Reader Mode';
    }
  };
  (document.body||document.documentElement).appendChild(btn);
})();
"""
        }]
    },
    {
        "id":          "json-formatter",
        "name":        "JSON Formatter",
        "version":     "0.6.0",
        "description": "Automatically formats raw JSON responses into a collapsible tree view.",
        "icon":        "{}",
        "permissions": ["tabs"],
        "content_scripts": [{
            "matches": ["<all_urls>"],
            "js_code": """
(function(){
  try {
    const pre = document.querySelector('body > pre');
    if (!pre) return;
    const raw = pre.textContent.trim();
    if (!raw.startsWith('{') && !raw.startsWith('[')) return;
    const data = JSON.parse(raw);
    const fmt = JSON.stringify(data, null, 2)
      .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
      .replace(/"(\\w+)":/g,'<span style="color:#e06c75">"$1"</span>:')
      .replace(/: "([^"]*)"/g,': <span style="color:#98c379">"$1"</span>')
      .replace(/: (\\d+\\.?\\d*)/g,': <span style="color:#d19a66">$1</span>')
      .replace(/: (true|false)/g,': <span style="color:#56b6c2">$1</span>');
    document.body.style.background='#282c34';
    pre.style.cssText='color:#abb2bf;font:14px monospace;white-space:pre-wrap;padding:20px;';
    pre.innerHTML=fmt;
    console.log('[JSON Formatter] Formatted.');
  } catch(e){}
})();
"""
        }]
    },
]


# ══════════════════════════════════════════════════════════════════════════════
class Extension:
    """Represents a single loaded extension."""

    def __init__(self, ext_id: str, manifest: dict, ext_dir: Optional[str] = None,
                 is_builtin: bool = False):
        self.id          = ext_id
        self.name        = manifest.get("name", ext_id)
        self.version     = manifest.get("version", "0.0.0")
        self.description = manifest.get("description", "")
        self.icon        = manifest.get("icon", "🧩")
        self.permissions = manifest.get("permissions", [])
        self.enabled     = manifest.get("enabled", True)
        self.is_builtin  = is_builtin
        self.ext_dir     = ext_dir
        self._content_script_defs: List[Dict] = manifest.get("content_scripts", [])

    # ── Public helpers ─────────────────────────────────────────────────────────
    def get_qwebengine_scripts(self) -> List[QWebEngineScript]:
        """Return QWebEngineScript objects for every content-script entry."""
        scripts = []
        if not self.enabled:
            return scripts

        for i, cs_def in enumerate(self._content_script_defs):
            code = self._resolve_js_code(cs_def)
            if not code:
                continue
            script = QWebEngineScript()
            script.setName(f"_ext_{self.id}_{i}")
            script.setSourceCode(code)
            script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
            script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
            script.setRunsOnSubFrames(False)
            scripts.append(script)

        return scripts

    def _resolve_js_code(self, cs_def: dict) -> str:
        """Return the JS source — inline or from disk file."""
        # Inline (catalogue-injected)
        if "js_code" in cs_def:
            return cs_def["js_code"]

        # Disk-based (real extension folder)
        js_code = ""
        if self.ext_dir:
            for js_file in cs_def.get("js", []):
                full = os.path.join(self.ext_dir, js_file)
                if os.path.isfile(full):
                    with open(full, encoding="utf-8", errors="replace") as f:
                        js_code += f.read() + "\n"
        return js_code

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "name":        self.name,
            "version":     self.version,
            "description": self.description,
            "icon":        self.icon,
            "permissions": self.permissions,
            "enabled":     self.enabled,
            "is_builtin":  self.is_builtin,
            "content_scripts": self._content_script_defs,
        }


# ══════════════════════════════════════════════════════════════════════════════
class ExtensionManager:
    """
    Singleton-style manager for browser extensions.

    Usage
    -----
    mgr = ExtensionManager()
    mgr.inject_into_profile(profile)   # call once per QWebEngineProfile
    """

    def __init__(self):
        _ensure_dirs()
        self._extensions: Dict[str, Extension] = {}
        self._registry: Dict[str, dict] = self._load_registry()
        self._load_all()

    # ── Registry (persistence) ─────────────────────────────────────────────────
    def _load_registry(self) -> dict:
        reg_path = get_registry_path()
        if os.path.isfile(reg_path):
            try:
                with open(reg_path, encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_registry(self):
        data = {ext_id: ext.to_dict() for ext_id, ext in self._extensions.items()}
        with open(get_registry_path(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # ── Load ───────────────────────────────────────────────────────────────────
    def _load_all(self):
        """Load installed extensions from registry + rescan disk."""
        # 1. Load from saved registry (remembers enabled/disabled state)
        for ext_id, data in self._registry.items():
            ext = Extension(ext_id, data,
                            ext_dir=data.get("ext_dir"),
                            is_builtin=data.get("is_builtin", False))
            self._extensions[ext_id] = ext

        # 2. Scan extensions folder for any new folders with manifest.json
        ext_dir = get_extensions_dir()
        for name in os.listdir(ext_dir):
            folder = os.path.join(ext_dir, name)
            manifest_path = os.path.join(folder, "manifest.json")
            if os.path.isdir(folder) and os.path.isfile(manifest_path):
                if name not in self._extensions:
                    try:
                        with open(manifest_path, encoding="utf-8") as f:
                            manifest = json.load(f)
                        ext = Extension(name, manifest, ext_dir=folder)
                        self._extensions[name] = ext
                    except Exception:
                        pass

    # ── Public API ─────────────────────────────────────────────────────────────
    @property
    def extensions(self) -> List[Extension]:
        return list(self._extensions.values())

    def get(self, ext_id: str) -> Optional[Extension]:
        return self._extensions.get(ext_id)

    def install_from_catalogue(self, ext_id: str) -> Extension:
        """Install a built-in catalogue extension."""
        for item in CATALOGUE:
            if item["id"] == ext_id:
                item_copy = dict(item)
                item_copy["enabled"] = True
                item_copy["is_builtin"] = True
                ext = Extension(ext_id, item_copy, is_builtin=True)
                self._extensions[ext_id] = ext
                self._save_registry()
                return ext
        raise ValueError(f"Extension '{ext_id}' not found in catalogue")

    def install_from_zip(self, zip_path: str) -> Extension:
        """Install from a .zip file (e.g. a downloaded Chrome extension .crx renamed)."""
        _ensure_dirs()
        with zipfile.ZipFile(zip_path, "r") as zf:
            # Read manifest first
            manifest_str = zf.read("manifest.json").decode("utf-8")
            manifest = json.loads(manifest_str)
            ext_id = manifest.get("name", os.path.splitext(os.path.basename(zip_path))[0])
            ext_id = ext_id.lower().replace(" ", "-")
            target_dir = os.path.join(get_extensions_dir(), ext_id)
            os.makedirs(target_dir, exist_ok=True)
            zf.extractall(target_dir)

        ext = Extension(ext_id, manifest, ext_dir=target_dir)
        self._extensions[ext_id] = ext
        self._save_registry()
        return ext

    def install_from_folder(self, folder_path: str) -> Extension:
        """Install from an unpacked extension folder."""
        manifest_path = os.path.join(folder_path, "manifest.json")
        if not os.path.isfile(manifest_path):
            raise FileNotFoundError("manifest.json not found in folder")
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        ext_id = manifest.get("name", os.path.basename(folder_path))
        ext_id = ext_id.lower().replace(" ", "-")
        target_dir = os.path.join(get_extensions_dir(), ext_id)
        if os.path.abspath(folder_path) != os.path.abspath(target_dir):
            shutil.copytree(folder_path, target_dir, dirs_exist_ok=True)
        ext = Extension(ext_id, manifest, ext_dir=target_dir)
        self._extensions[ext_id] = ext
        self._save_registry()
        return ext

    def uninstall(self, ext_id: str):
        ext = self._extensions.pop(ext_id, None)
        if ext and ext.ext_dir and os.path.isdir(ext.ext_dir) and not ext.is_builtin:
            shutil.rmtree(ext.ext_dir, ignore_errors=True)
        self._save_registry()

    def enable(self, ext_id: str):
        if ext_id in self._extensions:
            self._extensions[ext_id].enabled = True
            self._save_registry()

    def disable(self, ext_id: str):
        if ext_id in self._extensions:
            self._extensions[ext_id].enabled = False
            self._save_registry()

    # ── Profile injection ──────────────────────────────────────────────────────
    def inject_into_profile(self, profile):
        """
        Injects all enabled extension scripts into a QWebEngineProfile.
        Call this once per profile (standard + incognito) at startup,
        and again whenever an extension is toggled/installed.
        """
        # Remove previously injected extension scripts
        scripts_col = profile.scripts()
        for script in list(scripts_col.toList()):
            if script.name().startswith("_ext_"):
                scripts_col.remove(script)

        # Inject currently enabled ones
        for ext in self._extensions.values():
            for qs in ext.get_qwebengine_scripts():
                scripts_col.insert(qs)

    def catalogue_entries(self) -> List[Dict]:
        """Returns all catalogue entries, marking which are installed."""
        result = []
        for item in CATALOGUE:
            entry = dict(item)
            entry["installed"] = item["id"] in self._extensions
            entry["enabled"] = self._extensions[item["id"]].enabled if item["id"] in self._extensions else False
            result.append(entry)
        return result
