from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

class SelectionWatcher(QObject):
    selection_changed = pyqtSignal(str)
    
    def start_watching(self, web_view):
        # Disconnect previous to avoid multiple signals if called repeatedly
        try:
            web_view.selectionChanged.disconnect()
        except TypeError:
            pass
        web_view.selectionChanged.connect(lambda: self._handle_selection(web_view))
        
    def _handle_selection(self, web_view):
        web_view.page().runJavaScript("window.getSelection().toString()", self._on_js_result)
        
    def _on_js_result(self, text):
        if text and len(text.strip()) > 2:
            QApplication.clipboard().setText(text.strip())
            self.selection_changed.emit(text.strip())

    def inject_selection_script(self, web_view):
        script = """
        document.addEventListener('mouseup', function() {
            var sel = window.getSelection().toString().trim();
            if (sel.length > 2) {
                // Qt will read this via selectionChanged signal
                document.title = document.title; // trigger refresh
            }
        });
        """
        web_view.page().runJavaScript(script)
