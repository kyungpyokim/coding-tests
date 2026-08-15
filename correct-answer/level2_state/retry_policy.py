import functools
import time
from collections.abc import Callable
from typing import Any


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 0.1,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that retries a function with exponential backoff on specified exceptions."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions:
                    if attempt == max_retries:
                        raise
                    time.sleep(delay)
                    delay *= backoff_factor

        return wrapper

    return decorator
