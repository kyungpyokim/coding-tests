import functools
import time
from collections import OrderedDict
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class RateLimitExceededError(Exception):
    """Raised when call count exceeds limit in a given time window."""


def retry(
    max_retries: int = 3,
    backoff_factor: float = 0.05,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_err: Exception | None = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_err = e
                    if attempt < max_retries:
                        sleep_time = backoff_factor * (2**attempt)
                        time.sleep(sleep_time)
                    else:
                        raise last_err from None
            raise last_err or RuntimeError("Retry loop terminated unexpectedly")

        return wrapper  # type: ignore[return-value]

    return decorator


class RateLimiter:
    def __init__(self, max_calls: int, period_seconds: float) -> None:
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self._timestamps: list[float] = []

    def reset(self) -> None:
        self._timestamps.clear()

    def __call__(self, func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            now = time.monotonic()
            cutoff = now - self.period_seconds
            # Remove timestamps outside the window
            self._timestamps = [t for t in self._timestamps if t > cutoff]

            if len(self._timestamps) >= self.max_calls:
                raise RateLimitExceededError(
                    f"Rate limit exceeded: {self.max_calls} calls per {self.period_seconds}s"
                )

            self._timestamps.append(now)
            return func(*args, **kwargs)

        wrapper.reset = self.reset  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]


def cache_with_ttl(
    ttl_seconds: float = 60.0,
    maxsize: int = 128,
) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        cache: OrderedDict[Any, tuple[Any, float]] = OrderedDict()
        stats = {"hits": 0, "misses": 0}

        def make_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[Any, ...]:
            kw_items = tuple(sorted(kwargs.items()))
            return (args, kw_items)

        def cache_clear() -> None:
            cache.clear()
            stats["hits"] = 0
            stats["misses"] = 0

        def cache_info() -> dict[str, int]:
            return {
                "hits": stats["hits"],
                "misses": stats["misses"],
                "currsize": len(cache),
            }

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = make_key(args, kwargs)
            now = time.monotonic()

            if key in cache:
                val, timestamp = cache[key]
                if now - timestamp < ttl_seconds:
                    stats["hits"] += 1
                    cache.move_to_end(key)
                    return val
                else:
                    del cache[key]

            stats["misses"] += 1
            result = func(*args, **kwargs)

            if len(cache) >= maxsize:
                cache.popitem(last=False)  # Evict LRU

            cache[key] = (result, now)
            return result

        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
        wrapper.cache_info = cache_info  # type: ignore[attr-defined]
        return wrapper  # type: ignore[return-value]

    return decorator
