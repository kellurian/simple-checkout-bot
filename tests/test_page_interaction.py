import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from star_citizen_checkout.page_interaction import (
    PageInteractor,
    PageInteractionError,
    ElementNotFoundError,
    ElementNotInteractableError
)
from star_citizen_checkout.config import Config
from star_citizen_checkout.browser import BrowserFactory
import os

@pytest.fixture
def mock_server_url():
    """Get the mock server URL from environment or use default."""
    return os.getenv('MOCK_SERVER_URL', 'http://localhost:8000')

@pytest.fixture
def driver():
    """Create a WebDriver instance for testing."""
    config = Config()
    driver = BrowserFactory.create_driver(config.browser)
    try:
        yield driver
    finally:
        driver.quit()

@pytest.fixture
def page_interactor(driver):
    """Create a PageInteractor instance for testing."""
    return PageInteractor(driver)

def test_element_detection(mock_server_url, driver, page_interactor):
    """Test that the page interactor can detect elements on the mock checkout page."""
    driver.get(mock_server_url)
    
    # Verify all elements are present
    element_status = page_interactor.verify_all_elements_present()
    assert all(element_status.values()), f"Missing elements: {[k for k,v in element_status.items() if not v]}"

def test_out_of_stock_detection(mock_server_url, driver, page_interactor):
    """Test that out-of-stock detection works."""
    driver.get(mock_server_url)
    
    # First check without the message
    assert not page_interactor.is_out_of_stock(), "Should not detect out of stock when message isn't present"
    
    # Inject the out-of-stock message for testing
    driver.execute_script("""
        const p = document.createElement('p');
        p.className = 'm-toast__title a-fontStyle -emphasis-3 -no-rich-text';
        p.setAttribute('data-cy-id', 'toast__title');
        p.textContent = 'Unfortunately this item is out of stock';
        document.body.appendChild(p);
    """)
    
    # Now check with the message
    assert page_interactor.is_out_of_stock(), "Should detect out of stock message"

def test_successful_checkout_flow(mock_server_url, driver, page_interactor):
    """Test the complete checkout flow succeeds when all elements are present."""
    driver.get(mock_server_url)
    
    assert page_interactor.complete_checkout_flow(), "Checkout flow should succeed"

def test_checkout_flow_with_out_of_stock(mock_server_url, driver, page_interactor):
    """Test the checkout flow handles out of stock correctly."""
    driver.get(mock_server_url)
    
    # Inject out of stock message
    driver.execute_script("""
        const p = document.createElement('p');
        p.className = 'm-toast__title a-fontStyle -emphasis-3 -no-rich-text';
        p.setAttribute('data-cy-id', 'toast__title');
        p.textContent = 'Unfortunately this item is out of stock';
        document.body.appendChild(p);
    """)
    
    assert not page_interactor.complete_checkout_flow(), "Checkout should fail when out of stock"

def test_error_handling(mock_server_url, driver, page_interactor):
    """Test error handling for missing elements."""
    driver.get(mock_server_url)
    
    # Remove a required element
    driver.execute_script("""
        const btn = document.querySelector('[data-cy-id="__place-order-button"]');
        if (btn) btn.remove();
    """)
    
    with pytest.raises(PageInteractionError):
        page_interactor.complete_checkout_flow()

def test_safe_click_retry(mock_server_url, driver, page_interactor):
    """Test that safe_click retries on temporary failures."""
    driver.get(mock_server_url)
    
    # Create a button that becomes clickable after delay
    driver.execute_script("""
        const btn = document.querySelector('[data-cy-id="__place-order-button"]');
        const originalClick = btn.click;
        let attempts = 0;
        btn.click = function() {
            attempts++;
            if (attempts < 2) throw new Error('Temporary failure');
            return originalClick.call(this);
        };
    """)
    
    assert page_interactor.click_proceed_to_pay(), "Click should succeed after retry"
