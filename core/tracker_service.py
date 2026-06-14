"""Main tracking service."""

import time
import random
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings
from core.proxy_manager import ProxyManager
from core.browser_manager import BrowserManager
from core.extractor import TrackingExtractor
from core.exceptions import (
    InvalidTrackingNumberException,
    PageBlockedException,
    TrackingException,
)
from utils.logger import logger_instance as logger
from utils.headers_builder import HeadersBuilder

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class TrackerService:
    """Main service for USPS package tracking."""

    def __init__(self, settings=settings):
        """Initialize tracker service.
        
        Args:
            settings: Settings instance
        """
        self.settings = settings
        self.proxy_manager = ProxyManager(
            proxy_list=settings.get_proxy_list(),
            rotation_strategy=settings.proxy_rotation_strategy,
        )
        self.browser_manager = BrowserManager(
            headless=settings.headless,
            timeout=settings.browser_timeout,
        )
        self.extractor = TrackingExtractor()
        self.headers_builder = HeadersBuilder()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10),
    )
    def track_package(self, tracking_number: str) -> Dict:
        """Track single package.
        
        Args:
            tracking_number: USPS tracking number
            
        Returns:
            Dictionary with tracking information
        """
        if not self._validate_tracking_number(tracking_number):
            raise InvalidTrackingNumberException(
                f"Invalid tracking number: {tracking_number}"
            )

        driver = None
        try:
            # Get proxy
            proxy = None
            if self.settings.proxy_enabled:
                proxy = self.proxy_manager.get_next_proxy()
                if not proxy:
                    logger.warning("No proxy available, attempting direct connection")

            # Create browser
            driver = self.browser_manager.create_driver_with_proxy(proxy)

            # Navigate to tracking page
            logger.info(f"Navigating to USPS tracking page for {tracking_number}")
            driver.get(self.settings.usps_tracking_url)

            # Add random delay
            self.browser_manager.add_random_delay(2, 4)

            # Find and fill tracking number input
            try:
                input_field = driver.find_element(By.ID, "tracking-input")
            except:
                input_field = driver.find_element(By.CSS_SELECTOR, "input[name='tracking-input']")

            # Simulate human typing
            self.browser_manager.simulate_typing(input_field, tracking_number)

            # Add delay before clicking
            self.browser_manager.add_random_delay(1, 2)

            # Click track button
            try:
                track_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            except:
                track_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Track')]")

            track_button.click()

            # Wait for results
            time.sleep(random.uniform(3, 5))

            # Check if page was blocked
            page_source = driver.page_source
            if len(page_source) < 1500:
                logger.warning(f"Page blocked for {tracking_number}")
                if proxy:
                    self.proxy_manager.mark_proxy_bad(proxy)
                raise PageBlockedException("USPS blocked the request")

            # Extract data
            tracking_data = self.extractor.extract(driver)

            if tracking_data:
                if proxy:
                    self.proxy_manager.mark_proxy_good(proxy)
                logger.info(f"Successfully tracked: {tracking_number}")
                return {
                    "status": "success",
                    "tracking_number": tracking_number,
                    "data": tracking_data,
                }
            else:
                if proxy:
                    self.proxy_manager.mark_proxy_bad(proxy)
                return {
                    "status": "failed",
                    "tracking_number": tracking_number,
                    "error": "Could not extract tracking data",
                }

        except PageBlockedException as e:
            logger.error(f"Page blocked: {str(e)}")
            return {
                "status": "blocked",
                "tracking_number": tracking_number,
                "error": "USPS detected and blocked the request",
            }
        except InvalidTrackingNumberException as e:
            return {
                "status": "invalid",
                "tracking_number": tracking_number,
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"Tracking error for {tracking_number}: {str(e)}")
            return {
                "status": "error",
                "tracking_number": tracking_number,
                "error": str(e),
            }
        finally:
            if driver:
                self.browser_manager.quit_driver(driver)

    def batch_track(
        self,
        tracking_numbers: List[str],
        max_workers: int = None,
        callback=None,
    ) -> List[Dict]:
        """Track multiple packages concurrently.
        
        Args:
            tracking_numbers: List of tracking numbers
            max_workers: Number of concurrent workers
            callback: Optional callback for each completed tracking
            
        Returns:
            List of tracking results
        """
        max_workers = max_workers or self.settings.max_workers
        results = []

        logger.info(f"Starting batch tracking of {len(tracking_numbers)} packages")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self.track_package, tn): tn
                for tn in tracking_numbers
            }

            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)

                    if callback:
                        callback(result)

                    # Add delay between requests
                    time.sleep(random.uniform(1, 2))

                except Exception as e:
                    tracking_number = futures[future]
                    logger.error(f"Error tracking {tracking_number}: {str(e)}")
                    results.append({
                        "status": "error",
                        "tracking_number": tracking_number,
                        "error": str(e),
                    })

        logger.info(f"Batch tracking completed. Results: {len(results)}")
        return results

    def _validate_tracking_number(self, tracking_number: str) -> bool:
        """Validate USPS tracking number format.
        
        Args:
            tracking_number: Tracking number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # USPS tracking numbers are typically 20-34 digits
        import re
        return bool(re.match(r"^\d{20,34}$", str(tracking_number).strip()))

    def get_proxy_stats(self) -> Dict:
        """Get proxy pool statistics."""
        return self.proxy_manager.get_proxy_stats()
