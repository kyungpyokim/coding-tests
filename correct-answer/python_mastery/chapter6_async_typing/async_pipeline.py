import asyncio
from collections.abc import Callable, Coroutine
from typing import Any, TypeVar

T = TypeVar("T")
R = TypeVar("R")


class AsyncConnectionPool:
    def __init__(self, pool_name: str) -> None:
        self.pool_name = pool_name
        self.connected = False

    async def __aenter__(self) -> "AsyncConnectionPool":
        await asyncio.sleep(0.01)
        self.connected = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        await asyncio.sleep(0.01)
        self.connected = False


class AsyncDataStream:
    def __init__(self, items: list[T], delay: float = 0.01) -> None:
        self.items = items
        self.delay = delay
        self._index = 0

    def __aiter__(self) -> "AsyncDataStream[T]":
        return self

    async def __anext__(self) -> T:
        if self._index >= len(self.items):
            raise StopAsyncIteration
        await asyncio.sleep(self.delay)
        item = self.items[self._index]
        self._index += 1
        return item


class AsyncWorkerPool:
    def __init__(self, max_concurrency: int = 3) -> None:
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)

    async def execute_batch(
        self,
        tasks: list[Callable[[], Coroutine[Any, Any, R]]],
    ) -> list[R]:
        results: list[R | None] = [None] * len(tasks)

        async def worker(
            idx: int, task_func: Callable[[], Coroutine[Any, Any, R]]
        ) -> None:
            async with self.semaphore:
                results[idx] = await task_func()

        async with asyncio.TaskGroup() as tg:
            for idx, task_func in enumerate(tasks):
                tg.create_task(worker(idx, task_func))

        return [r for r in results if r is not None]  # type: ignore[misc]
