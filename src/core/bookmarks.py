import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List

from src.utils.exception_logger import log_exception

from src.utils.paths import get_data_file_path

@dataclass
class BookmarkEntry:
    url: str
    title: str
    timestamp: str

class BookmarksManager:
    """Manages reading and writing bookmarks to a JSON file."""
    
    def __init__(self):
        self.FILE_PATH = get_data_file_path("bookmarks.json")
        self._ensure_data_dir()
        self.bookmarks: List[BookmarkEntry] = self.load_bookmarks()

    def _ensure_data_dir(self) -> None:
        """Ensures the data directory exists."""
        try:
            os.makedirs(os.path.dirname(self.FILE_PATH), exist_ok=True)
        except Exception as e:
            log_exception(e)

    def load_bookmarks(self) -> List[BookmarkEntry]:
        """Loads bookmarks from JSON."""
        if not os.path.exists(self.FILE_PATH):
            return []
        try:
            with open(self.FILE_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [BookmarkEntry(**item) for item in data]
        except Exception as e:
            log_exception(e)
            return []

    def save_bookmarks(self) -> None:
        """Saves current bookmarks to JSON."""
        try:
            with open(self.FILE_PATH, 'w', encoding='utf-8') as f:
                data = [asdict(bm) for bm in self.bookmarks]
                json.dump(data, f, indent=4)
        except Exception as e:
            log_exception(e)

    def add_bookmark(self, url: str, title: str) -> None:
        """Adds a new bookmark if it doesn't already exist."""
        if any(bm.url == url for bm in self.bookmarks):
            return
            
        timestamp = datetime.now().isoformat()
        new_bm = BookmarkEntry(url=url, title=title, timestamp=timestamp)
        self.bookmarks.append(new_bm)
        self.save_bookmarks()

    def remove_bookmark(self, url: str) -> None:
        """Removes a bookmark by URL."""
        initial_len = len(self.bookmarks)
        self.bookmarks = [bm for bm in self.bookmarks if bm.url != url]
        if len(self.bookmarks) < initial_len:
            self.save_bookmarks()

    def get_bookmarks(self) -> List[BookmarkEntry]:
        """Returns the list of bookmarks."""
        return self.bookmarks
