"""Module for handling graceful shutdown and cleanup procedures."""

import signal
import tempfile
import os
from pathlib import Path
from typing import Optional, List, Callable, Any, Union
from selenium import webdriver
from .logging import get_logger

logger = get_logger(__name__)

class ShutdownManager:
    """Manages graceful shutdown and cleanup procedures."""
    
    def __init__(self):
        self.driver: Optional[webdriver.Remote] = None
        self.temp_files: List[str] = []  # Store as strings instead of Path objects
        self.cleanup_callbacks: List[Callable] = []
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self) -> None:
        """Set up handlers for SIGTERM and SIGINT."""
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
    
    def _handle_signal(self, signum: int, frame: Optional[Any]) -> None:
        """Handle shutdown signals."""
        sig_name = signal.Signals(signum).name
        logger.info(f"Received {sig_name} signal, initiating shutdown...")
        self.shutdown(f"Received {sig_name}")
    
    def register_browser(self, driver: webdriver.Remote) -> None:
        """Register browser instance for cleanup."""
        self.driver = driver
    
    def register_temp_file(self, file_path: Union[Path, str]) -> None:
        """Register temporary file for cleanup."""
        self.temp_files.append(str(file_path))
    
    def register_cleanup_callback(self, callback: Callable) -> None:
        """Register additional cleanup callback."""
        self.cleanup_callbacks.append(callback)
    
    def cleanup_browser(self) -> None:
        """Clean up browser session."""
        if self.driver:
            try:
                logger.info("Closing browser session...")
                self.driver.quit()
                self.driver = None
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
    
    def cleanup_temp_files(self) -> None:
        """Clean up temporary files."""
        for file_path in self.temp_files:
            try:
                path = Path(file_path)
                if path.exists():
                    logger.info(f"Removing temporary file: {file_path}")
                    path.unlink()
            except Exception as e:
                logger.error(f"Error removing temp file {file_path}: {e}")
        self.temp_files.clear()
    
    def run_cleanup_callbacks(self) -> None:
        """Run registered cleanup callbacks."""
        for callback in self.cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error in cleanup callback: {e}")
        self.cleanup_callbacks.clear()
    
    def shutdown(self, reason: str = "Shutdown requested") -> None:
        """Execute complete shutdown procedure."""
        logger.info(f"Initiating shutdown: {reason}")
        
        # Run cleanup in order
        self.cleanup_browser()
        self.cleanup_temp_files()
        self.run_cleanup_callbacks()
        
        logger.info("Shutdown complete")
