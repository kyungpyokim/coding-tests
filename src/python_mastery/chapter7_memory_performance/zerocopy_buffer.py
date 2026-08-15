class ZeroCopyPacketParser:
    """Zero-copy packet parser using Python's memoryview and bytearray.

    Packet Wire Format:
    - [0..3] : 4 bytes unsigned int (Big-endian) - Payload Length (N)
    - [4..5] : 2 bytes unsigned short (Big-endian) - Packet Type Code
    - [6..6+N-1] : N bytes - Payload Data

    Demonstrates:
    - Using memoryview for zero-copy slicing and struct unpacking.
    - Direct in-place payload modification without memory reallocation.
    """

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
        """Parse (payload_len, packet_type) from offset without copying memory.

        Raises:
            ValueError: If offset + HEADER_SIZE exceeds buffer length.
        """
        # TODO: offset 검증 후 struct.unpack_from(">IH", self._view, offset)으로 헤더를 추출하세요.
        raise NotImplementedError

    def get_payload_view(self, offset: int = 0) -> memoryview:
        """Return a sliced memoryview of the payload for the packet starting at offset.

        Raises:
            ValueError: If packet bounds exceed buffer size.
        """
        # TODO: 헤더를 파싱하고 페이로드 구간의 memoryview 슬라이스를 반환하세요.
        raise NotImplementedError

    def mask_payload_inplace(self, offset: int, mask_byte: int) -> None:
        """XOR mask the payload directly in-place without creating new objects."""
        # TODO: get_payload_view로 획득한 메모리뷰를 순회하며 각 바이트를 XOR 연산하여 직접 수정하세요.
        raise NotImplementedError
