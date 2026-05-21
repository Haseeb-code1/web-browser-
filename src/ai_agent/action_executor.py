import json
import urllib.parse
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QEventLoop
import time

class ActionExecutor:
    def __init__(self, web_view: QWebEngineView):
        self.web_view = web_view

    def execute(self, tool_call: dict) -> str:
        tool = tool_call.get("tool")
        params = tool_call.get("params", {})
        
        if tool == "navigate_to":
            return self.navigate_to(params.get("url", ""))
        elif tool == "click_element":
            return self.click_element(params.get("text", ""))
        elif tool == "fill_field":
            return self.fill_field(params.get("field_name", ""), params.get("value", ""))
        elif tool == "submit_form":
            return self.submit_form(params.get("form_id", ""))
        elif tool == "scroll_down":
            return self.scroll_down(params.get("amount", 500))
        elif tool == "wait":
            return self.wait(params.get("seconds", 2))
        elif tool == "read_page":
            from src.ai_agent.page_reader import PageReader
            reader = PageReader(self.web_view)
            data = reader.get_page_context_sync()
            return f"Page Data: {json.dumps(data)}"
        elif tool == "answer":
            return f"Answer: {params.get('message', '')}"
        else:
            return f"Error: Unknown tool {tool}"

    def _run_js_sync(self, js: str) -> str:
        loop = QEventLoop()
        result_data = {}
        def callback(res):
            result_data['data'] = res
            loop.quit()
        self.web_view.page().runJavaScript(js, callback)
        loop.exec()
        return str(result_data.get('data', ''))

    def navigate_to(self, url: str) -> str:
        if not url: return "Error: No URL provided."
        if not (url.startswith("http://") or url.startswith("https://")):
            if "." in url and " " not in url:
                url = "https://" + url
            else:
                url = "https://www.google.com/search?q=" + urllib.parse.quote(url)
        self.web_view.load(QUrl(url))
        return f"Navigated to {url}"

    def click_element(self, text: str) -> str:
        js = f"""
        (function() {{
            let text = "{text}".toLowerCase();
            let elements = [...document.querySelectorAll('a, button')];
            for (let el of elements) {{
                if (el.innerText.toLowerCase().includes(text)) {{
                    el.click();
                    return "Clicked element containing '" + text + "'";
                }}
            }}
            return "Element not found";
        }})();
        """
        return self._run_js_sync(js)

    def fill_field(self, field_name: str, value: str) -> str:
        js = f"""
        (function() {{
            let name = "{field_name}".toLowerCase();
            let inputs = document.querySelectorAll('input, textarea');
            for (let el of inputs) {{
                if ((el.name && el.name.toLowerCase().includes(name)) || 
                    (el.id && el.id.toLowerCase().includes(name)) ||
                    (el.placeholder && el.placeholder.toLowerCase().includes(name))) {{
                    el.value = "{value}";
                    return "Filled field " + name;
                }}
            }}
            return "Field not found";
        }})();
        """
        return self._run_js_sync(js)

    def submit_form(self, form_id: str) -> str:
        js = f"""
        (function() {{
            let id = "{form_id}";
            if (id) {{
                let form = document.getElementById(id);
                if (form) {{ form.submit(); return "Submitted form " + id; }}
            }} else {{
                let form = document.querySelector('form');
                if (form) {{ form.submit(); return "Submitted first form found"; }}
            }}
            return "Form not found";
        }})();
        """
        return self._run_js_sync(js)

    def scroll_down(self, amount: int) -> str:
        js = f"window.scrollBy(0, {amount}); 'Scrolled down by {amount} pixels';"
        return self._run_js_sync(js)

    def wait(self, seconds: int) -> str:
        import time
        from PyQt6.QtWidgets import QApplication
        
        # We need a non-blocking wait to allow Qt to process events
        end = time.time() + min(seconds, 5)
        while time.time() < end:
            QApplication.processEvents()
            time.sleep(0.1)
        return f"Waited {seconds} seconds."
