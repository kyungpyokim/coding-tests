from collections import deque
from collections.abc import Iterable, Iterator
from typing import TypeVar

T = TypeVar("T")


class SlidingWindow(Iterator[tuple[T, ...]]):
    def __init__(self, iterable: Iterable[T], size: int, step: int = 1) -> None:
        if size < 1 or step < 1:
            raise ValueError("size and step must be positive integers >= 1")
        self._iterator = iter(iterable)
        self._size = size
        self._step = step
        self._window: deque[T] = deque(maxlen=size)
        self._is_first = True

    def __iter__(self) -> "SlidingWindow[T]":
        return self

    def __next__(self) -> tuple[T, ...]:
        if self._is_first:
            for _ in range(self._size):
                try:
                    self._window.append(next(self._iterator))
                except StopIteration:
                    break
            if len(self._window) < self._size:
                raise StopIteration
            self._is_first = False
            return tuple(self._window)

        # Advance by step elements
        for _ in range(self._step):
            self._window.append(next(self._iterator))

        return tuple(self._window)


def ChunkedStream(iterable: Iterable[T], chunk_size: int) -> Iterator[list[T]]:
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")
    iterator = iter(iterable)
    while True:
        chunk: list[T] = []
        for _ in range(chunk_size):
            try:
                chunk.append(next(iterator))
            except StopIteration:
                break
        if not chunk:
            break
        yield chunk
