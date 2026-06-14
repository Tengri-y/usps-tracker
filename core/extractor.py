"""Data extraction module."""

import re
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from config.constants import USPS_SELECTORS
from utils.logger import logger_instance as logger


class TrackingExtractor:
    """Extract tracking information from USPS page."""

    def __init__(self):
        """Initialize extractor."""
        self.selectors = USPS_SELECTORS

    def extract(self, driver: WebDriver) -> Optional[Dict]:
        """Extract tracking data from driver.
        
        Args:
            driver: Selenium WebDriver instance
            
        Returns:
            Dictionary with tracking data or None if extraction fails
        """
        try:
            page_source = driver.page_source
            
            # Check if page is blank
            if len(page_source) < 2000:
                logger.warning("Page content too small - likely blocked")
                return None
            
            soup = BeautifulSoup(page_source, "html.parser")
            
            # Try to extract tracking number
            tracking_number = self._extract_tracking_number(soup)
            if not tracking_number:
                logger.warning("Could not extract tracking number")
                return None
            
            # Extract status and location
            status = self._extract_status(soup)
            location = self._extract_location(soup)
            
            # Extract events
            events = self._extract_events(soup)
            
            return {
                "tracking_number": tracking_number,
                "status": status,
                "current_location": location,
                "events": events,
                "success": True,
            }
            
        except Exception as e:
            logger.error(f"Error extracting tracking data: {str(e)}")
            return None

    def _extract_tracking_number(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract tracking number from page."""
        try:
            # Try multiple selectors
            patterns = [
                r"tracking['\"]?\s*:\s*['\"]([0-9]{20,34})",
                r"Tracking Number[:\s]+([0-9]{20,34})",
                r"([0-9]{20,34})",
            ]
            
            for pattern in patterns:
                match = re.search(pattern, soup.text, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            logger.error(f"Error extracting tracking number: {str(e)}")
            return None

    def _extract_status(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract delivery status from page."""
        try:
            # Try to find status in common locations
            status_selectors = [
                ".status",
                ".current-status",
                "[class*='status']",
                "h3",
                "h2",
            ]
            
            for selector in status_selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if any(keyword in text.lower() for keyword in 
                           ["delivered", "in transit", "out for delivery", "exception"]):
                        return text
            
            return "Unknown"
        except Exception as e:
            logger.error(f"Error extracting status: {str(e)}")
            return None

    def _extract_location(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract current location from page."""
        try:
            # Try to find location info
            location_selectors = [
                ".location",
                ".current-location",
                "[class*='location']",
            ]
            
            for selector in location_selectors:
                element = soup.select_one(selector)
                if element:
                    text = element.get_text(strip=True)
                    if text and len(text) > 0:
                        return text
            
            return "Location Unknown"
        except Exception as e:
            logger.error(f"Error extracting location: {str(e)}")
            return None

    def _extract_events(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract tracking events from page."""
        try:
            events = []
            
            # Try multiple event selectors
            event_selectors = [
                ".tracking-event",
                ".event",
                "tr[class*='event']",
                "div[class*='event']",
            ]
            
            for selector in event_selectors:
                elements = soup.select(selector)
                if elements:
                    for element in elements:
                        event = self._parse_event(element)
                        if event:
                            events.append(event)
            
            return events
        except Exception as e:
            logger.error(f"Error extracting events: {str(e)}")
            return []

    def _parse_event(self, element) -> Optional[Dict]:
        """Parse single tracking event."""
        try:
            event_text = element.get_text(strip=True)
            
            if not event_text:
                return None
            
            # Try to extract date, location, and status
            date = self._extract_event_date(element)
            location = self._extract_event_location(element)
            status = self._extract_event_status(element)
            
            if date or status:
                return {
                    "date": date or "Unknown",
                    "location": location or "Unknown",
                    "status": status or "Unknown",
                    "detail": event_text[:200],
                }
            
            return None
        except Exception as e:
            logger.debug(f"Error parsing event: {str(e)}")
            return None

    def _extract_event_date(self, element) -> Optional[str]:
        """Extract date from event element."""
        try:
            date_selectors = [".date", ".event-date", "[class*='date']"]
            for selector in date_selectors:
                date_elem = element.select_one(selector)
                if date_elem:
                    return date_elem.get_text(strip=True)
            return None
        except:
            return None

    def _extract_event_location(self, element) -> Optional[str]:
        """Extract location from event element."""
        try:
            location_selectors = [".location", ".event-location", "[class*='location']"]
            for selector in location_selectors:
                loc_elem = element.select_one(selector)
                if loc_elem:
                    return loc_elem.get_text(strip=True)
            return None
        except:
            return None

    def _extract_event_status(self, element) -> Optional[str]:
        """Extract status from event element."""
        try:
            status_selectors = [".status", ".event-status", "[class*='status']"]
            for selector in status_selectors:
                status_elem = element.select_one(selector)
                if status_elem:
                    return status_elem.get_text(strip=True)
            return None
        except:
            return None
