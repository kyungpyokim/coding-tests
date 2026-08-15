import json
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
        if chunk.content:
            self.text_buffer.append(chunk.content)
            return {"type": "text_delta", "delta": chunk.content}

        if chunk.tool_call_delta:
            idx = chunk.index
            if idx not in self.tool_call_buffers:
                self.tool_call_buffers[idx] = {
                    "id": "",
                    "name": "",
                    "args_raw": "",
                }

            delta = chunk.tool_call_delta
            if "id" in delta and delta["id"]:
                self.tool_call_buffers[idx]["id"] = delta["id"]
            if "name" in delta and delta["name"]:
                self.tool_call_buffers[idx]["name"] = delta["name"]
            if "arguments" in delta and delta["arguments"]:
                self.tool_call_buffers[idx]["args_raw"] += delta["arguments"]

            return {"type": "tool_delta", "index": idx, "delta": delta}

        return {"type": "complete"}

    def get_accumulated_text(self) -> str:
        """Return full text accumulated so far."""
        return "".join(self.text_buffer)

    def get_assembled_tool_calls(self) -> list[dict[str, Any]]:
        """Return fully assembled tool calls with JSON-parsed arguments."""
        assembled: list[dict[str, Any]] = []
        for idx in sorted(self.tool_call_buffers.keys()):
            buf = self.tool_call_buffers[idx]
            args = {}
            if buf["args_raw"]:
                try:
                    args = json.loads(buf["args_raw"])
                except json.JSONDecodeError:
                    args = {"raw": buf["args_raw"]}

            assembled.append(
                {
                    "id": buf["id"],
                    "name": buf["name"],
                    "arguments": args,
                }
            )
        return assembled
