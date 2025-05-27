import time
import random
from datetime import datetime, timedelta
from typing import Callable, Optional, TypeVar, List
from dataclasses import dataclass
from .config import RetryConfig
from .logging import get_logger
from .monitoring import MonitoringSystem

logger = get_logger(__name__)

T = TypeVar('T')

@dataclass
class RetryStats:
    """Statistics about retry attempts."""
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    last_success_time: Optional[datetime] = None
    last_failure_time: Optional[datetime] = None
    attempt_intervals: List[float] = None
    
    def __post_init__(self):
        self.attempt_intervals = []
    
    def add_interval(self, interval: float):
        """Add an interval measurement."""
        self.attempt_intervals.append(interval)
    
    @property
    def average_interval(self) -> Optional[float]:
        """Calculate average interval between attempts."""
        if not self.attempt_intervals:
            return None
        return sum(self.attempt_intervals) / len(self.attempt_intervals)

class RetryManager:
    """Manages retry logic with fixed intervals and rate limiting."""
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.stats = RetryStats()
        self._last_attempt_time: Optional[datetime] = None
        self._attempts_this_minute = 0
        self._minute_start_time: Optional[datetime] = None
        self._current_attempt: int = 0
        self.monitoring = MonitoringSystem()
        self.monitoring.update_state("initialized")
    
    def _apply_jitter(self, base_interval: float) -> float:
        """Add small random jitter to prevent thundering herd."""
        jitter = random.uniform(-0.1, 0.1) * base_interval
        return max(0.1, base_interval + jitter)
    
    def _reset_rate_limit(self):
        """Reset rate limiting counters."""
        self._attempts_this_minute = 0
        self._minute_start_time = datetime.now()
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        now = datetime.now()
        
        # Initialize or reset minute window
        if not self._minute_start_time or (now - self._minute_start_time) > timedelta(minutes=1):
            self._reset_rate_limit()
            
        # Check rate limit
        if self._attempts_this_minute >= self.config.max_attempts_per_minute:
            wait_time = 60 - (now - self._minute_start_time).total_seconds()
            if wait_time > 0:
                logger.warning(f"Rate limit reached. Waiting {wait_time:.1f}s")
                time.sleep(wait_time)
                self._reset_rate_limit()
        
        self._attempts_this_minute += 1
        return True
    
    def execute_with_retry(self, operation: Callable[[], T]) -> Optional[T]:
        """
        Execute an operation with retry logic.
        
        Args:
            operation: Function to execute that returns True on success
            
        Returns:
            The result of the operation if successful, None otherwise
        """
        start_state = "running"
        self.monitoring.update_state(start_state)
        while self.stats.total_attempts < self.config.max_retries or self.config.max_retries == 0:
            # Check rate limiting
            self._check_rate_limit()
            
            # Record attempt timing
            attempt_start = datetime.now()
            if self._last_attempt_time:
                interval = (attempt_start - self._last_attempt_time).total_seconds()
                self.stats.add_interval(interval)
            
            # Execute attempt
            try:
                self.stats.total_attempts += 1
                self._current_attempt = self.stats.total_attempts
                logger.info(f"Attempt {self._current_attempt}")
                self.monitoring.update_retry_count(self._current_attempt)
                
                result = operation()
                
                if result:
                    self.stats.successful_attempts += 1
                    self.stats.last_success_time = datetime.now()
                    attempt_duration = (datetime.now() - attempt_start).total_seconds()
                    self.monitoring.record_attempt(True, attempt_duration)
                    logger.info("Operation succeeded", 
                              total_attempts=self.stats.total_attempts,
                              successful_attempts=self.stats.successful_attempts)
                    self.monitoring.update_state("completed")
                    return result
                
                self.stats.failed_attempts += 1
                self.stats.last_failure_time = datetime.now()
                attempt_duration = (datetime.now() - attempt_start).total_seconds()
                self.monitoring.record_attempt(False, attempt_duration)
                self.monitoring.update_state("failed")
                
            except Exception as e:
                self.stats.failed_attempts += 1
                self.stats.last_failure_time = datetime.now()
                attempt_duration = (datetime.now() - attempt_start).total_seconds()
                self.monitoring.record_attempt(False, attempt_duration)
                self.monitoring.record_error(e.__class__.__name__)
                self.monitoring.update_state("error")
                logger.error(f"Attempt failed: {str(e)}")
            
            # Prepare for next attempt
            self._last_attempt_time = datetime.now()
            interval = self._apply_jitter(self.config.base_interval)
            self.monitoring.update_retry_count(self.stats.total_attempts)
            
            logger.info(f"Waiting {interval:.1f}s before next attempt")
            time.sleep(interval)
        
        logger.warning("Max retries reached", 
                      max_retries=self.config.max_retries,
                      total_attempts=self.stats.total_attempts)
        self.monitoring.update_state("stopped")
        return None
