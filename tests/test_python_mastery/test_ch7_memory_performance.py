import gc
import struct

import pytest

from python_mastery.chapter7_memory_performance import (
    OptimizedNode,
    WeakRefCache,
    ZeroCopyPacketParser,
)


class TestOptimizedNodeAndWeakRef:
    def test_slots_prevents_dict_and_arbitrary_attributes(self):
        node = OptimizedNode(name="root", value=100)
        assert not hasattr(node, "__dict__")

        # Slots attributes work
        assert node.name == "root"
        assert node.value == 100

        # Arbitrary attribute assignment is blocked
        with pytest.raises(AttributeError):
            node.extra_field = "blocked"

    def test_weakref_parent_prevents_cyclic_leak(self):
        parent = OptimizedNode("parent", 1)
        child = OptimizedNode("child", 2, parent=parent)

        assert child.parent is parent

        # Delete parent and trigger GC
        del parent
        gc.collect()

        # Weak ref now resolves to None
        assert child.parent is None

    def test_weak_ref_cache_auto_eviction(self):
        cache = WeakRefCache()

        class Resource:
            def __init__(self, data: str) -> None:
                self.data = data

        r1 = Resource("alpha")
        r2 = Resource("beta")

        cache.set("r1", r1)
        cache.set("r2", r2)
        assert len(cache) == 2
        assert cache.get("r1") is r1

        # Delete r1 and force garbage collection
        del r1
        gc.collect()

        assert cache.get("r1") is None
        assert len(cache) == 1
        assert cache.get("r2") is r2


class TestZeroCopyPacketParser:
    def test_parse_header_and_payload_view(self):
        # Format: 4-byte len=5, 2-byte type=101, payload="HELLO"
        raw = bytearray(struct.pack(">IH", 5, 101) + b"HELLO")
        parser = ZeroCopyPacketParser(raw)

        length, p_type = parser.parse_header(0)
        assert length == 5
        assert p_type == 101

        payload_view = parser.get_payload_view(0)
        assert bytes(payload_view) == b"HELLO"

    def test_inplace_payload_masking_without_copy(self):
        raw = bytearray(struct.pack(">IH", 4, 200) + b"\x01\x02\x03\x04")
        parser = ZeroCopyPacketParser(raw)

        # XOR mask with 0xFF
        parser.mask_payload_inplace(0, 0xFF)

        payload_view = parser.get_payload_view(0)
        assert bytes(payload_view) == b"\xfe\xfd\xfc\xfb"
        # Verify underlying buffer modified directly
        assert raw[6:] == b"\xfe\xfd\xfc\xfb"
