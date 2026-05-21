import json
import os
from typing import Any

from src.utils.exception_logger import log_exception

from src.utils.paths import get_data_file_path

class SettingsManager:
    """Manages browser settings."""
    
    DEFAULT_SETTINGS = {
        "homepage": "https://www.google.com",
        "search_engine": "https://www.google.com/search?q=",
        "theme": "dark"
    }

    def __init__(self):
        self.FILE_PATH = get_data_file_path("settings.json")
        self._ensure_data_dir()
        self.settings = self.load_settings()

    def _ensure_data_dir(self) -> None:
        """Ensures the data directory exists."""
        try:
            os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        except Exception as e:
            log_exception(e)

    def load_settings(self) -> dict:
        """Loads settings from JSON, filling defaults if missing."""
        if not os.path.exists(self.FILE_PATH):
            return self.DEFAULT_SETTINGS.copy()
            
        try:
            with open(self.FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Merge with defaults to ensure all keys exist
            merged = self.DEFAULT_SETTINGS.copy()
            merged.update(data)
            return merged
        except Exception as e:
            log_exception(e)
            return self.DEFAULT_SETTINGS.copy()

    def save_settings(self) -> None:
        """Saves current settings to JSON."""
        try:
            with open(self.FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            log_exception(e)

    def get_setting(self, key: str) -> Any:
        """Gets a setting value."""
        return self.settings.get(key, self.DEFAULT_SETTINGS.get(key))

    def set_setting(self, key: str, value: Any) -> None:
        """Sets a setting value and saves."""
        self.settings[key] = value
        self.save_settings()
