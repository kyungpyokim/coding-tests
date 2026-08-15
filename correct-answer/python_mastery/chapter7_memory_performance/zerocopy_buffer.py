import struct


class ZeroCopyPacketParser:
    HEADER_SIZE = 6  # 4 bytes length + 2 bytes type

    def __init__(self, raw_buffer: bytearray) -> None:
        if not isinstance(raw_buffer, bytearray):
            raise TypeError("Buffer must be a mutable bytearray")
        self._buffer = raw_buffer
        self._view = memoryview(self._buffer)

    @property
    def buffer(self) -> bytearray:
        return self._buffer

    def parse_header(self, offset: int = 0) -> tuple[int, int]:
        if offset + self.HEADER_SIZE > len(self._buffer):
            raise ValueError(
                f"Offset {offset} + header exceeds buffer size {len(self._buffer)}"
            )
        length, p_type = struct.unpack_from(">IH", self._view, offset)
        return (length, p_type)

    def get_payload_view(self, offset: int = 0) -> memoryview:
        payload_len, _ = self.parse_header(offset)
        start = offset + self.HEADER_SIZE
        end = start + payload_len
        if end > len(self._buffer):
            raise ValueError(
                f"Payload end {end} exceeds buffer size {len(self._buffer)}"
            )
        return self._view[start:end]

    def mask_payload_inplace(self, offset: int, mask_byte: int) -> None:
        payload_view = self.get_payload_view(offset)
        for i in range(len(payload_view)):
            payload_view[i] ^= mask_byte
