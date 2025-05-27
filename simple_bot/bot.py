"""
Star Citizen Checkout Bot

This script automates the checkout process for purchasing ships on the Star Citizen website,
specifically for timed drops of the Aegis Idris-P ship.

Features:
- Navigates to the ship's page
- Adds the ship to cart
- Applies 20% off coupon
- Applies $1385 in store credit
- Gets to the payment prompt

Requirements:
- Python 3.x
- Selenium WebDriver
- Chrome/Firefox WebDriver executable
"""

import os
import time
import logging
import platform
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("checkout_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def launch_chrome_debug(port=9222):
    """
    Launch Chrome in debug mode for remote automation.
    
    Args:
        port (int): Debug port to use (default: 9222)
    
    Returns:
        subprocess.Popen: Process handle for the Chrome instance
    """
    import subprocess
    import platform
    
    if platform.system() == 'Windows':
        chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
        if not os.path.exists(chrome_path):
            chrome_path = r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
    elif platform.system() == 'Darwin':  # macOS
        chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
    else:  # Linux
        chrome_path = 'google-chrome'
    
    cmd = [
        chrome_path,
        f'--remote-debugging-port={port}',
        '--user-data-dir=remote-profile',
        '--no-first-run',
        '--no-default-browser-check',
        '--start-maximized'
    ]
    
    try:
        process = subprocess.Popen(cmd)
        logger.info(f"Launched Chrome in debug mode on port {port}")
        return process
    except Exception as e:
        logger.error(f"Failed to launch Chrome in debug mode: {str(e)}")
        raise

class StarCitizenCheckoutBot:
    def __init__(self, browser='chrome', headless=False, ship_url=None, warbond=False, 
                 store_credit_amount=1385, profile=None, use_existing_browser=True, **kwargs):
        """
        Initialize the checkout bot.
        
        Args:
            browser (str): Browser to use ('chrome', 'firefox', or 'safari')
            headless (bool): Run browser in headless mode
            ship_url (str): URL of the ship to purchase (defaults to Idris-P)
            warbond (bool): Whether to select warbond version
            store_credit_amount (int): Amount of store credit to apply
            profile (str): Browser profile name to use (e.g., 'Default' or 'Sean')
            use_existing_browser (bool): Whether to connect to an existing Chrome instance (default: True)
            **kwargs: Additional browser-specific options
        """
        self.logger = logger  # Initialize logger
        self.ship_url = ship_url or "https://robertsspaceindustries.com/en/pledge/ships/aegis-idris/Idris-P"
        self.coupon_code = None  # Will be provided by user
        self.store_credit_amount = store_credit_amount
        self.warbond = warbond
        
        # Setup browser with automatic webdriver management
        try:
            if browser.lower() == 'chrome':
                from selenium.webdriver.chrome.service import Service
                from webdriver_manager.chrome import ChromeDriverManager
                options = webdriver.ChromeOptions()
                
                # Core stability options
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--disable-software-rasterizer')
                
                # Performance and reliability options
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-notifications')
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--start-maximized')
                options.add_argument('--window-size=1920,1080')  # Explicit window size
                options.add_argument('--remote-debugging-port=9222')  # Enable debugging
                options.add_argument('--disable-popup-blocking')  # Handle popups
                options.add_argument('--disable-blink-features')  # Disable Blink features that can cause issues
                
                # Memory and process management
                options.add_argument('--disable-background-networking')
                options.add_argument('--disable-backgrounding-occluded-windows')
                options.add_argument('--disable-breakpad')
                options.add_argument('--disable-component-update')  # Prevent updates during runtime
                options.add_argument('--disable-domain-reliability')
                options.add_argument('--disable-sync')  # Disable Chrome sync
                
                # Advanced stability options
                options.add_argument('--force-color-profile=srgb')  # Consistent color rendering
                options.add_argument('--metrics-recording-only')  # Minimal performance impact
                options.add_argument('--no-first-run')  # Skip first run wizards
                options.add_argument('--password-store=basic')
                
                # Automation-related options
                options.add_experimental_option('excludeSwitches', [
                    'enable-logging',
                    'enable-automation',
                    'ignore-certificate-errors'
                ])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_experimental_option('w3c', True)  # Enable W3C compliance
                
                # Handle browser connection mode
                debug_port = kwargs.get('debug_port', 9222)
                if use_existing_browser:
                    try:
                        # Launch or connect to debug mode Chrome
                        self.logger.info("Attempting to connect to existing Chrome instance...")
                        chrome_process = launch_chrome_debug(port=debug_port)
                        time.sleep(2)  # Give Chrome time to start
                        
                        options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
                        self.logger.info(f"Successfully connected to Chrome on port {debug_port}")
                    except Exception as e:
                        self.logger.warning(f"Failed to connect to existing Chrome: {e}")
                        self.logger.info("Falling back to new browser window")
                        # Set fallback options for new window
                        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                        options.add_argument('--disable-blink-features=AutomationControlled')
                        options.add_experimental_option("excludeSwitches", ["enable-automation"])
                        options.add_experimental_option('useAutomationExtension', False)
                else:
                    self.logger.info("Using new browser window as requested")
                    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
                    options.add_argument('--disable-blink-features=AutomationControlled')
                    options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    options.add_experimental_option('useAutomationExtension', False)
                
                # Use existing profile and cookies
                if platform.system() == 'Windows':
                    user_data_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data')
                elif platform.system() == 'Darwin':  # macOS
                    user_data_dir = os.path.expanduser('~/Library/Application Support/Google/Chrome')
                else:  # Linux
                    user_data_dir = os.path.expanduser('~/.config/google-chrome')
                
                if os.path.exists(user_data_dir):
                    options.add_argument(f'user-data-dir={user_data_dir}')
                    # Use specified profile or default
                    profile_dir = profile or 'Default'
                    profile_path = os.path.join(user_data_dir, profile_dir)
                    
                    if os.path.exists(profile_path):
                        options.add_argument(f'--profile-directory={profile_dir}')
                        self.logger.info(f"Using Chrome profile: {profile_dir}")
                    else:
                        self.logger.warning(f"Profile '{profile_dir}' not found, using Default")
                        options.add_argument('--profile-directory=Default')
                
                # Additional options for stability
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                
                if headless:
                    options.add_argument('--headless')
                
                max_retries = 3
                retry_count = 0
                
                while retry_count < max_retries:
                    try:
                        driver_path = ChromeDriverManager().install()
                        service = Service(
                            driver_path,
                            start_error_message="Chrome failed to start (Timeout)",
                            service_args=['--verbose'],
                            log_path='chromedriver.log'
                        )
                        service.connection_timeout = 60
                        
                        self.driver = webdriver.Chrome(
                            service=service,
                            options=options
                        )
                        self.logger.info(f"Chrome initialized with profile: {profile}")
                        break
                    except Exception as e:
                        retry_count += 1
                        self.logger.warning(f"Chrome initialization attempt {retry_count} failed: {str(e)}")
                        time.sleep(5)
                        
                        if retry_count >= max_retries:
                            self.logger.error(f"Failed to initialize Chrome after {max_retries} attempts")
                            self.logger.error("Trying without user profile...")
                            break
                    
                    # Retry without profile but keep security settings
                    options = webdriver.ChromeOptions()
                    
                    # Core security and stability options
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-gpu')
                    options.add_argument('--disable-extensions')
                    options.add_argument('--ignore-certificate-errors')
                    options.add_argument('--password-store=basic')
                    options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
                    options.add_experimental_option('useAutomationExtension', False)
                    
                    if headless:
                        options.add_argument('--headless')
                        
                    try:
                        self.driver = webdriver.Chrome(
                            service=Service(ChromeDriverManager().install()),
                            options=options
                        )
                        self.logger.info("Successfully initialized Chrome without profile")
                    except Exception as retry_error:
                        self.logger.error(f"Failed to initialize Chrome even without profile: {str(retry_error)}")
                        self.logger.error("Please check if Chrome is properly installed and up to date")
                        raise
            elif browser.lower() == 'firefox':
                from selenium.webdriver.firefox.service import Service
                from webdriver_manager.firefox import GeckoDriverManager
                options = webdriver.FirefoxOptions()
                
                # Security and stability preferences
                options.set_preference('security.ssl.enable_ocsp_must_staple', False)
                options.set_preference('security.ssl.enable_ocsp_stapling', False)
                options.set_preference('security.tls.enable_0rtt_data', False)
                options.set_preference('dom.webnotifications.enabled', False)
                options.set_preference('dom.push.enabled', False)
                options.set_preference('browser.cache.disk.enable', False)
                options.set_preference('browser.privatebrowsing.autostart', False)
                options.set_preference('network.http.spdy.enabled', False)
                options.set_preference('network.manage-offline-status', False)
                
                # Performance settings
                options.set_preference('browser.tabs.remote.autostart', False)
                options.set_preference('browser.tabs.remote.autostart.2', False)
                options.set_preference('toolkit.cosmeticAnimations.enabled', False)
                
                # Set legitimate user agent and mask automation
                options.set_preference('general.useragent.override', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0')
                options.set_preference('dom.webdriver.enabled', False)
                options.set_preference('useAutomationExtension', False)
                options.set_preference('marionette', False)
                options.set_preference('media.gmp-provider.enabled', False)
                
                # Determine Firefox profile directory based on OS
                if platform.system() == 'Windows':
                    profile_base = os.path.join(os.getenv('APPDATA'), 'Mozilla', 'Firefox', 'Profiles')
                elif platform.system() == 'Darwin':  # macOS
                    profile_base = os.path.expanduser('~/Library/Application Support/Firefox/Profiles')
                else:  # Linux
                    profile_base = os.path.expanduser('~/.mozilla/firefox')
                
                profile_name = kwargs.get('profile', None)
                if os.path.exists(profile_base) and profile_name:
                    # Look for profile by name
                    for dir_name in os.listdir(profile_base):
                        if profile_name.lower() in dir_name.lower():
                            profile_path = os.path.join(profile_base, dir_name)
                            logger.info(f"Found Firefox profile at: {profile_path}")
                            options.set_preference('profile', profile_path)
                            break
                    else:
                        logger.warning(f"Firefox profile '{profile_name}' not found, using default")
                
                if headless:
                    options.add_argument('--headless')
                
                try:
                    self.driver = webdriver.Firefox(
                        service=Service(GeckoDriverManager().install()),
                        options=options
                    )
                    logger.info("Firefox initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize Firefox with profile: {str(e)}")
                    logger.error("Trying without profile...")
                    # Retry without profile
                    options = webdriver.FirefoxOptions()
                    if headless:
                        options.add_argument('--headless')
                    self.driver = webdriver.Firefox(
                        service=Service(GeckoDriverManager().install()),
                        options=options
                    )
            elif browser.lower() == 'safari':
                # Safari setup
                try:
                    from selenium.webdriver.safari.options import Options as SafariOptions
                    from selenium.webdriver.safari.service import Service as SafariService
                    
                    if platform.system() != 'Darwin':
                        raise ValueError("Safari automation is only supported on macOS")
                    
                    # Check Safari Technology Preview for better automation support
                    tech_preview = False
                    if os.path.exists('/Applications/Safari Technology Preview.app'):
                        try:
                            self.driver = webdriver.Safari(
                                executable_path='/usr/bin/safaridriver.preview',
                                options=SafariOptions()
                            )
                            tech_preview = True
                            logger.info("Using Safari Technology Preview")
                        except:
                            pass
                    
                    if not tech_preview:
                        # Standard Safari setup
                        import subprocess
                        try:
                            # Try to enable Remote Automation
                            subprocess.run(['safaridriver', '--enable'], check=True)
                            
                            # Configure Safari preferences
                            subprocess.run([
                                'defaults', 'write', 
                                'com.apple.Safari', 
                                'AutoFillPasswords', '-bool', 'true'
                            ], check=True)
                            
                            subprocess.run([
                                'defaults', 'write',
                                'com.apple.Safari',
                                'AllowRemoteAutomation', '-bool', 'true'
                            ], check=True)
                        except subprocess.CalledProcessError:
                            logger.warning("Could not automatically configure Safari")
                            logger.info("\nPlease configure Safari manually:")
                            logger.info("1. Open Safari")
                            logger.info("2. Enable the Develop menu in Safari > Preferences > Advanced")
                            logger.info("3. Check 'Allow Remote Automation' in the Develop menu")
                            logger.info("4. Enable AutoFill passwords in Safari > Preferences > AutoFill")
                        
                        options = SafariOptions()
                        if headless:
                            logger.warning("Headless mode not supported in Safari")
                        
                        service = SafariService()
                        self.driver = webdriver.Safari(service=service, options=options)
                        logger.info("Safari initialized successfully")
                        
                        # Additional configurations after initialization
                        self.driver.execute_script("""
                            if (typeof safari !== 'undefined') {
                                safari.extension.settings.AutoFillPasswords = true;
                                safari.extension.settings.AutoFillCreditCards = true;
                            }
                        """)
                    
                except Exception as e:
                    logger.error("Failed to initialize Safari")
                    logger.error("Common issues:")
                    logger.error("1. Safari's Remote Automation is not enabled")
                    logger.error("2. Safari's Develop menu is not enabled")
                    logger.error("3. Safari's WebDriver is not installed")
                    logger.error(f"Error details: {str(e)}")
                    logger.info("\nTo fix:")
                    logger.info("1. Open Safari")
                    logger.info("2. Enable the Develop menu in Safari > Preferences > Advanced")
                    logger.info("3. Check 'Allow Remote Automation' in the Develop menu")
                    logger.info("4. Run 'safaridriver --enable' in terminal")
                    raise
            else:
                raise ValueError(f"Unsupported browser: {browser}. Use 'chrome', 'firefox', or 'safari'")
        except Exception as e:
            logger.error(f"Failed to initialize {browser} browser: {str(e)}")
            logger.error("Please ensure:")
            logger.error("1. The browser is installed")
            logger.error("2. You're running in virtual environment")
            logger.error("3. Required packages are installed (run reset_and_test.bat)")
            raise
        
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 15)
        logger.info(f"Initialized bot with {browser} browser")
    
    def login(self, username, password, max_retries=3):
        """
        Log in to the Star Citizen website.
        
        Args:
            username (str): RSI account username
            password (str): RSI account password
            max_retries (int): Maximum number of login attempts
        """
        retry_count = 0
        while retry_count < max_retries:
            try:
                # Clear cookies and cache before login attempt
                self.driver.delete_all_cookies()
                
                # Navigate to login page with page load strategy
                logger.info("Navigating to login page")
                self.driver.get("https://robertsspaceindustries.com/sign-in")
                
                # Wait for page to be fully loaded
                self.wait.until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
                
                # Wait for login form with extended timeout
                username_field = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.ID, "handle")),
                    message="Username field not found"
                )
                
                # Ensure fields are interactable
                password_field = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.ID, "password")),
                    message="Password field not found or not clickable"
                )
                
                # Clear fields before entering credentials
                username_field.clear()
                password_field.clear()
                
                # Enter credentials with delay between keystrokes
                for char in username:
                    username_field.send_keys(char)
                    time.sleep(0.1)
                
                for char in password:
                    password_field.send_keys(char)
                    time.sleep(0.1)
                
                # Find and verify login button is clickable
                login_button = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")),
                    message="Login button not found or not clickable"
                )
                
                # Execute click with JavaScript for reliability
                self.driver.execute_script("arguments[0].click();", login_button)
                
                # Wait for login to complete with multiple success conditions
                WebDriverWait(self.driver, 30).until(
                    lambda driver: any([
                        EC.url_contains("account")(driver),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".account-hub"))(driver),
                        EC.presence_of_element_located((By.CSS_SELECTOR, ".logged-in"))(driver)
                    ]),
                    message="Login verification failed"
                )
                
                logger.info("Successfully logged in")
                return True
                
            except Exception as e:
                retry_count += 1
                logger.warning(f"Login attempt {retry_count} failed: {str(e)}")
                
                if retry_count >= max_retries:
                    logger.error(f"Login failed after {max_retries} attempts. Last error: {str(e)}")
                    raise
                
                # Wait before retrying
                time.sleep(5)
                
                # Refresh the page for next attempt
                try:
                    self.driver.refresh()
                except:
                    pass
    
    def navigate_to_ship(self):
        """Navigate to the ship's page."""
        try:
            logger.info(f"Navigating to ship URL: {self.ship_url}")
            self.driver.get(self.ship_url)
            
            # Wait for the page to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-pledge")))
            logger.info("Successfully loaded ship page")
            
        except Exception as e:
            logger.error(f"Failed to navigate to ship page: {str(e)}")
            raise
    
    def check_stock_available(self):
        """
        Check if the ship is in stock.
        
        Returns:
            bool: True if in stock, False otherwise
        """
        try:
            # Check for common "out of stock" indicators
            out_of_stock_indicators = [
                ".out-of-stock",
                ".sold-out",
                ".stock-depleted",
                ".unavailable"
            ]
            
            # Look for any out of stock indicators
            for indicator in out_of_stock_indicators:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, indicator)
                    logger.info("Ship is out of stock")
                    return False
                except NoSuchElementException:
                    continue
            
            # Check if add to cart button is present and enabled
            try:
                add_to_cart_button = self.driver.find_element(By.CSS_SELECTOR, ".js-store-add-to-cart, .btn-add-to-cart")
                if add_to_cart_button.is_enabled():
                    logger.info("Ship appears to be in stock")
                    return True
                else:
                    logger.info("Add to cart button is disabled - likely out of stock")
                    return False
            except NoSuchElementException:
                logger.info("Add to cart button not found - likely out of stock")
                return False
            
        except Exception as e:
            logger.error(f"Error checking stock: {str(e)}")
            return False

    def select_ship_offer(self):
        """Select the appropriate ship offer (warbond or standard)."""
        try:
            logger.info("Looking for ship offers...")
            
            # Click 'View Offers' button if present
            try:
                view_offers = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-view-offers, .view-offers-btn"))
                )
                view_offers.click()
                logger.info("Clicked View Offers button")
            except Exception as e:
                logger.info("No View Offers button found, proceeding with visible offers")
            
            # Wait for offers to be visible
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ship-offers, .pledge-options"))
            )
            
            # Look for the appropriate offer
            if self.warbond:
                logger.info("Looking for Warbond offer...")
                offer_selector = "[data-warbond='true'], .warbond-offer"
            else:
                logger.info("Looking for standard offer...")
                offer_selector = "[data-warbond='false'], .standard-offer"
            
            offer = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, offer_selector))
            )
            offer.click()
            logger.info(f"Selected {'Warbond' if self.warbond else 'Standard'} offer")
            
        except Exception as e:
            logger.error(f"Failed to select ship offer: {str(e)}")
            raise

    def add_to_cart(self, retry_attempts=None, retry_interval=5):
        """
        Add the ship to the cart with optional retry functionality.
        
        Args:
            retry_attempts (int, optional): Number of times to retry if out of stock.
                                         If None, will retry indefinitely.
            retry_interval (int): Seconds to wait between retries
        
        Returns:
            bool: True if successfully added to cart, False if max retries reached
        """
        attempt = 1
        
        while True:
            try:
                logger.info(f"Attempt {attempt} to add ship to cart")
                
                # Refresh the page to get latest stock status
                self.driver.refresh()
                time.sleep(2)  # Wait for page to settle
                
                # Check if in stock
                if not self.check_stock_available():
                    if retry_attempts and attempt >= retry_attempts:
                        logger.error("Maximum retry attempts reached - ship still not available")
                        return False
                    
                    logger.info(f"Ship not in stock. Waiting {retry_interval} seconds before retry...")
                    time.sleep(retry_interval)
                    attempt += 1
                    continue
                
                # Try to add to cart
                add_to_cart_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-store-add-to-cart, .btn-add-to-cart"))
                )
                add_to_cart_button.click()
                
                # Wait for confirmation that item was added to cart
                self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".js-cart-notification, .notification-success")))
                logger.info("Successfully added ship to cart")
                return True
                
            except TimeoutException:
                logger.warning("Timeout while attempting to add to cart")
                if retry_attempts and attempt >= retry_attempts:
                    logger.error("Maximum retry attempts reached")
                    return False
                
            except Exception as e:
                logger.error(f"Error adding ship to cart: {str(e)}")
                if retry_attempts and attempt >= retry_attempts:
                    logger.error("Maximum retry attempts reached")
                    return False
            
            logger.info(f"Waiting {retry_interval} seconds before retry...")
            time.sleep(retry_interval)
            attempt += 1
    
    def go_to_checkout(self):
        """Navigate to the checkout page."""
        try:
            logger.info("Navigating to checkout")
            
            # Navigate to cart page
            self.driver.get("https://robertsspaceindustries.com/en/account/cart")
            
            # Wait for the checkout button
            checkout_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-checkout-button, .btn-checkout"))
            )
            checkout_button.click()
            
            # Wait for checkout page to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".checkout-step")))
            logger.info("Successfully navigated to checkout page")
            
        except Exception as e:
            logger.error(f"Failed to navigate to checkout: {str(e)}")
            raise
    
    def apply_coupon(self, coupon_code):
        """
        Apply a coupon code at checkout.
        
        Args:
            coupon_code (str): The coupon code to apply
        """
        try:
            logger.info(f"Attempting to apply coupon code: {coupon_code}")
            self.coupon_code = coupon_code
            
            # Find and click "Apply Coupon" button or field
            coupon_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".js-coupon-field, #coupon-code"))
            )
            coupon_field.send_keys(coupon_code)
            
            # Click apply button
            apply_button = self.driver.find_element(By.CSS_SELECTOR, ".js-apply-coupon, .btn-apply-coupon")
            apply_button.click()
            
            # Wait for confirmation
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".coupon-applied, .notification-success")))
            logger.info("Successfully applied coupon code")
            
        except Exception as e:
            logger.error(f"Failed to apply coupon: {str(e)}")
            raise
    
    def apply_store_credit(self):
        """Apply store credit to the purchase."""
        try:
            logger.info(f"Attempting to apply ${self.store_credit_amount} in store credit")
            
            # Find store credit field
            credit_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".js-store-credit-field, #store-credit"))
            )
            
            # Clear the field and enter the credit amount
            credit_field.clear()
            credit_field.send_keys(str(self.store_credit_amount))
            
            # Click apply button
            apply_button = self.driver.find_element(By.CSS_SELECTOR, ".js-apply-credit, .btn-apply-credit")
            apply_button.click()
            
            # Wait for confirmation
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".credit-applied, .notification-success")))
            logger.info("Successfully applied store credit")
            
        except Exception as e:
            logger.error(f"Failed to apply store credit: {str(e)}")
            raise
    
    def proceed_to_payment(self):
        """Proceed to the payment options screen."""
        try:
            logger.info("Proceeding to payment options")
            
            # Click the "Proceed to Payment" button
            payment_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-proceed-to-payment, .btn-proceed"))
            )
            payment_button.click()
            
            # Wait for payment options to appear
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".payment-methods, .payment-options")))
            logger.info("Successfully reached payment options")
            
        except Exception as e:
            logger.error(f"Failed to proceed to payment: {str(e)}")
            raise
    
    def handle_disclaimer(self):
        """Handle the disclaimer popup during checkout."""
        try:
            logger.info("Handling disclaimer popup...")
            
            # Wait for disclaimer popup
            disclaimer_dialog = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".disclaimer-dialog, #disclaimer-popup"))
            )
            
            # Scroll to bottom of disclaimer
            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", 
                disclaimer_dialog
            )
            
            # Check the agreement boxes
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, 
                ".disclaimer-checkbox, input[type='checkbox']")
            for checkbox in checkboxes:
                if not checkbox.is_selected():
                    checkbox.click()
            
            # Click agree button
            agree_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-agree-button, #agree-button"))
            )
            agree_button.click()
            
            logger.info("Successfully handled disclaimer")
            
        except Exception as e:
            logger.error(f"Failed to handle disclaimer: {str(e)}")
            raise

    def complete_checkout(self, retry_attempts=None, retry_interval=5):
        """
        Run the complete checkout process.
        
        Args:
            retry_attempts (int, optional): Number of times to retry if ship is out of stock.
                                         If None, will retry indefinitely.
            retry_interval (int): Seconds to wait between retries
            
        Returns:
            bool: True if checkout process completed successfully, False otherwise
        """
        try:
            logger.info("Starting checkout process")
            
            # Navigate to ship page and select offer
            self.navigate_to_ship()
            self.select_ship_offer()
            
            # Try to add to cart with retry functionality
            cart_success = False
            while not cart_success:
                if not self.add_to_cart(retry_attempts=retry_attempts, retry_interval=retry_interval):
                    logger.error("Failed to add ship to cart after all retry attempts")
                    return False
                
                try:
                    # Try to proceed with checkout
                    self.go_to_checkout()
                    cart_success = True
                except Exception as e:
                    logger.warning(f"Checkout failed, retrying: {str(e)}")
                    continue
                logger.error("Failed to add ship to cart after all retry attempts")
                return False
            
            # Handle Step 1: Apply coupon and store credit
            if self.coupon_code:
                self.apply_coupon(self.coupon_code)
            self.apply_store_credit()
            
            # Click continue to Step 2
            continue_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-continue, .continue-btn"))
            )
            continue_button.click()
            
            # Handle Step 2: Confirm address and handle disclaimer
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".address-step, #shipping-step"))
            )
            proceed_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-proceed-pay, .proceed-to-pay"))
            )
            proceed_button.click()
            
            # Handle the disclaimer popup
            self.handle_disclaimer()
            
            # Wait for Step 3 (payment screen)
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".payment-step, #payment-step"))
            )
            
            logger.info("Checkout process completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Checkout process failed: {str(e)}")
            return False
    
    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()
            logger.info("Browser closed")

def main():
    """Main function to run the checkout bot."""
    import argparse
    import getpass
    
    parser = argparse.ArgumentParser(description="Star Citizen Checkout Bot")
    parser.add_argument("--username", help="RSI account username")
    parser.add_argument("--password", help="RSI account password")
    parser.add_argument("--coupon", help="20% off coupon code")
    parser.add_argument("--browser", default="chrome", choices=["chrome", "firefox", "safari"], help="Browser to use")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode (not supported in Safari)")
    parser.add_argument("--use-existing-browser", action="store_true", default=True, help="Connect to existing Chrome instance (maintains login)")
    parser.add_argument("--new-window", action="store_true", help="Launch in a new browser window instead of connecting to existing")
    parser.add_argument("--use-config", action="store_true", help="Use saved configuration")
    parser.add_argument("--setup-config", action="store_true", help="Setup and save configuration")
    parser.add_argument("--retry-attempts", type=int, help="Number of times to retry if ship is out of stock. If not provided, will retry indefinitely.")
    parser.add_argument("--retry-interval", type=int, default=5, help="Seconds to wait between retries (default: 5)")
    parser.add_argument("--ship-url", help="URL of the ship to purchase (defaults to Idris-P)")
    parser.add_argument("--warbond", action="store_true", help="Select warbond version instead of standard")
    parser.add_argument("--store-credit", type=float, default=1385, help="Amount of store credit to apply (default: 1385)")
    
    args = parser.parse_args()
    
    # Handle configuration
    username = args.username
    password = args.password
    coupon_code = args.coupon
    browser = args.browser
    
    # Check if we should use the configuration manager
    if args.setup_config:
        from config_manager import setup_config
        if setup_config():
            logger.info("Configuration saved successfully. You can now use --use-config")
            return
        else:
            logger.error("Configuration setup failed")
            return
    
    if args.use_config:
        try:
            from config_manager import ConfigManager
            config = ConfigManager()
            
            # Get encryption password
            encryption_password = getpass.getpass("Enter your encryption password: ")
            if not config.set_encryption_password(encryption_password):
                logger.error("Failed to decrypt configuration with provided password")
                return
            
            # Get saved credentials
            username, password = config.get_credentials()
            if not username or not password:
                logger.error("Failed to retrieve credentials from configuration")
                return
            
            # Get saved coupon
            coupon_code = config.get_coupon()
            if not coupon_code:
                logger.error("Failed to retrieve coupon from configuration")
                return
            
            # Get browser preference
            browser = config.get_browser_preference()
            
            logger.info("Successfully loaded configuration")
            
        except ImportError:
            logger.error("Config manager not found. Please create a configuration first with --setup-config")
            return
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return
    
    # Validate required arguments
    if not username or not password or not coupon_code:
        logger.error("Missing required arguments. Provide credentials and coupon directly or use --use-config")
        parser.print_help()
        return
    
    bot = StarCitizenCheckoutBot(
        browser=browser,
        headless=args.headless,
        ship_url=args.ship_url,
        warbond=args.warbond,
        store_credit_amount=args.store_credit
    )
    
    try:
        bot.login(username, password)
        bot.coupon_code = coupon_code
        success = bot.complete_checkout(
            retry_attempts=args.retry_attempts,
            retry_interval=args.retry_interval
        )
        
        if not success:
            logger.error("Checkout process failed")
            return
        
        # Keep the browser open at the payment screen
        logger.info("Bot has reached the payment screen. DO NOT CLOSE THIS WINDOW.")
        logger.info("Please complete the payment process manually.")
        
        # Wait indefinitely for user to complete the process
        while True:
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
    finally:
        # Don't close the browser automatically to allow manual completion
        # The user will need to close it manually after completing payment
        pass

if __name__ == "__main__":
    main()
