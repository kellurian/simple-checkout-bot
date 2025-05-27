from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from typing import Optional
from .config import BrowserConfig, BrowserMode
from .logging import get_logger

logger = get_logger(__name__)

class BrowserFactory:
    """Factory for creating WebDriver instances with proper configuration."""
    
    @staticmethod
    def create_driver(config: BrowserConfig) -> webdriver.Remote:
        """Create a new WebDriver instance based on configuration."""
        if config.browser_type == "chrome":
            return BrowserFactory._create_chrome_driver(config)
        elif config.browser_type == "firefox":
            return BrowserFactory._create_firefox_driver(config)
        else:
            raise ValueError(f"Unsupported browser type: {config.browser_type}")

    @staticmethod
    def _create_chrome_driver(config: BrowserConfig) -> webdriver.Chrome:
        """Create and configure Chrome WebDriver."""
        options = webdriver.ChromeOptions()
        
        if config.mode == BrowserMode.HEADLESS:
            options.add_argument("--headless=new")
        
        # Add common Chrome options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        
        if config.profile_path:
            options.add_argument(f"user-data-dir={config.profile_path}")

        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        logger.info("Chrome WebDriver created", mode=config.mode.value)
        return driver

    @staticmethod
    def _create_firefox_driver(config: BrowserConfig) -> webdriver.Firefox:
        """Create and configure Firefox WebDriver."""
        options = webdriver.FirefoxOptions()
        
        if config.mode == BrowserMode.HEADLESS:
            options.add_argument("--headless")
        
        if config.profile_path:
            options.add_argument("-profile")
            options.add_argument(config.profile_path)

        service = FirefoxService(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        
        logger.info("Firefox WebDriver created", mode=config.mode.value)
        return driver
