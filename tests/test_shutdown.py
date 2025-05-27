"""Tests for the shutdown manager functionality."""

import pytest
import signal
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from selenium import webdriver
from star_citizen_checkout.shutdown import ShutdownManager

def test_shutdown_manager_initialization():
    """Test basic initialization of shutdown manager."""
    manager = ShutdownManager()
    assert manager.driver is None
    assert len(manager.temp_files) == 0
    assert len(manager.cleanup_callbacks) == 0

def test_browser_registration():
    """Test browser registration and cleanup."""
    manager = ShutdownManager()
    mock_driver = Mock(spec=webdriver.Remote)
    
    # Register and verify
    manager.register_browser(mock_driver)
    assert manager.driver == mock_driver
    
    # Test cleanup
    manager.cleanup_browser()
    mock_driver.quit.assert_called_once()
    assert manager.driver is None

def test_temp_file_registration():
    """Test temporary file registration and cleanup."""
    manager = ShutdownManager()
    test_path = "/tmp/test_file.txt"
    
    # Register and verify
    manager.register_temp_file(test_path)
    assert test_path in manager.temp_files
    
    # Test cleanup with mocked Path operations
    with patch('star_citizen_checkout.shutdown.Path') as mock_path_class:
        mock_path_instance = Mock()
        mock_path_class.return_value = mock_path_instance
        mock_path_instance.exists.return_value = True
        
        manager.cleanup_temp_files()
        
        mock_path_class.assert_called_once_with(test_path)
        mock_path_instance.exists.assert_called_once()
        mock_path_instance.unlink.assert_called_once()
        assert len(manager.temp_files) == 0

def test_cleanup_callback():
    """Test cleanup callback registration and execution."""
    manager = ShutdownManager()
    mock_callback = Mock()
    
    # Register and verify
    manager.register_cleanup_callback(mock_callback)
    assert mock_callback in manager.cleanup_callbacks
    
    # Test execution
    manager.run_cleanup_callbacks()
    mock_callback.assert_called_once()
    assert len(manager.cleanup_callbacks) == 0

@patch('star_citizen_checkout.shutdown.Path')
def test_complete_shutdown(mock_path_class):
    """Test complete shutdown procedure."""
    manager = ShutdownManager()
    test_path = "/tmp/test_file.txt"
    
    # Setup mocks
    mock_driver = Mock(spec=webdriver.Remote)
    mock_path_instance = Mock()
    mock_path_class.return_value = mock_path_instance
    mock_path_instance.exists.return_value = True
    mock_callback = Mock()
    
    # Register everything
    manager.register_browser(mock_driver)
    manager.register_temp_file(test_path)
    manager.register_cleanup_callback(mock_callback)
    
    # Execute shutdown
    manager.shutdown("Test shutdown")
    
    # Verify all cleanups occurred
    mock_driver.quit.assert_called_once()
    mock_path_class.assert_called_once_with(test_path)
    mock_path_instance.exists.assert_called_once()
    mock_path_instance.unlink.assert_called_once()
    mock_callback.assert_called_once()
    
    # Verify all collections cleared
    assert manager.driver is None
    assert len(manager.temp_files) == 0
    assert len(manager.cleanup_callbacks) == 0

@patch('signal.signal')
def test_signal_handling(mock_signal):
    """Test signal handler registration."""
    manager = ShutdownManager()
    
    # Verify signal handlers were registered
    assert mock_signal.call_count == 2
    mock_signal.assert_any_call(signal.SIGTERM, manager._handle_signal)
    mock_signal.assert_any_call(signal.SIGINT, manager._handle_signal)

@patch('star_citizen_checkout.shutdown.Path')
def test_error_handling(mock_path_class):
    """Test error handling during cleanup."""
    manager = ShutdownManager()
    test_path = "/tmp/test_error.txt"
    
    # Setup failing mocks
    mock_driver = Mock(spec=webdriver.Remote)
    mock_driver.quit.side_effect = Exception("Browser cleanup failed")
    
    mock_path_instance = Mock()
    mock_path_class.return_value = mock_path_instance
    mock_path_instance.exists.return_value = True
    mock_path_instance.unlink.side_effect = Exception("File cleanup failed")
    
    mock_callback = Mock(side_effect=Exception("Callback failed"))
    
    # Register everything
    manager.register_browser(mock_driver)
    manager.register_temp_file(test_path)
    manager.register_cleanup_callback(mock_callback)
    
    # Shutdown should complete without raising exceptions
    manager.shutdown("Test error handling")
    
    # Verify all cleanups were attempted
    mock_driver.quit.assert_called_once()
    mock_path_class.assert_called_once_with(test_path)
    mock_path_instance.exists.assert_called_once()
    mock_path_instance.unlink.assert_called_once()
    mock_callback.assert_called_once()
