"""Unit tests for the error recovery system."""

import pytest
from unittest.mock import Mock, patch
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    WebDriverException
)
from star_citizen_checkout.error_recovery import (
    ErrorRecoveryManager,
    RecoveryLevel,
    ErrorClassification
)

@pytest.fixture
def mock_driver():
    """Create a mock WebDriver."""
    return Mock()

@pytest.fixture
def mock_restart_callback():
    """Create a mock restart callback."""
    return Mock()

@pytest.fixture
def recovery_manager(mock_driver, mock_restart_callback):
    """Create an ErrorRecoveryManager instance with mocks."""
    return ErrorRecoveryManager(mock_driver, mock_restart_callback)

def test_error_classification(recovery_manager):
    """Test that errors are classified correctly."""
    assert recovery_manager.classify_error(TimeoutException()) == ErrorClassification.NETWORK
    assert recovery_manager.classify_error(NoSuchElementException()) == ErrorClassification.STRUCTURAL
    assert recovery_manager.classify_error(ElementClickInterceptedException()) == ErrorClassification.TEMPORARY
    assert recovery_manager.classify_error(StaleElementReferenceException()) == ErrorClassification.TEMPORARY
    assert recovery_manager.classify_error(WebDriverException()) == ErrorClassification.NETWORK
    assert recovery_manager.classify_error(Exception()) == ErrorClassification.FATAL

def test_recovery_escalation(recovery_manager):
    """Test that recovery levels escalate properly."""
    with patch('time.sleep') as mock_sleep:
        # Level 1: Wait and retry (should escalate after 3 attempts)
        for _ in range(3):
            recovery_manager.execute_recovery(TimeoutException())
        assert recovery_manager.current_level == RecoveryLevel.REFRESH_RETRY
        
        # Level 2: Refresh and retry (should escalate after 2 attempts)
        for _ in range(2):
            recovery_manager.execute_recovery(TimeoutException())
        assert recovery_manager.current_level == RecoveryLevel.RESTART_RETRY
        
        # Level 3: Restart and retry (should escalate after 1 attempt)
        recovery_manager.execute_recovery(TimeoutException())
        assert recovery_manager.current_level == RecoveryLevel.USER_INTERVENTION

def test_wait_retry_recovery(recovery_manager):
    """Test Level 1 recovery: Wait and retry."""
    with patch('time.sleep') as mock_sleep:
        result = recovery_manager.execute_recovery(TimeoutException())
        assert result is True
        mock_sleep.assert_called_once_with(5)  # 5 second delay

def test_refresh_retry_recovery(recovery_manager):
    """Test Level 2 recovery: Refresh and retry."""
    recovery_manager.current_level = RecoveryLevel.REFRESH_RETRY
    with patch('time.sleep') as mock_sleep:
        result = recovery_manager.execute_recovery(TimeoutException())
        assert result is True
        mock_sleep.assert_called_once_with(15)  # 15 second delay
        recovery_manager.driver.refresh.assert_called_once()

def test_restart_retry_recovery(recovery_manager):
    """Test Level 3 recovery: Restart and retry."""
    recovery_manager.current_level = RecoveryLevel.RESTART_RETRY
    with patch('time.sleep') as mock_sleep:
        result = recovery_manager.execute_recovery(TimeoutException())
        assert result is True
        mock_sleep.assert_called_once_with(30)  # 30 second delay
        recovery_manager.restart_callback.assert_called_once()

def test_user_intervention(recovery_manager):
    """Test Level 4: User intervention raises exception."""
    recovery_manager.current_level = RecoveryLevel.USER_INTERVENTION
    with pytest.raises(Exception) as exc_info:
        recovery_manager.execute_recovery(TimeoutException())
    assert "Recovery escalated to user intervention" in str(exc_info.value)

def test_reset_recovery_state(recovery_manager):
    """Test that reset properly clears recovery state."""
    # Simulate some recovery attempts
    recovery_manager.execute_recovery(TimeoutException())
    recovery_manager.execute_recovery(NoSuchElementException())
    
    # Reset state
    recovery_manager.reset()
    
    # Verify reset
    assert recovery_manager.current_level == RecoveryLevel.WAIT_RETRY
    assert all(count == 0 for count in recovery_manager.recovery_attempts.values())
    assert all(count == 0 for count in recovery_manager.error_counts.values())
    assert recovery_manager.recovery_start_time == 0.0
