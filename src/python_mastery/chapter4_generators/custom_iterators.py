from collections import deque
from collections.abc import Iterable, Iterator
from typing import TypeVar

T = TypeVar("T")


class SlidingWindow(Iterator[tuple[T, ...]]):
    """Custom Iterator maintaining a sliding window over an iterable.

    Demonstrates Low-Level Iterator Protocol:
    - __iter__(self) returns self
    - __next__(self) produces the next window tuple, or raises StopIteration
    - Uses collections.deque(maxlen=size) for O(1) sliding window updates.
    """

    def __init__(self, iterable: Iterable[T], size: int, step: int = 1) -> None:
        """Initialize SlidingWindow.

        Raises:
            ValueError: If size < 1 or step < 1.
        """
        if size < 1 or step < 1:
            raise ValueError("size and step must be positive integers >= 1")
        self._iterator = iter(iterable)
        self._size = size
        self._step = step
        self._window: deque[T] = deque(maxlen=size)
        self._is_first = True

    def __iter__(self) -> "SlidingWindow[T]":
        # TODO: self를 반환하세요.
        raise NotImplementedError

    def __next__(self) -> tuple[T, ...]:
        # TODO: 첫 번째 윈도우 채우기 및 이후 step 만큼 요소를 밀어내며 다음 윈도우 튜플을 반환하세요.
        # 더 이상 채울 수 없으면 StopIteration을 발생시키세요.
        raise NotImplementedError


def ChunkedStream(iterable: Iterable[T], chunk_size: int) -> Iterator[list[T]]:
    """Generator yielding chunks of up to `chunk_size` elements from iterable."""
    # TODO: 제너레이터(yield)를 이용해 chunk_size 만큼의 리스트 청크를 순차적으로 방출하세요.
    raise NotImplementedError
