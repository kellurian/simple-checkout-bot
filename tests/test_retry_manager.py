import pytest
from datetime import datetime, timedelta
import time
from star_citizen_checkout.config import RetryConfig
from star_citizen_checkout.retry_manager import RetryManager, RetryStats

def test_retry_stats():
    """Test retry statistics tracking."""
    stats = RetryStats()
    
    # Test interval tracking
    stats.add_interval(5.0)
    stats.add_interval(5.2)
    assert stats.average_interval == pytest.approx(5.1, abs=0.1)
    
    # Test attempt counting
    stats.total_attempts = 2
    stats.successful_attempts = 1
    stats.failed_attempts = 1
    assert stats.total_attempts == 2
    assert stats.successful_attempts == 1
    assert stats.failed_attempts == 1

def test_retry_with_success():
    """Test retry logic with eventual success."""
    config = RetryConfig(
        base_interval=0.1,  # Small interval for testing
        max_retries=5,
        max_attempts_per_minute=10
    )
    
    manager = RetryManager(config)
    
    # Operation that succeeds on third attempt
    attempt_count = 0
    def test_operation():
        nonlocal attempt_count
        attempt_count += 1
        return attempt_count == 3
    
    result = manager.execute_with_retry(test_operation)
    
    assert result is True
    assert manager.stats.total_attempts == 3
    assert manager.stats.successful_attempts == 1
    assert manager.stats.failed_attempts == 2

def test_retry_with_max_retries():
    """Test that retry stops after max attempts."""
    config = RetryConfig(
        base_interval=0.1,
        max_retries=3,
        max_attempts_per_minute=10
    )
    
    manager = RetryManager(config)
    
    # Operation that never succeeds
    result = manager.execute_with_retry(lambda: False)
    
    assert result is None
    assert manager.stats.total_attempts == 3
    assert manager.stats.successful_attempts == 0
    assert manager.stats.failed_attempts == 3

def test_rate_limiting():
    """Test rate limiting functionality."""
    config = RetryConfig(
        base_interval=0.01,  # Very short for testing
        max_retries=3,
        max_attempts_per_minute=2  # Only 2 attempts allowed per minute
    )
    
    manager = RetryManager(config)
    
    # Mock time.sleep to avoid actual waiting
    original_sleep = time.sleep
    sleep_calls = []
    
    def mock_sleep(seconds):
        sleep_calls.append(seconds)
    
    time.sleep = mock_sleep
    try:
        manager.execute_with_retry(lambda: False)
    finally:
        time.sleep = original_sleep
    
    # Verify rate limiting caused longer waits
    assert any(wait > 1.0 for wait in sleep_calls), "No rate limiting waits detected"
    assert len(sleep_calls) >= 2, "Not enough retry attempts"

def test_comprehensive_stats():
    """Test detailed statistics tracking."""
    config = RetryConfig(
        base_interval=0.01,
        max_retries=5,
        max_attempts_per_minute=100
    )
    
    manager = RetryManager(config)
    
    # Operation that fails with exception first, fails normally second, then succeeds
    attempt_count = 0
    def test_operation():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count == 1:
            raise Exception("Test exception")
        elif attempt_count == 2:
            return False
        return True
    
    result = manager.execute_with_retry(test_operation)
    
    assert result is True
    assert manager.stats.total_attempts == 3
    assert manager.stats.successful_attempts == 1
    assert manager.stats.failed_attempts == 2
    assert manager.stats.last_success_time is not None
    assert manager.stats.last_failure_time is not None
    assert len(manager.stats.attempt_intervals) == 2  # Should have 2 intervals for 3 attempts
    assert all(i > 0 for i in manager.stats.attempt_intervals)

def test_infinite_retries():
    """Test infinite retry mode with early exit."""
    config = RetryConfig(
        base_interval=0.01,
        max_retries=0,  # 0 means infinite
        max_attempts_per_minute=100
    )
    
    manager = RetryManager(config)
    
    # Operation that succeeds after 3 attempts
    attempt_count = 0
    def test_operation():
        nonlocal attempt_count
        attempt_count += 1
        return attempt_count == 3
    
    result = manager.execute_with_retry(test_operation)
    
    assert result is True
    assert manager.stats.total_attempts == 3
    assert manager.stats.successful_attempts == 1

def test_jitter():
    """Test that jitter is applied to intervals."""
    config = RetryConfig(
        base_interval=1.0,
        max_retries=5,
        max_attempts_per_minute=10
    )
    
    manager = RetryManager(config)
    
    # Collect several jittered intervals
    intervals = []
    for _ in range(10):
        interval = manager._apply_jitter(config.base_interval)
        intervals.append(interval)
    
    # Verify jitter was applied (not all intervals are exactly 1.0)
    assert not all(i == 1.0 for i in intervals)
    # Verify jitter is within bounds (±10%)
    assert all(0.9 <= i <= 1.1 for i in intervals)
