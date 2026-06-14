"""Custom exceptions for USPS Tracker."""


class USPSTrackerException(Exception):
    """Base exception for USPS Tracker."""
    pass


class ProxyException(USPSTrackerException):
    """Exception related to proxy operations."""
    pass


class ProxyUnavailableException(ProxyException):
    """Exception when no proxy is available."""
    pass


class BrowserException(USPSTrackerException):
    """Exception related to browser operations."""
    pass


class BrowserTimeoutException(BrowserException):
    """Exception when browser operation times out."""
    pass


class TrackingException(USPSTrackerException):
    """Exception related to tracking operations."""
    pass


class InvalidTrackingNumberException(TrackingException):
    """Exception for invalid tracking number."""
    pass


class TrackingNotFoundException(TrackingException):
    """Exception when tracking number is not found."""
    pass


class PageBlockedException(TrackingException):
    """Exception when page is blocked by USPS."""
    pass
