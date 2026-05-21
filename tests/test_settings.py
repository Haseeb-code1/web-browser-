import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.settings_manager import SettingsManager

@pytest.fixture
def settings_manager(tmpdir):
    manager = SettingsManager()
    manager.FILE_PATH = os.path.join(tmpdir, "settings.json")
    manager.settings = manager.DEFAULT_SETTINGS.copy()
    return manager

def test_default_homepage(settings_manager):
    assert settings_manager.get_setting("homepage") == "https://www.google.com"

def test_save_load(settings_manager):
    settings_manager.set_setting("homepage", "https://duckduckgo.com")
    
    # Create a new instance to simulate reload
    new_manager = SettingsManager()
    new_manager.FILE_PATH = settings_manager.FILE_PATH
    new_manager.settings = new_manager.load_settings()
    
    assert new_manager.get_setting("homepage") == "https://duckduckgo.com"
