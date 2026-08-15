"""Chapter 4: Generators, Iterators & Coroutines (Reference Solution)."""

from .custom_iterators import ChunkedStream, SlidingWindow
from .stream_pipeline import (
    ResetSignal,
    averager,
    coroutine,
    flatten_tree,
    pipeline_broadcast,
)

__all__ = [
    "SlidingWindow",
    "ChunkedStream",
    "flatten_tree",
    "averager",
    "coroutine",
    "ResetSignal",
    "pipeline_broadcast",
]
