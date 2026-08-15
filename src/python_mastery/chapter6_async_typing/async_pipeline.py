import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class AsyncConnectionPool:
    """Asynchronous Context Manager managing mock DB connections.

    Demonstrates:
    - __aenter__(self): asynchronously acquires connection
    - __aexit__(self, exc_type, exc_val, exc_tb): asynchronously releases connection
    """

    def __init__(self, pool_name: str) -> None:
        self.pool_name = pool_name
        self.connected = False

    async def __aenter__(self) -> "AsyncConnectionPool":
        # TODO: self.connected = True 로 설정하고 0.01초 대기(asyncio.sleep) 후 self를 반환하세요.
        raise NotImplementedError

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        # TODO: self.connected = False 로 설정하고 0.01초 대기 후 종료하세요.
        raise NotImplementedError


class AsyncDataStream:
    """Asynchronous Iterator generating streaming items asynchronously.

    Demonstrates:
    - __aiter__(self): returns self
    - __anext__(self): asynchronously fetches next item or raises StopAsyncIteration
    """

    def __init__(self, items: list[T], delay: float = 0.01) -> None:
        self.items = items
        self.delay = delay
        self._index = 0

    def __aiter__(self) -> "AsyncDataStream[T]":
        # TODO: self를 반환하세요.
        raise NotImplementedError

    async def __anext__(self) -> T:
        # TODO: 다음 요소가 있으면 asyncio.sleep(delay) 후 반환하고, 없으면 StopAsyncIteration을 발생시키세요.
        raise NotImplementedError


class AsyncWorkerPool:
    """Manages concurrent worker execution using asyncio.TaskGroup & asyncio.Semaphore."""

    def __init__(self, max_concurrency: int = 3) -> None:
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def execute_batch(
        self,
        tasks: list[Callable[[], Coroutine[Any, Any, R]]],
    ) -> list[R]:
        """Execute tasks concurrently bounded by semaphore, using asyncio.TaskGroup."""
        # TODO: TaskGroup(Python 3.11+)과 semaphore를 사용하여 tasks를 병렬 실행하고,
        # 모든 결과 리스트를 원래 입력 순서대로 반환하세요.
        raise NotImplementedError
