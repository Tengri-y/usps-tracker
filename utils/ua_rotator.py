"""User-Agent rotation utilities."""

import random
from config.constants import USER_AGENTS


class UARotator:
    """Rotate User-Agent strings to avoid detection."""

    def __init__(self, ua_list=None):
        """Initialize with optional custom UA list.
        
        Args:
            ua_list: Custom list of User-Agent strings
        """
        self.ua_list = ua_list or USER_AGENTS

    def get_random_ua(self) -> str:
        """Get a random User-Agent string.
        
        Returns:
            Random User-Agent string
        """
        return random.choice(self.ua_list)

    def get_ua_for_platform(self, platform: str) -> str:
        """Get User-Agent for specific platform.
        
        Args:
            platform: Platform name ('windows', 'mac', 'linux')
            
        Returns:
            User-Agent string for platform
        """
        platform_ua_map = {
            "windows": [ua for ua in self.ua_list if "Windows" in ua],
            "mac": [ua for ua in self.ua_list if "Macintosh" in ua],
            "linux": [ua for ua in self.ua_list if "Linux" in ua or "X11" in ua],
        }
        ua_list = platform_ua_map.get(platform.lower(), self.ua_list)
        return random.choice(ua_list) if ua_list else self.get_random_ua()
