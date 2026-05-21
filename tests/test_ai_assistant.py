import pytest
from unittest.mock import Mock, patch
from src.ai_assistant.model_router import ModelRouter
from src.ai_assistant.groq_client import GroqClient, GroqNotConfiguredError
from src.ai_assistant.ollama_client import OllamaClient
from src.ai_assistant.browser_controller import BrowserController
from src.ai_assistant.selection_watcher import SelectionWatcher
from PyQt6.QtCore import QUrl

def test_model_router_selects_groq():
    gc = Mock()
    gc.stream.return_value = iter(["res"])
    oc = Mock()
    router = ModelRouter(gc, oc)
    router.set_model("groq")
    list(router.ask("test"))
    gc.stream.assert_called_once()
    oc.stream.assert_not_called()

def test_model_router_selects_phi3():
    gc = Mock()
    oc = Mock()
    oc.stream.return_value = iter(["res"])
    router = ModelRouter(gc, oc)
    router.set_model("phi3")
    list(router.ask("test"))
    oc.stream.assert_called_once()
    gc.stream.assert_not_called()

def test_model_router_auto_phi3_available():
    gc = Mock()
    oc = Mock()
    oc.check_running.return_value = True
    oc.stream.return_value = iter(["res"])
    router = ModelRouter(gc, oc)
    router.set_model("auto")
    list(router.ask("test"))
    oc.stream.assert_called_once()
    gc.stream.assert_not_called()

def test_model_router_auto_fallback():
    gc = Mock()
    gc.stream.return_value = iter(["res"])
    oc = Mock()
    oc.check_running.return_value = False
    router = ModelRouter(gc, oc)
    router.set_model("auto")
    list(router.ask("test"))
    gc.stream.assert_called_once()
    oc.stream.assert_not_called()

def test_groq_no_key_raises():
    client = GroqClient(api_key="")
    client.api_key = ""
    with pytest.raises(GroqNotConfiguredError):
        list(client.stream("test"))

def test_browser_controller_open_intent():
    bw = Mock()
    bc = BrowserController(bw)
    res = bc.parse_and_execute("open google.com", {})
    assert "Opened" in res
    bw.tabs.current_browser().setUrl.assert_called_once()

def test_browser_controller_search_intent():
    bw = Mock()
    bc = BrowserController(bw)
    res = bc.parse_and_execute("search for cats", {})
    assert "Searching" in res
    bw.tabs.current_browser().setUrl.assert_called_once()

def test_browser_controller_close_intent():
    bw = Mock()
    bc = BrowserController(bw)
    res = bc.parse_and_execute("close tab", {})
    assert "Closed" in res
    bw.tabs.close_current_tab.assert_called_once()
