from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import json
import logging
import os
from pathlib import Path
import time

@dataclass
class MetricsData:
    """Stores monitoring metrics data."""
    start_time: datetime = field(default_factory=datetime.now)
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    response_times: List[float] = field(default_factory=list)
    error_counts: Dict[str, int] = field(default_factory=dict)
    current_state: str = "stopped"
    last_attempt_result: Optional[str] = None
    current_retry_count: int = 0

    def record_error(self, error_type: str) -> None:
        """Record an error occurrence."""
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1

class MonitoringSystem:
    """Manages monitoring, metrics collection, and status reporting."""
    
    def __init__(self, metrics_file: str = "checkout_metrics.json"):
        self.logger = logging.getLogger(__name__)
        self.metrics = MetricsData()
        self.metrics_file = metrics_file
        self._ensure_metrics_file()

    def _ensure_metrics_file(self) -> None:
        """Create metrics file if it doesn't exist."""
        if not os.path.exists(self.metrics_file):
            self.save_metrics()

    def record_attempt(self, success: bool, response_time: float) -> None:
        """Record an attempt with its outcome and response time."""
        self.metrics.total_attempts += 1
        if success:
            self.metrics.successful_attempts += 1
            self.metrics.last_attempt_result = "success"
        else:
            self.metrics.failed_attempts += 1
            self.metrics.last_attempt_result = "failure"
        
        self.metrics.response_times.append(response_time)
        self.save_metrics()
        self._notify_status()

    def record_error(self, error_type: str) -> None:
        """Record an error occurrence."""
        self.metrics.record_error(error_type)
        self.save_metrics()

    def update_state(self, state: str) -> None:
        """Update the current state of the bot."""
        self.metrics.current_state = state
        self._notify_status()
        self.save_metrics()

    def update_retry_count(self, count: int) -> None:
        """Update the current retry count."""
        self.metrics.current_retry_count = count
        self._notify_status()
        self.save_metrics()

    def _notify_status(self) -> None:
        """Display current status in console."""
        status_msg = (
            f"\nStatus: {self.metrics.current_state.upper()}\n"
            f"Last attempt: {self.metrics.last_attempt_result or 'N/A'}\n"
            f"Current retry: {self.metrics.current_retry_count}\n"
            f"Success rate: {self._calculate_success_rate():.1f}%\n"
        )
        self.logger.info(status_msg)

    def _calculate_success_rate(self) -> float:
        """Calculate the current success rate."""
        if self.metrics.total_attempts == 0:
            return 0.0
        return (self.metrics.successful_attempts / self.metrics.total_attempts) * 100

    def save_metrics(self) -> None:
        """Save current metrics to file in JSON format."""
        metrics_dict = {
            "start_time": self.metrics.start_time.isoformat(),
            "total_attempts": self.metrics.total_attempts,
            "successful_attempts": self.metrics.successful_attempts,
            "failed_attempts": self.metrics.failed_attempts,
            "average_response_time": sum(self.metrics.response_times) / len(self.metrics.response_times) if self.metrics.response_times else 0,
            "error_counts": dict(self.metrics.error_counts),  # Ensure we get a fresh copy
            "current_state": self.metrics.current_state,
            "last_attempt_result": self.metrics.last_attempt_result,
            "current_retry_count": self.metrics.current_retry_count,
            "success_rate": self._calculate_success_rate()
        }
        
        with open(self.metrics_file, 'w') as f:
            json.dump(metrics_dict, f, indent=2)
