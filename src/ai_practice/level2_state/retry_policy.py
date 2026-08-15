import time
from collections.abc import Callable
from functools import wraps
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
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # 원본 함수의 메타데이터(__name__, __doc__ 등)를 보존
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay
            # 최초 시도 1회 + 재시도 max_retries회 (총 max_retries + 1회)
            for attempt in range(max_retries + 1):
                try:
                    # 원본 함수 호출 및 성공 시 결과 반환
                    return func(*args, **kwargs)
                except retryable_exceptions:
                    # 최대 재시도 횟수에 도달한 경우 마지막 예외를 그대로 발생
                    if attempt == max_retries:
                        raise
                    # 대기 시간만큼 일시 중지 후 지수 백오프 적용 (delay 증가)
                    time.sleep(delay)
                    delay *= backoff_factor

        return wrapper

    return decorator
