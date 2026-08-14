from collections.abc import Callable
from typing import Any


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 0.1,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator that retries a function with exponential backoff on specified exceptions."""
    # TODO: 데코레이터 함수를 구현하세요.
    # 함수 실행 중 retryable_exceptions에 해당하는 예외가 발생하면 time.sleep(delay) 후 재시도하고,
    # delay는 backoff_factor 배수만큼 증가시키며, max_retries 초과 시 마지막 예외를 발생시키세요.
    raise NotImplementedError
