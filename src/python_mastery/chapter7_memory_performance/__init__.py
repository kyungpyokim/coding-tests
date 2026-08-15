"""Chapter 7: Memory Internals & Zero-Copy."""

from .slots_and_weakref import OptimizedNode, WeakRefCache
from .zerocopy_buffer import ZeroCopyPacketParser

__all__ = ["OptimizedNode", "WeakRefCache", "ZeroCopyPacketParser"]
