import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.url_utils import is_valid_url, format_url

def test_valid_url():
    assert is_valid_url("https://google.com") == True
    assert is_valid_url("http://example.org") == True

def test_invalid_url():
    assert is_valid_url("not a url") == False
    assert is_valid_url("hello world") == False

def test_prefix_added():
    assert format_url("google.com") == "https://google.com"
    assert format_url("localhost") == "https://localhost"
    assert format_url("https://google.com") == "https://google.com"
