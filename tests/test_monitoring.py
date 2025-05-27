import json
import os
from datetime import datetime
import pytest
from src.star_citizen_checkout.monitoring import MonitoringSystem, MetricsData

@pytest.fixture
def monitoring():
    """Create a monitoring system with a temporary metrics file."""
    test_file = "test_metrics.json"
    monitoring = MonitoringSystem(metrics_file=test_file)
    yield monitoring
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)

def test_metrics_file_creation(monitoring):
    """Test that metrics file is created on initialization."""
    assert os.path.exists(monitoring.metrics_file)
    with open(monitoring.metrics_file) as f:
        data = json.load(f)
    assert "total_attempts" in data
    assert "success_rate" in data

def test_record_attempt(monitoring):
    """Test recording successful and failed attempts."""
    # Record successful attempt
    monitoring.record_attempt(True, 0.5)
    assert monitoring.metrics.total_attempts == 1
    assert monitoring.metrics.successful_attempts == 1
    assert len(monitoring.metrics.response_times) == 1
    assert monitoring.metrics.last_attempt_result == "success"

    # Record failed attempt
    monitoring.record_attempt(False, 0.3)
    assert monitoring.metrics.total_attempts == 2
    assert monitoring.metrics.failed_attempts == 1
    assert len(monitoring.metrics.response_times) == 2
    assert monitoring.metrics.last_attempt_result == "failure"

def test_record_error(monitoring):
    """Test error recording."""
    error_type = "TimeoutError"
    monitoring.record_error(error_type)
    assert monitoring.metrics.error_counts[error_type] == 1
    monitoring.record_error(error_type)
    assert monitoring.metrics.error_counts[error_type] == 2

def test_update_state(monitoring):
    """Test state updates."""
    monitoring.update_state("running")
    assert monitoring.metrics.current_state == "running"
    with open(monitoring.metrics_file) as f:
        data = json.load(f)
    assert data["current_state"] == "running"

def test_update_retry_count(monitoring):
    """Test retry count updates."""
    monitoring.update_retry_count(5)
    assert monitoring.metrics.current_retry_count == 5
    with open(monitoring.metrics_file) as f:
        data = json.load(f)
    assert data["current_retry_count"] == 5

def test_success_rate_calculation(monitoring):
    """Test success rate calculation."""
    # No attempts
    assert monitoring._calculate_success_rate() == 0.0

    # 2 successes, 1 failure
    monitoring.record_attempt(True, 0.5)
    monitoring.record_attempt(True, 0.5)
    monitoring.record_attempt(False, 0.5)
    assert monitoring._calculate_success_rate() == pytest.approx(66.67, rel=0.01)

def test_metrics_file_format(monitoring):
    """Test that metrics file is properly formatted and readable."""
    monitoring.record_attempt(True, 0.5)
    monitoring.record_error("NetworkError")
    monitoring.update_state("running")
    
    with open(monitoring.metrics_file) as f:
        data = json.load(f)
    
    required_fields = {
        "start_time",
        "total_attempts",
        "successful_attempts",
        "failed_attempts",
        "average_response_time",
        "error_counts",
        "current_state",
        "last_attempt_result",
        "current_retry_count",
        "success_rate"
    }
    
    assert all(field in data for field in required_fields)
    assert isinstance(data["error_counts"], dict)
    assert datetime.fromisoformat(data["start_time"])
