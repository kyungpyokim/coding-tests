import functools
from collections.abc import Callable, Generator, Iterator
from typing import Any, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def flatten_tree(tree: Any) -> Iterator[Any]:
    """Recursively flatten nested lists, tuples, or dict values using `yield from`.

    Leaves (non-containers or strings/bytes) are yielded directly.
    """
    # TODO: `yield from`을 활용하여 중첩된 트리/리스트/딕셔너리의 리프 노드들을 평탄화하여 yield 하세요.
    raise NotImplementedError


def coroutine(
    func: Callable[..., Generator[R, T, Any]],
) -> Callable[..., Generator[R, T, Any]]:
    """Decorator that automatically primes a generator coroutine (calls next())."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Generator[R, T, Any]:
        # TODO: func(*args, **kwargs)를 호출하여 제너레이터를 얻고,
        # next()를 한 번 호출하여 priming한 뒤 반환하세요.
        raise NotImplementedError

    return wrapper


class ResetSignal(Exception):
    """Signal exception sent via .throw() to reset coroutine state."""


def averager() -> Generator[tuple[int, float], float, tuple[int, float]]:
    """Bi-directional generator coroutine.

    - Receives numbers via `.send(val)`.
    - Yields `(count, current_average)` after each receive.
    - Catches `ResetSignal` (via `.throw(ResetSignal)`) and resets count and total to 0.
    - When closed / terminated, returns the final `(count, average)` via return statement.
    """
    # TODO: 무한 루프 내에서 yield로 값을 전달받고 계산된 튜플을 반환하세요.
    # try-except로 ResetSignal을 잡아 상태를 초기화하세요.
    raise NotImplementedError


@coroutine
def pipeline_broadcast(
    targets: list[Generator[None, Any, Any]],
) -> Generator[None, Any, None]:
    """Coroutine that broadcasts incoming items to all target coroutines."""
    # TODO: 들어오는 item을 targets의 모든 코루틴에 .send(item) 하세요.
    raise NotImplementedError
