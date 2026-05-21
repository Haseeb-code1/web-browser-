import json
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QEventLoop

class PageReader:
    def __init__(self, web_view: QWebEngineView):
        self.web_view = web_view

    def get_page_context(self, callback):
        js = """
        (function() {
            try {
                function isVisible(el) {
                    return el.offsetParent !== null;
                }
                
                let text = document.body ? document.body.innerText.replace(/\\s+/g, ' ').substring(0, 1000) : '';
                
                let links = [];
                document.querySelectorAll('a').forEach(a => {
                    if (links.length >= 20) return; // Limit to 20 links to save context
                    if (isVisible(a) && a.innerText.trim().length > 2) {
                        links.push({text: a.innerText.trim().substring(0,50), href: a.href});
                    }
                });
                
                let forms = [];
                document.querySelectorAll('form').forEach(f => {
                    if (forms.length >= 3) return; // Limit forms
                    if (isVisible(f)) {
                        let fields = [];
                        f.querySelectorAll('input, select, textarea').forEach(input => {
                            if (isVisible(input) && input.type !== 'hidden') {
                                fields.push({
                                    name: input.name || input.id || '',
                                    type: input.type,
                                    placeholder: input.placeholder || '',
                                    value: input.value || ''
                                });
                            }
                        });
                        forms.push({
                            id: f.id || '',
                            fields: fields,
                            submit_button: 'submit'
                        });
                    }
                });
                
                let buttons = [];
                document.querySelectorAll('button').forEach(b => {
                    if (buttons.length >= 10) return; // Limit to 10 buttons
                    if (isVisible(b) && b.innerText.trim().length > 2) {
                        buttons.push({text: b.innerText.trim().substring(0,30)});
                    }
                });
                
                return JSON.stringify({
                    url: window.location.href,
                    title: document.title,
                    text: text,
                    links: links,
                    forms: forms,
                    buttons: buttons
                });
            } catch (e) {
                return JSON.stringify({error: e.toString()});
            }
        })();
        """
        self.web_view.page().runJavaScript(js, callback)

    def get_page_context_sync(self):
        loop = QEventLoop()
        result_data = {}
        def callback(res):
            result_data['data'] = res
            loop.quit()
        self.get_page_context(callback)
        loop.exec()
        if 'data' in result_data:
            try:
                return json.loads(result_data['data'])
            except:
                return {}
        return {}
