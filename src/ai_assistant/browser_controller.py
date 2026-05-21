import re
from PyQt6.QtCore import QUrl

class BrowserController:
    def __init__(self, browser_window):
        self.browser_window = browser_window

    def parse_and_execute(self, user_query: str, page_context: dict) -> str:
        """Parse natural language command and execute browser action"""
        query_lower = user_query.lower().strip()
        
        # open_website
        match_open = re.match(r'^(open|go to|visit|navigate to)\s+(.+)', query_lower)
        if match_open:
            target = match_open.group(2).strip()
            # simple url formatting
            url = target if "." in target and not " " in target else target
            if not url.startswith("http"):
                url = f"https://{url}" if "." in url else f"https://www.google.com/search?q={url}"
            self.browser_window.tabs.current_browser().setUrl(QUrl(url))
            return f"Opened {url}"

        # search_web
        match_search = re.match(r'^(search for|search|find|look up|google)\s+(.+)', query_lower)
        if match_search:
            query = match_search.group(2).strip()
            url = f"https://www.google.com/search?q={query}"
            self.browser_window.tabs.current_browser().setUrl(QUrl(url))
            return f"Searching for '{query}'"

        # close_tab
        if query_lower in ["close tab", "close this", "close current"]:
            self.browser_window.tabs.close_current_tab()
            return "Closed current tab"

        # new_tab
        if query_lower in ["new tab", "open tab"]:
            self.browser_window.tabs.add_new_tab(QUrl("https://google.com"), "New Tab")
            return "Opened new tab"

        # get_links
        if query_lower in ["get links", "show links", "list links", "all links"]:
            links = page_context.get("links", [])
            if not links:
                return "No links found on this page."
            formatted_links = "\n".join([f"- [{link.get('text', 'Link')}]({link.get('url', '')})" for link in links[:10]])
            return f"Top links on this page:\n{formatted_links}"

        # summarize
        if query_lower in ["summarize", "summary", "what is this page", "explain this page"]:
            text = page_context.get("text", "")
            if not text:
                return "No content to summarize."
            return text[:2000]

        # scroll
        if query_lower in ["scroll down"]:
            self.browser_window.tabs.current_browser().page().runJavaScript("window.scrollBy(0, 500);")
            return "Scrolled down"
            
        if query_lower in ["scroll up"]:
            self.browser_window.tabs.current_browser().page().runJavaScript("window.scrollBy(0, -500);")
            return "Scrolled up"

        # go_back
        if query_lower in ["go back", "previous page", "back"]:
            self.browser_window.tabs.current_browser().back()
            return "Went back"

        # go_forward
        if query_lower in ["go forward", "next page", "forward"]:
            self.browser_window.tabs.current_browser().forward()
            return "Went forward"
            
        return ""

    def execute_ai_tags(self, ai_response: str):
        """Execute tags like [OPEN: url], [SEARCH: query] embedded in AI responses."""
        open_match = re.search(r'\[OPEN:\s*(.+?)\]', ai_response)
        if open_match:
            url = open_match.group(1).strip()
            if not url.startswith("http"):
                url = f"https://{url}"
            self.browser_window.tabs.current_browser().setUrl(QUrl(url))
            
        search_match = re.search(r'\[SEARCH:\s*(.+?)\]', ai_response)
        if search_match:
            query = search_match.group(1).strip()
            url = f"https://www.google.com/search?q={query}"
            self.browser_window.tabs.current_browser().setUrl(QUrl(url))
            
        if "[CLOSE TAB]" in ai_response:
            self.browser_window.tabs.close_current_tab()
            
        if "[NEW TAB]" in ai_response:
            self.browser_window.tabs.add_new_tab(QUrl("https://google.com"), "New Tab")
            
        if "[SCROLL DOWN]" in ai_response:
            self.browser_window.tabs.current_browser().page().runJavaScript("window.scrollBy(0, 500);")

    def get_page_context(self) -> dict:
        # Simplistic sync context getter
        # Ideally, this should wait for JS callbacks or use PageReader
        browser = self.browser_window.tabs.current_browser()
        url = browser.url().toString()
        title = browser.title()
        
        # We can use the existing ai_agent.page_reader if we want, but since this runs async and requires a callback, 
        # for a simplistic blocking get_page_context we might return what we have right now
        return {
            "url": url,
            "title": title,
            "text": "Page content extraction pending...", # JS injection required for real text
            "links": [] 
        }
