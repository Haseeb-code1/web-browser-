import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

from src.utils.exception_logger import log_exception

from src.utils.paths import get_data_file_path

@dataclass
class HistoryEntry:
    url: str
    title: str
    timestamp: str

class HistoryManager:
    """Manages reading and writing browsing history to a JSON file."""
    
    def __init__(self):
        self.FILE_PATH = get_data_file_path("history.json")
        self._ensure_data_dir()
        self.history: List[HistoryEntry] = self.load_history()

    def _ensure_data_dir(self) -> None:
        """Ensures the data directory exists."""
        try:
            os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        except Exception as e:
            log_exception(e)

    def load_history(self) -> List[HistoryEntry]:
        """Loads history from JSON."""
        if not os.path.exists(self.FILE_PATH):
            return []
        try:
            with open(self.FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [HistoryEntry(**item) for item in data]
        except Exception as e:
            log_exception(e)
            return []

    def save_history(self) -> None:
        """Saves current history to JSON."""
        try:
            with open(self.FILE_PATH, 'w', encoding='utf-8') as f:
                data = [asdict(entry) for entry in self.history]
                json.dump(data, f, indent=4)
        except Exception as e:
            log_exception(e)

    def log_entry(self, url: str, title: str) -> None:
        """Logs a new visited URL."""
        if url.startswith("chrome://") or url.startswith("about:"):
            return # Ignore internal pages
            
        timestamp = datetime.now().isoformat()
        new_entry = HistoryEntry(url=url, title=title, timestamp=timestamp)
        # Add to beginning of list (most recent first)
        self.history.insert(0, new_entry)
        
        # Limit history to 1000 entries
        if len(self.history) > 1000:
            self.history = self.history[:1000]
            
        self.save_history()

    def get_history(self) -> List[HistoryEntry]:
        """Returns the list of history entries."""
        return self.history
        
    def remove_entry(self, index: int) -> None:
        """Removes a specific history entry by index."""
        if 0 <= index < len(self.history):
            self.history.pop(index)
            self.save_history()
        
    def clear_history(self) -> None:
        """Clears all history."""
        self.history = []
        self.save_history()
