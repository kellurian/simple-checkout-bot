import pytest
from selenium.webdriver.common.by import By
from star_citizen_checkout.config import Config, BrowserMode
from star_citizen_checkout.browser import BrowserFactory

def test_browser_factory():
    """Test that browser factory can be initialized."""
    config = Config(browser={"mode": BrowserMode.HEADLESS})
    assert config.browser.mode == BrowserMode.HEADLESS
    assert config.browser.browser_type == "chrome"

def test_config_validation():
    """Test that configuration validation works."""
    # Test default config
    config = Config()
    assert config.browser.mode == BrowserMode.HEADLESS
    assert config.browser.browser_type == "chrome"
    
    # Test custom config
    custom_config = Config(
        browser={"mode": BrowserMode.HEADED, "browser_type": "firefox"},
        retry={"base_interval": 10, "max_retries": 50}
    )
    assert custom_config.browser.mode == BrowserMode.HEADED
    assert custom_config.browser.browser_type == "firefox"
    assert custom_config.retry.base_interval == 10
    assert custom_config.retry.max_retries == 50
