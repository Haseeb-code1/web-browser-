import sys
import os
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.bookmarks import BookmarksManager

@pytest.fixture
def bm_manager(tmpdir):
    # Patch the FILE_PATH to use a temp directory
    manager = BookmarksManager()
    manager.FILE_PATH = os.path.join(tmpdir, "bookmarks.json")
    manager.bookmarks = []
    return manager

def test_add_bookmark(bm_manager):
    bm_manager.add_bookmark("https://google.com", "Google")
    bms = bm_manager.get_bookmarks()
    assert len(bms) == 1
    assert bms[0].url == "https://google.com"
    assert bms[0].title == "Google"

def test_remove_bookmark(bm_manager):
    bm_manager.add_bookmark("https://google.com", "Google")
    bm_manager.remove_bookmark("https://google.com")
    assert len(bm_manager.get_bookmarks()) == 0

def test_duplicate_bookmark(bm_manager):
    bm_manager.add_bookmark("https://google.com", "Google")
    bm_manager.add_bookmark("https://google.com", "Google Again")
    assert len(bm_manager.get_bookmarks()) == 1
