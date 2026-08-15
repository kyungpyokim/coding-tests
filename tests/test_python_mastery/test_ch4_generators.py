from python_mastery.chapter4_generators import (
    ChunkedStream,
    ResetSignal,
    SlidingWindow,
    averager,
    coroutine,
    flatten_tree,
    pipeline_broadcast,
)


class TestCustomIterators:
    def test_sliding_window_basic(self):
        items = [1, 2, 3, 4, 5]
        sw = SlidingWindow(items, size=3, step=1)
        assert list(sw) == [(1, 2, 3), (2, 3, 4), (3, 4, 5)]

    def test_sliding_window_step(self):
        items = [1, 2, 3, 4, 5, 6]
        sw = SlidingWindow(items, size=2, step=2)
        assert list(sw) == [(1, 2), (3, 4), (5, 6)]

    def test_sliding_window_shorter_than_size(self):
        items = [1, 2]
        sw = SlidingWindow(items, size=3)
        assert list(sw) == []

    def test_chunked_stream(self):
        data = range(10)
        chunks = list(ChunkedStream(data, chunk_size=3))
        assert chunks == [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]


class TestStreamPipeline:
    def test_flatten_tree(self):
        nested = [1, [2, 3, [4, 5]], {"a": 6, "b": [7, 8]}, (9, 10)]
        result = list(flatten_tree(nested))
        assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def test_averager_coroutine_send_and_throw(self):
        avg_gen = averager()
        next(avg_gen)  # Prime

        assert avg_gen.send(10) == (1, 10.0)
        assert avg_gen.send(20) == (2, 15.0)
        assert avg_gen.send(30) == (3, 20.0)

        # Reset via throw
        avg_gen.throw(ResetSignal)
        assert avg_gen.send(100) == (1, 100.0)

    def test_pipeline_broadcast(self):
        collector_a = []
        collector_b = []

        @coroutine
        def target_a():
            while True:
                item = yield
                collector_a.append(item * 2)

        @coroutine
        def target_b():
            while True:
                item = yield
                collector_b.append(f"val-{item}")

        t_a = target_a()
        t_b = target_b()

        broadcaster = pipeline_broadcast([t_a, t_b])
        broadcaster.send(10)
        broadcaster.send(20)

        assert collector_a == [20, 40]
        assert collector_b == ["val-10", "val-20"]
