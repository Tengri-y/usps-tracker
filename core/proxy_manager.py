"""Proxy management module."""

import random
from itertools import cycle
from typing import Optional, List
from utils.logger import logger_instance as logger


class ProxyManager:
    """Manage proxy rotation and fallback."""

    def __init__(self, proxy_list: List[str] = None, rotation_strategy: str = "round_robin"):
        """Initialize proxy manager.
        
        Args:
            proxy_list: List of proxy URLs
            rotation_strategy: 'round_robin' or 'random'
        """
        self.proxy_list = proxy_list or []
        self.rotation_strategy = rotation_strategy
        self.good_proxies = set(proxy_list) if proxy_list else set()
        self.bad_proxies = set()
        
        if rotation_strategy == "round_robin":
            self.proxy_cycle = cycle(self.proxy_list) if self.proxy_list else None
        
    def get_next_proxy(self) -> Optional[str]:
        """Get next proxy from pool.
        
        Returns:
            Proxy URL or None if no proxies available
        """
        if not self.proxy_list:
            return None
            
        available = [p for p in self.proxy_list if p not in self.bad_proxies]
        
        if not available:
            logger.warning("No available proxies, resetting bad proxies list")
            self.bad_proxies.clear()
            available = self.proxy_list
        
        if self.rotation_strategy == "round_robin":
            return next(self.proxy_cycle)
        else:  # random
            return random.choice(available)
    
    def mark_proxy_bad(self, proxy: str):
        """Mark proxy as bad (temporarily unavailable)."""
        if proxy in self.proxy_list:
            self.bad_proxies.add(proxy)
            logger.warning(f"Marked proxy as bad: {proxy}")
    
    def mark_proxy_good(self, proxy: str):
        """Mark proxy as good."""
        if proxy in self.bad_proxies:
            self.bad_proxies.discard(proxy)
            logger.info(f"Marked proxy as good: {proxy}")
    
    def add_proxy(self, proxy: str):
        """Add new proxy to pool."""
        if proxy not in self.proxy_list:
            self.proxy_list.append(proxy)
            if self.rotation_strategy == "round_robin":
                self.proxy_cycle = cycle(self.proxy_list)
            logger.info(f"Added proxy: {proxy}")
    
    def remove_proxy(self, proxy: str):
        """Remove proxy from pool."""
        if proxy in self.proxy_list:
            self.proxy_list.remove(proxy)
            self.bad_proxies.discard(proxy)
            if self.rotation_strategy == "round_robin":
                self.proxy_cycle = cycle(self.proxy_list)
            logger.info(f"Removed proxy: {proxy}")
    
    def get_proxy_stats(self) -> dict:
        """Get proxy pool statistics."""
        return {
            "total": len(self.proxy_list),
            "available": len(self.proxy_list) - len(self.bad_proxies),
            "bad": len(self.bad_proxies),
        }
