import os
import time
from PyQt6.QtWebEngineCore import QWebEngineDownloadRequest
from PyQt6.QtCore import Qt

from src.utils.exception_logger import log_exception

class DownloadManager:
    """Manages browser downloads with progress dialogs."""
    
    
    def __init__(self, parent_widget):
        self.parent = parent_widget
        self.downloads_history = []
        self.active_downloads = {}

    def handle_download(self, download: QWebEngineDownloadRequest) -> None:
        """
        Handles a download request from the web engine.
        
        Args:
            download: The download request object.
        """
        try:
            # Let the user choose the save location
            # Note: For a robust implementation, you might want a QFileDialog
            # but QWebEngineDownloadRequest handles path suggestion.
            # We'll just accept it and show progress.
            
            # download.setDownloadDirectory(...) # Could set dir here
            download.accept()
            
            dl_id = download.id()
            self.active_downloads[dl_id] = {
                "request": download,
                "filename": download.downloadFileName(),
                "received": 0,
                "total": download.totalBytes(),
                "speed_bps": 0,
                "last_bytes": 0,
                "last_time": time.time()
            }
            
            if hasattr(self.parent, "main_window"):
                self.parent.main_window.status.showMessage(f"Started downloading: {download.downloadFileName()}", 3000)
            
            # Connect signals
            download.receivedBytesChanged.connect(
                lambda: self._update_progress(download)
            )
            
            download.stateChanged.connect(
                lambda state: self._handle_state_change(state, download)
            )
            
        except Exception as e:
            log_exception(e)
            if hasattr(self.parent, "main_window"):
                self.parent.main_window.status.showMessage("Download Error!", 3000)

    def _update_progress(self, download: QWebEngineDownloadRequest) -> None:
        """Updates internal state and calculates speed silently."""
        dl_id = download.id()
        if dl_id not in self.active_downloads: return
        
        info = self.active_downloads[dl_id]
        received = download.receivedBytes()
        total = download.totalBytes()
        
        curr_time = time.time()
        elapsed = curr_time - info["last_time"]
        if elapsed > 0.5:
            speed = (received - info["last_bytes"]) / elapsed
            info["speed_bps"] = speed
            info["last_bytes"] = received
            info["last_time"] = curr_time
            
        info["received"] = received
        info["total"] = total
        
    def _handle_state_change(self, state: QWebEngineDownloadRequest.DownloadState, download: QWebEngineDownloadRequest) -> None:
        """Handles download state changes."""
        dl_id = download.id()
        filename = download.downloadFileName()
        
        if state == QWebEngineDownloadRequest.DownloadState.DownloadCompleted:
            self.downloads_history.append(f"Completed: {filename}")
            if dl_id in self.active_downloads: del self.active_downloads[dl_id]
            if hasattr(self.parent, "main_window"):
                self.parent.main_window.status.showMessage(f"Download Complete: {filename}", 5000)
            
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadCancelled:
            self.downloads_history.append(f"Cancelled: {filename}")
            if dl_id in self.active_downloads: del self.active_downloads[dl_id]
            
        elif state == QWebEngineDownloadRequest.DownloadState.DownloadInterrupted:
            self.downloads_history.append(f"Failed: {filename}")
            if dl_id in self.active_downloads: del self.active_downloads[dl_id]
            if hasattr(self.parent, "main_window"):
                self.parent.main_window.status.showMessage(f"Download Failed: {filename}", 5000)

    def pause_download(self, dl_id):
        if dl_id in self.active_downloads:
            self.active_downloads[dl_id]["request"].pause()
            
    def resume_download(self, dl_id):
        if dl_id in self.active_downloads:
            self.active_downloads[dl_id]["request"].resume()
            
    def cancel_download(self, dl_id):
        if dl_id in self.active_downloads:
            self.active_downloads[dl_id]["request"].cancel()
            
    def delete_history(self, index):
        if 0 <= index < len(self.downloads_history):
            self.downloads_history.pop(index)
