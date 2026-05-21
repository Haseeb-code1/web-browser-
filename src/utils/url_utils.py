import re
from urllib.parse import urlparse

def is_valid_url(url: str) -> bool:
    """
    Checks if a given string is a valid URL.
    
    Args:
        url: The string to check.
        
    Returns:
        True if the string is a valid URL, False otherwise.
    """
    # A simple regex for URL validation
    pattern = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' # domain...
        r'localhost|' # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    if not url.startswith(('http://', 'https://', 'ftp://')):
        # Check if it would be a valid URL with https:// added
        return re.match(pattern, f"https://{url}") is not None
    return re.match(pattern, url) is not None

def format_url(url: str) -> str:
    """
    Formats a URL by adding https:// if it's missing a scheme.
    
    Args:
        url: The raw URL string.
        
    Returns:
        The formatted URL string.
    """
    if not url.strip():
        return url
        
    parsed = urlparse(url)
    if not parsed.scheme:
        if '.' in url or url == 'localhost':
            return f"https://{url}"
        else:
            # It's likely a search query
            return url
    return url

def get_search_url(query: str, search_engine: str = "https://www.google.com/search?q=") -> str:
    """
    Creates a search URL from a query string.
    
    Args:
        query: The search terms.
        search_engine: The base search engine URL.
        
    Returns:
        The full search URL.
    """
    from urllib.parse import quote_plus
    return f"{search_engine}{quote_plus(query)}"
