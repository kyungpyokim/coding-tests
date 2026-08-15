import asyncio

import pytest

from python_mastery.chapter6_async_typing import (
    AsyncConnectionPool,
    AsyncDataStream,
    AsyncWorkerPool,
    GenericStack,
    Serializable,
    format_output,
)


class TestStructuralTyping:
    def test_protocol_duck_typing(self):
        class UserDict:
            def to_dict(self):
                return {"user": "Alice"}

        class PlainObject:
            pass

        assert isinstance(UserDict(), Serializable)
        assert not isinstance(PlainObject(), Serializable)

    def test_generic_stack(self):
        stack = GenericStack[int]()
        stack.push(10)
        stack.push(20)
        assert len(stack) == 2
        assert stack.peek() == 20
        assert stack.pop() == 20
        assert stack.pop() == 10

        with pytest.raises(IndexError):
            stack.pop()

    def test_format_output_overloads(self):
        assert format_output(42) == "NUM:42"
        assert format_output(["hello", "world"]) == 10

        class Article:
            def to_dict(self):
                return {"title": "Python Deep Dive"}

        assert format_output(Article()) == {"title": "Python Deep Dive"}

        with pytest.raises(TypeError):
            format_output(3.14)


class TestAsyncPipelines:
    @pytest.mark.asyncio
    async def test_async_connection_pool(self):
        pool = AsyncConnectionPool("PrimaryDB")
        assert pool.connected is False

        async with pool as conn:
            assert conn.connected is True

        assert pool.connected is False

    @pytest.mark.asyncio
    async def test_async_data_stream(self):
        stream = AsyncDataStream(["a", "b", "c"], delay=0.01)
        collected = []
        async for item in stream:
            collected.append(item)

        assert collected == ["a", "b", "c"]

    @pytest.mark.asyncio
    async def test_async_worker_pool_concurrency(self):
        pool = AsyncWorkerPool(max_concurrency=2)
        concurrent_count = 0
        max_seen = 0

        async def slow_task(val: int) -> int:
            nonlocal concurrent_count, max_seen
            concurrent_count += 1
            max_seen = max(max_seen, concurrent_count)
            await asyncio.sleep(0.05)
            concurrent_count -= 1
            return val * 2

        tasks = [lambda v=i: slow_task(v) for i in range(5)]
        results = await pool.execute_batch(tasks)

        assert results == [0, 2, 4, 6, 8]
        assert max_seen <= 2  # Bounded by semaphore
