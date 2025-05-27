import pytest
from src.star_citizen_checkout.config import RetryConfig
from src.star_citizen_checkout.retry_manager import RetryManager
import os
import json

@pytest.fixture
def retry_manager():
    """Create a retry manager with test configuration."""
    config = RetryConfig(
        base_interval=0.1,  # Short interval for tests
        max_retries=3,  # Number of retries after initial attempt
        max_attempts_per_minute=60
    )
    manager = RetryManager(config)
    yield manager
    # Cleanup metrics file
    if os.path.exists(manager.monitoring.metrics_file):
        os.remove(manager.monitoring.metrics_file)

def test_retry_manager_monitoring_integration(retry_manager):
    """Test that RetryManager properly updates monitoring metrics."""
    
    # Define test operations
    def success_operation():
        return True
    
    def failure_operation():
        return False
    
    def error_operation():
        raise ValueError("Test error")
    
    # Test successful operation
    result = retry_manager.execute_with_retry(success_operation)
    assert result is True
    
    with open(retry_manager.monitoring.metrics_file) as f:
        metrics = json.load(f)
        assert metrics["total_attempts"] == 1
        assert metrics["successful_attempts"] == 1
        assert metrics["failed_attempts"] == 0
        assert metrics["current_retry_count"] == 1
        assert metrics["success_rate"] == 100.0
    
    # Test failed operation
    result = retry_manager.execute_with_retry(failure_operation)
    assert result is None  # Should return None after max retries
    
    with open(retry_manager.monitoring.metrics_file) as f:
        metrics = json.load(f)
        assert metrics["total_attempts"] == 3  # Initial attempt + 2 retries
        assert metrics["successful_attempts"] == 1
        assert metrics["failed_attempts"] == 2
        assert metrics["current_retry_count"] == 3
        assert metrics["success_rate"] == pytest.approx(33.33, rel=0.01)
    
    # Test error operation
    result = retry_manager.execute_with_retry(error_operation)
    assert result is None
    
    with open(retry_manager.monitoring.metrics_file) as f:
        metrics = json.load(f)
        assert metrics["total_attempts"] == 3  # Initial attempt + 2 retries
        assert metrics["successful_attempts"] == 1
        assert metrics["failed_attempts"] == 2
        assert "ValueError" in metrics["error_counts"]
        assert metrics["current_retry_count"] == 3
        assert metrics["success_rate"] == pytest.approx(33.33, rel=0.01)

def test_monitoring_state_updates(retry_manager):
    """Test that state updates are properly tracked."""
    def operation():
        return True
    
    retry_manager.execute_with_retry(operation)
    
    with open(retry_manager.monitoring.metrics_file) as f:
        metrics = json.load(f)
        assert metrics["current_state"] == "completed"  # State changes to completed on success
        assert metrics["last_attempt_result"] == "success"
