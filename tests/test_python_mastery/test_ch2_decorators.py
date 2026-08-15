import time
from dataclasses import dataclass
from datetime import datetime

import pytest

from python_mastery.chapter2_decorators import (
    DataPipeline,
    RateLimiter,
    RateLimitExceededError,
    cache_with_ttl,
    retry,
    serialize,
)


class TestRetryDecorator:
    def test_retry_eventual_success(self):
        attempts = 0

        @retry(max_retries=3, backoff_factor=0.01, exceptions=(ValueError,))
        def flaky_func(val: int) -> int:
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise ValueError("Temporary failure")
            return val * 10

        assert flaky_func(5) == 50
        assert attempts == 3
        assert flaky_func.__name__ == "flaky_func"

    def test_retry_exhausted_raises(self):
        attempts = 0

        @retry(max_retries=2, backoff_factor=0.01, exceptions=(KeyError,))
        def always_fails():
            nonlocal attempts
            attempts += 1
            raise KeyError("Key not found")

        with pytest.raises(KeyError, match="Key not found"):
            always_fails()
        assert attempts == 3  # Initial try + 2 retries


class TestRateLimiter:
    def test_rate_limiter_allows_under_limit(self):
        calls = 0

        @RateLimiter(max_calls=3, period_seconds=0.5)
        def limited_action():
            nonlocal calls
            calls += 1
            return calls

        assert limited_action() == 1
        assert limited_action() == 2
        assert limited_action() == 3

    def test_rate_limiter_blocks_and_resets(self):
        @RateLimiter(max_calls=2, period_seconds=0.2)
        def action():
            return "ok"

        assert action() == "ok"
        assert action() == "ok"

        with pytest.raises(RateLimitExceededError):
            action()

        # Reset explicitly
        action.reset()
        assert action() == "ok"

        # Wait for period to expire
        action()  # 2nd call
        time.sleep(0.25)
        assert action() == "ok"  # Window slid


class TestCacheWithTTL:
    def test_cache_hit_and_miss(self):
        call_count = 0

        @cache_with_ttl(ttl_seconds=0.2, maxsize=2)
        def compute(x: int, y: int = 0) -> int:
            nonlocal call_count
            call_count += 1
            return x + y

        assert compute(2, y=3) == 5
        assert call_count == 1
        info = compute.cache_info()
        assert info["hits"] == 0 and info["misses"] == 1

        # Cache hit
        assert compute(2, y=3) == 5
        assert call_count == 1
        assert compute.cache_info()["hits"] == 1

        # Wait for TTL expiration
        time.sleep(0.25)
        assert compute(2, y=3) == 5
        assert call_count == 2
        assert compute.cache_info()["misses"] == 2

    def test_cache_clear(self):
        @cache_with_ttl(ttl_seconds=10.0, maxsize=5)
        def get_val(n: int) -> int:
            return n * 2

        get_val(1)
        get_val(2)
        assert get_val.cache_info()["currsize"] == 2
        get_val.cache_clear()
        assert get_val.cache_info()["currsize"] == 0


class TestSingleDispatch:
    def test_serialize_primitives(self):
        assert serialize(42) == 42
        assert serialize(3.14) == 3.14
        assert serialize(True) is True
        assert serialize("hello") == "hello"

    def test_serialize_collections(self):
        data = {"numbers": [1, 2], "active": True}
        assert serialize(data) == {"numbers": [1, 2], "active": True}

        # Set converted to list
        res = serialize({10, 20})
        assert isinstance(res, list)
        assert set(res) == {10, 20}

    def test_serialize_datetime_and_dataclass(self):
        dt = datetime(2026, 8, 15, 12, 0, 0)
        assert serialize(dt) == "2026-08-15T12:00:00"

        @dataclass
        class User:
            name: str
            joined: datetime

        u = User(name="Alice", joined=dt)
        serialized = serialize(u)
        assert serialized == {"name": "Alice", "joined": "2026-08-15T12:00:00"}

    def test_pipeline_singledispatchmethod(self):
        pipeline = DataPipeline(prefix="TEST")

        assert pipeline.process("python") == "[TEST] TEXT(6): PYTHON"
        assert pipeline.process(5) == "[TEST] NUM: 10"
        assert pipeline.process([1, "a"]) == "[TEST] BATCH(2): [1, a]"
        assert "UNKNOWN" in pipeline.process(object())
