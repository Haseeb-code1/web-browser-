import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.history import HistoryManager

@pytest.fixture
def hist_manager(tmpdir):
    manager = HistoryManager()
    manager.FILE_PATH = os.path.join(tmpdir, "history.json")
    manager.history = []
    return manager

def test_log_entry(hist_manager):
    hist_manager.log_entry("https://google.com", "Google")
    hist = hist_manager.get_history()
    assert len(hist) == 1
    assert hist[0].url == "https://google.com"

def test_history_order(hist_manager):
    hist_manager.log_entry("https://first.com", "First")
    hist_manager.log_entry("https://second.com", "Second")
    hist = hist_manager.get_history()
    assert hist[0].url == "https://second.com"
    assert hist[1].url == "https://first.com"

def test_clear_history(hist_manager):
    hist_manager.log_entry("https://first.com", "First")
    hist_manager.clear_history()
    assert len(hist_manager.get_history()) == 0
