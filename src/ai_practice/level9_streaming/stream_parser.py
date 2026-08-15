from typing import Any

from pydantic import BaseModel


class StreamChunk(BaseModel):
    """A streaming chunk from LLM with text delta and/or tool call delta."""

    index: int = 0
    content: str = ""
    tool_call_delta: dict[str, Any] | None = None


class StreamEventParser:
    """Aggregates streaming LLM tokens and reconstructs streamed tool calls."""

    def __init__(self) -> None:
        self.text_buffer: list[str] = []
        self.tool_call_buffers: dict[int, dict[str, Any]] = {}

    def feed_chunk(self, chunk: StreamChunk) -> dict[str, Any]:
        """Process incoming chunk and return structured event ('text_delta' | 'tool_delta' | 'complete')."""
        # TODO: chunk의 content는 text_buffer에 누적하고,
        # tool_call_delta는 index별로 name, args_delta(문자열 누적)를 취합하여 이벤트 dict를 반환하세요.
        raise NotImplementedError

    def get_accumulated_text(self) -> str:
        """Return full text accumulated so far."""
        # TODO: 누적된 전체 텍스트를 반환하세요.
        raise NotImplementedError

    def get_assembled_tool_calls(self) -> list[dict[str, Any]]:
        """Return fully assembled tool calls with JSON-parsed arguments."""
        # TODO: 스트리밍으로 조립된 도구 호출 목록을 파싱된 args(dict)와 함께 반환하세요.
        raise NotImplementedError
