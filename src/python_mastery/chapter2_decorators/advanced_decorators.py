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
    """Parameterized decorator for retrying a function upon failure.

    Features:
    - Retries up to `max_retries` times.
    - Sleeps `backoff_factor * (2 ** attempt)` between retries.
    - Catches only specified `exceptions`.
    - Preserves function metadata via functools.wraps.
    """
    # TODO: 데코레이터 함수와 래퍼 함수를 구현하세요.
    # 성공 시 즉시 결과를 반환하고, 실패 횟수가 초과되면 마지막 예외를 다시 발생시키세요.
    raise NotImplementedError


class RateLimiter:
    """Class-based decorator enforcing rate limits per function.

    Features:
    - Allows up to `max_calls` calls within `period_seconds`.
    - Raises RateLimitExceededError if limit is reached.
    - Provides a `.reset()` method to clear the call history.
    - Preserves function metadata.
    """

    def __init__(self, max_calls: int, period_seconds: float) -> None:
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        # TODO: 타임스탬프 기록을 위한 내부 상태를 초기화하세요.
        raise NotImplementedError

    def __call__(self, func: F) -> F:
        # TODO: 래퍼 함수를 정의하고, 현재 시간 기준 슬라이딩 윈도우 내 호출 횟수를 검사하세요.
        # 래퍼 객체에 reset() 메서드를 바인딩하고 wraps를 적용해 반환하세요.
        raise NotImplementedError


def cache_with_ttl(
    ttl_seconds: float = 60.0,
    maxsize: int = 128,
) -> Callable[[F], F]:
    """Cache decorator with Time-To-Live (TTL) expiration and max capacity.

    Features:
    - Caches return value keyed by (args, tuple(sorted(kwargs.items()))).
    - Evicts entry if elapsed time >= `ttl_seconds`.
    - Evicts oldest entries if len(cache) >= `maxsize`.
    - Exposes `.cache_clear()` and `.cache_info()` returning dict(hits, misses, currsize).
    """
    # TODO: TTL 캐시 래퍼 및 캐시 메타데이터 관리 함수를 구현하세요.
    raise NotImplementedError
