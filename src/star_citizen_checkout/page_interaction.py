from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException,
    WebDriverException
)
from typing import Optional, Tuple, Any, Dict, Callable
from selenium.webdriver.remote.webelement import WebElement
from .logging import get_logger
from .error_recovery import ErrorRecoveryManager

logger = get_logger(__name__)

class PageInteractionError(Exception):
    """Base exception for page interaction errors."""
    pass

class ElementNotFoundError(PageInteractionError):
    """Raised when an element cannot be found."""
    pass

class ElementNotInteractableError(PageInteractionError):
    """Raised when an element cannot be interacted with."""
    pass

class PageInteractor:
    """Handles all interactions with the checkout page."""
    
    # CSS Selectors from task description
    SELECTORS = {
        'proceed_button': "button.a-button.m-cartActionBar__button.-regular.-transaction.-filled.-withShapes.-shapecorner.-shapePadding24.-leftPadding24[data-cy-id='__place-order-button']",
        'terms_checkbox': "div.a-checkboxDisplay.a-checkbox__wrapper.-interactive[data-cy-id='checkbox__display']",
        'agree_button': "button.a-button.m-modalFooter__primaryButton.-regular.-interaction.-filled.-withShapes.-shapecorner.-shapePadding24.-leftPadding24[data-cy-id='modal_footer__primary_button']",
        'out_of_stock_msg': "p.m-toast__title.a-fontStyle.-emphasis-3.-no-rich-text[data-cy-id='toast__title']"
    }

    def __init__(self, driver: WebDriver, wait_timeout: int = 10, restart_callback: Optional[Callable] = None):
        """Initialize the page interactor with a WebDriver instance.
        
        Args:
            driver: WebDriver instance
            wait_timeout: Time to wait for elements in seconds
            restart_callback: Optional callback for browser restart during recovery
        """
        self.driver = driver
        self.wait_timeout = wait_timeout
        self.wait = WebDriverWait(driver, wait_timeout)
        self.recovery = ErrorRecoveryManager(driver, restart_callback)

    def wait_for_element(self, selector: str, timeout: Optional[int] = None) -> WebElement:
        """Wait for an element to be present and visible with recovery.
        
        Args:
            selector: CSS selector for the element
            timeout: Optional custom timeout in seconds
            
        Returns:
            WebElement: The found element
            
        Raises:
            ElementNotFoundError: If element cannot be found or is not visible after recovery attempts
        """
        while True:
            try:
                element = self.wait.until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, selector)),
                    timeout or self.wait_timeout
                )
                self.recovery.reset()  # Reset recovery state on success
                return element
            except TimeoutException as e:
                logger.warning("Element not found within timeout", selector=selector)
                if not self.recovery.execute_recovery(e):
                    raise ElementNotFoundError(f"Element not found after recovery attempts: {selector}") from e

    def safe_click(self, element: WebElement, element_name: str) -> bool:
        """Safely click an element with recovery logic.
        
        Args:
            element: WebElement to click
            element_name: Name of element for logging
            
        Returns:
            bool: True if click was successful
            
        Raises:
            ElementNotInteractableError: If element cannot be clicked after recovery attempts
        """
        while True:
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                element.click()
                logger.info(f"Clicked {element_name}")
                self.recovery.reset()  # Reset recovery state on success
                return True
            except (ElementClickInterceptedException, StaleElementReferenceException) as e:
                logger.warning(f"Click attempt failed for {element_name}", error=str(e))
                if not self.recovery.execute_recovery(e):
                    logger.error(f"Failed to click {element_name} after recovery attempts")
                    raise ElementNotInteractableError(f"Could not click {element_name} after recovery attempts") from e

    def click_proceed_to_pay(self) -> bool:
        """Click the 'Proceed to pay' button."""
        try:
            button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.SELECTORS['proceed_button']))
            )
            return self.safe_click(button, "proceed to pay button")
        except (TimeoutException, WebDriverException) as e:
            logger.error("Proceed to pay button not clickable", error=str(e))
            raise ElementNotInteractableError("Proceed to pay button not clickable") from e

    def check_terms(self) -> bool:
        """Click the terms checkbox.
        
        Returns:
            bool: True if terms were successfully checked
            
        Raises:
            ElementNotInteractableError: If checkbox cannot be clicked
        """
        try:
            checkbox = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.SELECTORS['terms_checkbox']))
            )
            return self.safe_click(checkbox, "terms checkbox")
        except (TimeoutException, WebDriverException) as e:
            logger.error("Terms checkbox not clickable", error=str(e))
            raise ElementNotInteractableError("Terms checkbox not clickable") from e

    def click_agree(self) -> bool:
        """Click the 'I agree' button in the modal.
        
        Returns:
            bool: True if button was successfully clicked
            
        Raises:
            ElementNotInteractableError: If button cannot be clicked
        """
        try:
            button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.SELECTORS['agree_button']))
            )
            return self.safe_click(button, "agree button")
        except (TimeoutException, WebDriverException) as e:
            logger.error("Agree button not clickable", error=str(e))
            raise ElementNotInteractableError("Agree button not clickable") from e

    def is_out_of_stock(self) -> bool:
        """Check if the out-of-stock message is present.
        
        Returns:
            bool: True if item is out of stock
        """
        try:
            element = self.wait_for_element(self.SELECTORS['out_of_stock_msg'])
            is_out = 'Unfortunately this item is out of stock' in element.text
            if is_out:
                logger.warning("Item is out of stock")
            return is_out
        except ElementNotFoundError:
            return False

    def verify_all_elements_present(self) -> Dict[str, bool]:
        """Verify that all required elements are present on the page.
        
        Returns:
            dict: Mapping of element names to their presence status
        """
        results = {}
        for name, selector in self.SELECTORS.items():
            try:
                self.wait_for_element(selector, timeout=2)  # Short timeout for quick checks
                results[name] = True
                logger.info(f"Found element: {name}")
            except ElementNotFoundError:
                results[name] = False
                logger.warning(f"Missing element: {name}")
        return results

    def complete_checkout_flow(self) -> bool:
        """Execute the complete checkout flow.
        
        Returns:
            bool: True if checkout was successful
            
        Raises:
            PageInteractionError: If any step fails
        """
        try:
            if self.is_out_of_stock():
                logger.warning("Cannot proceed - item is out of stock")
                return False
                
            # Verify critical elements are present
            element_status = self.verify_all_elements_present()
            if not all(element_status.values()):
                missing = [name for name, present in element_status.items() if not present]
                raise PageInteractionError(f"Missing required elements: {', '.join(missing)}")
            
            # Execute checkout steps
            self.check_terms()
            self.click_agree()
            self.click_proceed_to_pay()
            
            logger.info("Checkout flow completed successfully")
            return True
            
        except PageInteractionError as e:
            logger.error("Checkout flow failed", error=str(e))
            raise
