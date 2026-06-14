"""Browser management module."""

import time
import random
import undetected_chromedriver as uc
from typing import Optional
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from config.settings import settings
from config.constants import BASE_HEADERS
from utils.ua_rotator import UARotator
from utils.logger import logger_instance as logger
from core.exceptions import BrowserTimeoutException, BrowserException


class BrowserManager:
    """Manage browser instances with anti-detection features."""

    def __init__(self, headless: bool = True, timeout: int = 30):
        """Initialize browser manager.
        
        Args:
            headless: Run browser in headless mode
            timeout: Page load timeout in seconds
        """
        self.headless = headless
        self.timeout = timeout
        self.ua_rotator = UARotator()
        self.driver = None

    def create_driver_with_proxy(self, proxy: Optional[str] = None) -> WebDriver:
        """Create anti-detection browser driver.
        
        Args:
            proxy: Proxy URL to use
            
        Returns:
            WebDriver instance
            
        Raises:
            BrowserException: If driver creation fails
        """
        try:
            options = uc.ChromeOptions()
            
            # Add proxy if provided
            if proxy:
                options.add_argument(f"--proxy-server={proxy}")
                logger.info(f"Using proxy: {proxy}")
            
            # Basic options
            if self.headless:
                options.add_argument("--headless=new")
            
            options.add_argument("--start-maximized")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-plugins")
            
            # Disable images for faster loading
            if settings.disable_images:
                options.add_argument("--blink-settings=imagesEnabled=false")
            
            # Random window size
            width = random.randint(1800, 2560)
            height = random.randint(1000, 1440)
            options.add_argument(f"--window-size={width},{height}")
            
            # Create undetected driver
            driver = uc.Chrome(options=options, version_main=None)
            
            # Inject anti-webdriver detection
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                    });
                """
            })
            
            # Set timeouts
            driver.set_page_load_timeout(self.timeout)
            driver.set_script_timeout(self.timeout)
            
            logger.info("Browser driver created successfully")
            self.driver = driver
            return driver
            
        except Exception as e:
            logger.error(f"Failed to create browser driver: {str(e)}")
            raise BrowserException(f"Failed to create browser: {str(e)}")

    def quit_driver(self, driver: Optional[WebDriver] = None):
        """Close and quit browser driver.
        
        Args:
            driver: WebDriver instance to close (uses self.driver if None)
        """
        try:
            target = driver or self.driver
            if target:
                target.quit()
                logger.info("Browser driver closed")
                if target == self.driver:
                    self.driver = None
        except Exception as e:
            logger.error(f"Error closing driver: {str(e)}")

    def add_random_delay(self, min_sec: float = 1, max_sec: float = 3):
        """Add random delay to simulate human behavior.
        
        Args:
            min_sec: Minimum delay in seconds
            max_sec: Maximum delay in seconds
        """
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)

    def simulate_typing(self, element, text: str, delay: float = 0.1):
        """Simulate human-like typing.
        
        Args:
            element: WebElement to type into
            text: Text to type
            delay: Delay between keystrokes in seconds
        """
        element.clear()
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(delay * 0.5, delay * 1.5))

    def move_mouse_randomly(self, driver: WebDriver):
        """Move mouse to random position (requires undetected-chromedriver)."""
        try:
            from selenium.webdriver.common.action_chains import ActionChains
            actions = ActionChains(driver)
            x = random.randint(0, 1920)
            y = random.randint(0, 1080)
            actions.move_by_offset(x, y).perform()
        except Exception as e:
            logger.debug(f"Could not move mouse: {str(e)}")

    def wait_for_element(self, driver: WebDriver, by, locator, timeout: Optional[int] = None):
        """Wait for element to appear.
        
        Args:
            driver: WebDriver instance
            by: Selenium By selector
            locator: Element locator
            timeout: Timeout in seconds
            
        Returns:
            WebElement
            
        Raises:
            BrowserTimeoutException: If element not found within timeout
        """
        from selenium.webdriver.support import expected_conditions as EC
        
        wait_timeout = timeout or self.timeout
        try:
            wait = WebDriverWait(driver, wait_timeout)
            return wait.until(EC.presence_of_element_located((by, locator)))
        except Exception as e:
            logger.error(f"Timeout waiting for element: {str(e)}")
            raise BrowserTimeoutException(f"Timeout waiting for element: {str(e)}")
