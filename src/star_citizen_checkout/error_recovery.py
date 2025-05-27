"""Error recovery and handling system with progressive recovery strategies."""

from enum import Enum, auto
from typing import Optional, Dict, Any, Callable
import time
import logging
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
)

# Configure logging
logger = logging.getLogger(__name__)

class RecoveryLevel(Enum):
    """Progressive recovery levels for error handling."""
    WAIT_RETRY = auto()      # Level 1: Wait and retry (5s)
    REFRESH_RETRY = auto()   # Level 2: Refresh page and retry (15s)
    RESTART_RETRY = auto()   # Level 3: Restart browser and retry (30s)
    USER_INTERVENTION = auto()  # Level 4: Alert user and pause

class ErrorClassification(Enum):
    """Classification of error types for appropriate handling."""
    TEMPORARY = auto()  # Temporary errors that may resolve with retry
    STRUCTURAL = auto() # Page structure/element errors
    NETWORK = auto()    # Network-related errors
    FATAL = auto()      # Errors requiring user intervention

class ErrorRecoveryManager:
    """Manages error recovery with progressive strategies."""

    # Error classification mappings
    ERROR_CLASSIFICATIONS = {
        TimeoutException: ErrorClassification.NETWORK,
        NoSuchElementException: ErrorClassification.STRUCTURAL,
        ElementClickInterceptedException: ErrorClassification.TEMPORARY,
        StaleElementReferenceException: ErrorClassification.TEMPORARY,
        WebDriverException: ErrorClassification.NETWORK,
    }

    # Recovery delays (in seconds) for each level
    RECOVERY_DELAYS = {
        RecoveryLevel.WAIT_RETRY: 5,
        RecoveryLevel.REFRESH_RETRY: 15,
        RecoveryLevel.RESTART_RETRY: 30,
    }

    def __init__(self, driver: WebDriver, restart_callback: Optional[Callable] = None):
        """Initialize the recovery manager.
        
        Args:
            driver: Selenium WebDriver instance
            restart_callback: Optional callback for browser restart
        """
        self.driver = driver
        self.restart_callback = restart_callback
        self.recovery_attempts = {level: 0 for level in RecoveryLevel}
        self.error_counts: Dict[ErrorClassification, int] = {
            classification: 0 for classification in ErrorClassification
        }
        self.recovery_start_time = 0.0
        self.current_level = RecoveryLevel.WAIT_RETRY

    def classify_error(self, error: Exception) -> ErrorClassification:
        """Classify an error for appropriate handling."""
        error_type = type(error)
        return self.ERROR_CLASSIFICATIONS.get(error_type, ErrorClassification.FATAL)

    def should_escalate(self) -> bool:
        """Determine if recovery should escalate to next level."""
        MAX_ATTEMPTS = {
            RecoveryLevel.WAIT_RETRY: 3,
            RecoveryLevel.REFRESH_RETRY: 2,
            RecoveryLevel.RESTART_RETRY: 1,
        }
        return (self.current_level in MAX_ATTEMPTS and 
                self.recovery_attempts[self.current_level] >= MAX_ATTEMPTS[self.current_level])

    def execute_recovery(self, error: Exception) -> bool:
        """Execute recovery strategy for the given error.
        
        Args:
            error: The exception that triggered recovery
            
        Returns:
            bool: True if recovery was successful
            
        Raises:
            Exception: If recovery escalates to user intervention
        """
        if not self.recovery_start_time:
            self.recovery_start_time = time.time()

        error_class = self.classify_error(error)
        self.error_counts[error_class] += 1

        # Log detailed error information
        logger.error(
            "Error encountered during checkout",
            extra={
                "error_type": error.__class__.__name__,
                "error_message": str(error),
                "classification": error_class.name,
                "recovery_level": self.current_level.name,
                "attempt": self.recovery_attempts[self.current_level] + 1,
                "time_in_recovery": time.time() - self.recovery_start_time
            }
        )

        success = False
        
        try:
            # Execute recovery based on current level
            if self.current_level == RecoveryLevel.WAIT_RETRY:
                time.sleep(self.RECOVERY_DELAYS[RecoveryLevel.WAIT_RETRY])
                success = True

            elif self.current_level == RecoveryLevel.REFRESH_RETRY:
                time.sleep(self.RECOVERY_DELAYS[RecoveryLevel.REFRESH_RETRY])
                self.driver.refresh()
                success = True

            elif self.current_level == RecoveryLevel.RESTART_RETRY:
                time.sleep(self.RECOVERY_DELAYS[RecoveryLevel.RESTART_RETRY])
                if self.restart_callback:
                    self.restart_callback()
                    success = True

            elif self.current_level == RecoveryLevel.USER_INTERVENTION:
                msg = "Recovery escalated to user intervention. "
                msg += f"Error counts: {self.error_counts}, "
                msg += f"Time in recovery: {time.time() - self.recovery_start_time:.1f}s"
                raise Exception(msg)

        finally:
            self.recovery_attempts[self.current_level] += 1
            
            # Check if we should escalate to next level
            if self.should_escalate():
                next_levels = list(RecoveryLevel)
                current_idx = next_levels.index(self.current_level)
                if current_idx + 1 < len(next_levels):
                    self.current_level = next_levels[current_idx + 1]
                    logger.warning(
                        f"Escalating recovery to {self.current_level.name}",
                        extra={"error_counts": self.error_counts}
                    )
        
        return success

    def reset(self):
        """Reset recovery state for new attempts."""
        self.recovery_attempts = {level: 0 for level in RecoveryLevel}
        self.error_counts = {classification: 0 for classification in ErrorClassification}
        self.recovery_start_time = 0.0
        self.current_level = RecoveryLevel.WAIT_RETRY
