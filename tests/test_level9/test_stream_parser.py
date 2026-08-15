import pytest

from ai_practice.level9_streaming.stream_parser import (
    StreamChunk,
    StreamEventParser,
)


@pytest.mark.unit
class TestStreamParser:
    def test_text_streaming_accumulation(self):
        parser = StreamEventParser()

        e1 = parser.feed_chunk(StreamChunk(content="Hello "))
        e2 = parser.feed_chunk(StreamChunk(content="World!"))

        assert e1["type"] == "text_delta"
        assert e1["delta"] == "Hello "
        assert e2["delta"] == "World!"
        assert parser.get_accumulated_text() == "Hello World!"

    def test_tool_call_streaming_reassembly(self):
        parser = StreamEventParser()

        # Simulating streamed OpenAI function call deltas
        # Chunk 1: function name
        parser.feed_chunk(
            StreamChunk(
                index=0,
                tool_call_delta={
                    "id": "call_calc_1",
                    "name": "calculate",
                    "arguments": '{"a": ',
                },
            )
        )
        # Chunk 2: arguments continuation
        parser.feed_chunk(
            StreamChunk(
                index=0,
                tool_call_delta={"arguments": '10, "b": 20}'},
            )
        )

        tool_calls = parser.get_assembled_tool_calls()
        assert len(tool_calls) == 1
        assert tool_calls[0]["id"] == "call_calc_1"
        assert tool_calls[0]["name"] == "calculate"
        assert tool_calls[0]["arguments"] == {"a": 10, "b": 20}
