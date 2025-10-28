"""
Utility functions for Lambda handlers
"""

import time
from functools import wraps
from typing import Callable, Any, TypeVar, ParamSpec

P = ParamSpec('P')
T = TypeVar('T')


def retry_with_backoff(max_retries: int = 3, initial_backoff: float = 0.1):
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff delay in seconds
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            import structlog
            logger = structlog.get_logger()
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt < max_retries - 1:
                        backoff_delay = initial_backoff * (2 ** attempt)
                        logger.warning(
                            "Retrying after error",
                            function=func.__name__,
                            attempt=attempt + 1,
                            error=str(e)
                        )
                        time.sleep(backoff_delay)
                    else:
                        logger.error(
                            "Max retries exceeded",
                            function=func.__name__,
                            error=str(e)
                        )
                        raise
            
            raise Exception("Retry logic failed")
        
        return wrapper
    return decorator


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID
    
    Args:
        prefix: Optional prefix for the ID
    
    Returns:
        Unique ID string
    """
    import uuid
    id_value = str(uuid.uuid4())
    
    if prefix:
        return f"{prefix}-{id_value}"
    return id_value


def validate_required_fields(data: dict, required_fields: list[str]) -> tuple[bool, str]:
    """
    Validate that required fields are present in data
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, ""


def calculate_ttl(days: int) -> int:
    """
    Calculate TTL timestamp from current time
    
    Args:
        days: Number of days until expiration
    
    Returns:
        Unix timestamp for TTL
    """
    return int(time.time()) + (days * 24 * 60 * 60)

