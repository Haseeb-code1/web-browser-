from PyQt6.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from src.utils.exception_logger import log_exception

class AdBlockerInterceptor(QWebEngineUrlRequestInterceptor):
    """Intercepts and blocks web requests to known ad and tracking domains."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_enabled = True
        # A lightweight list of common ad and tracking domains
        self.blocked_domains = [
            "doubleclick.net",
            "googleadservices.com",
            "googlesyndication.com",
            "adsystem.com",
            "adservice.google.com",
            "google-analytics.com",
            "analytics.google.com",
            "quantserve.com",
            "scorecardresearch.com",
            "zedo.com",
            "ad.yieldmanager.com",
            "amazon-adsystem.com"
        ]

    def interceptRequest(self, info):
        if not self.is_enabled:
            return
            
        try:
            url = info.requestUrl().toString()
            for domain in self.blocked_domains:
                if domain in url:
                    info.block(True)
                    # print(f"AdGuard blocked: {url}")
                    return
        except Exception as e:
            log_exception(e)
