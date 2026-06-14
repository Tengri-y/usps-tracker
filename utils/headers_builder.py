"""Build realistic browser headers."""

from config.constants import BASE_HEADERS
from utils.ua_rotator import UARotator


class HeadersBuilder:
    """Build realistic HTTP headers that mimic a real browser."""

    def __init__(self):
        """Initialize headers builder."""
        self.ua_rotator = UARotator()

    def build_headers(self) -> dict:
        """Build realistic headers with random User-Agent.
        
        Returns:
            Dictionary of HTTP headers
        """
        headers = BASE_HEADERS.copy()
        headers["User-Agent"] = self.ua_rotator.get_random_ua()
        headers["Referer"] = "https://tools.usps.com/"
        headers["Origin"] = "https://tools.usps.com"
        return headers

    def build_headers_with_ua(self, ua: str) -> dict:
        """Build headers with specific User-Agent.
        
        Args:
            ua: User-Agent string
            
        Returns:
            Dictionary of HTTP headers
        """
        headers = BASE_HEADERS.copy()
        headers["User-Agent"] = ua
        headers["Referer"] = "https://tools.usps.com/"
        headers["Origin"] = "https://tools.usps.com"
        return headers
