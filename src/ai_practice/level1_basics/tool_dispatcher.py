from collections.abc import Callable
from typing import Any

from ai_practice.core.models import ToolCall, ToolResult


class ToolDispatcher:
    """Manages registration, schema generation, and execution of agent tools."""

    def __init__(self) -> None:
        # TODO: 등록된 도구 함수들과 스키마를 보관할 저장소를 초기화하세요.
        self._tools: dict[str, Callable[..., Any]] = {}
        self._schemas: dict[str, dict[str, Any]] = {}

    def register(self, func: Callable[..., Any], name: str | None = None) -> None:
        """Register a function as an executable tool."""
        # TODO: 함수를 등록하고, OpenAI 호환 JSON 스키마를 생성하여 보관하세요.
        raise NotImplementedError

    def get_schemas(self) -> list[dict[str, Any]]:
        """Return OpenAI-compatible tool schemas for all registered tools."""
        # TODO: 등록된 모든 도구의 스키마 리스트를 반환하세요.
        raise NotImplementedError

    def execute(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call safely and return structured ToolResult."""
        # TODO: tool_call.name에 해당하는 도구를 찾아 tool_call.arguments를 넘겨 실행하세요.
        # 도구가 없거나 실행 중 예외 발생 시 status="error"와 error_message를 담아 ToolResult를 반환하세요.
        raise NotImplementedError

    def _build_schema(self, func: Callable[..., Any], tool_name: str) -> dict[str, Any]:
        """Convert a python function's signature and type hints into a tool schema."""
        # TODO: inspect 모듈과 타입 힌트를 분석하여 OpenAI 함수 호출 스키마 dict를 생성하세요.
        raise NotImplementedError
