"""Custom exceptions for DEGIRO API handling."""

from typing import Optional, Dict, Any


class DEGIROError(Exception):
    """Base exception for all DEGIRO-related errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class AuthenticationError(DEGIROError):
    """Raised when authentication fails."""
    pass


class SessionExpiredError(DEGIROError):
    """Raised when the session has expired."""
    pass


class RateLimitError(DEGIROError):
    """Raised when API rate limit is exceeded."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class InvalidRequestError(DEGIROError):
    """Raised when the API request is invalid."""
    pass


class ProductNotFoundError(DEGIROError):
    """Raised when a requested product is not found."""
    pass


class InsufficientFundsError(DEGIROError):
    """Raised when there are insufficient funds for an operation."""
    pass


class OrderValidationError(DEGIROError):
    """Raised when order validation fails."""
    pass


class MarketClosedError(DEGIROError):
    """Raised when attempting to trade while market is closed."""
    
    def __init__(self, message: str, market_open_time: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.market_open_time = market_open_time


class APITimeoutError(DEGIROError):
    """Raised when API request times out."""
    pass


class ConnectionError(DEGIROError):
    """Raised when connection to API fails."""
    pass


class DataParsingError(DEGIROError):
    """Raised when API response cannot be parsed."""
    pass


def handle_degiro_error(error: Exception) -> DEGIROError:
    """
    Convert degiro-connector exceptions to our custom exceptions.
    
    Args:
        error: Original exception from degiro-connector
        
    Returns:
        Appropriate custom exception
    """
    from degiro_connector.core.exceptions import DeGiroConnectionError
    
    error_message = str(error)
    
    # Map degiro-connector exceptions
    if isinstance(error, DeGiroConnectionError):
        if "authentication" in error_message.lower() or "login" in error_message.lower():
            return AuthenticationError(error_message, {"original_error": type(error).__name__})
        elif "session" in error_message.lower():
            return SessionExpiredError(error_message, {"original_error": type(error).__name__})
        else:
            return ConnectionError(error_message, {"original_error": type(error).__name__})
    
    # Additional error handling based on error message content
    elif "timeout" in error_message.lower():
        return APITimeoutError(error_message, {"original_error": type(error).__name__})
    elif "rate limit" in error_message.lower():
        return RateLimitError(error_message)
    elif "invalid" in error_message.lower():
        return InvalidRequestError(error_message)
    elif "not found" in error_message.lower():
        return ProductNotFoundError(error_message)
    elif "insufficient" in error_message.lower():
        return InsufficientFundsError(error_message)
    elif "market closed" in error_message.lower():
        return MarketClosedError(error_message)
    
    # Generic errors
    elif isinstance(error, ValueError):
        return DataParsingError(f"Failed to parse data: {error_message}")
    
    elif isinstance(error, ConnectionError):
        return ConnectionError(f"Network error: {error_message}")
    
    # Default fallback
    return DEGIROError(f"Unexpected error: {error_message}", {"original_error": type(error).__name__})