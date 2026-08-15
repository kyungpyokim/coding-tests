import inspect
from collections.abc import Callable
from typing import Any

from ai_practice.core.models import ToolCall, ToolResult

TYPE_MAP: dict[type, str] = {
    str: "string",
    int: "integer",
    float: "number",
    bool: "boolean",
    list: "array",
    dict: "object",
}


class ToolDispatcher:
    """Manages registration, schema generation, and execution of agent tools."""

    def __init__(self) -> None:
        self._tools: dict[str, Callable[..., Any]] = {}
        self._schemas: dict[str, dict[str, Any]] = {}

    def register(self, func: Callable[..., Any], name: str | None = None) -> None:
        """Register a function as an executable tool."""
        tool_name = name or func.__name__
        self._tools[tool_name] = func

        schema = self._build_schema(func, tool_name)
        self._schemas[tool_name] = schema

    def get_schemas(self) -> list[dict[str, Any]]:
        """Return OpenAI-compatible tool schemas for all registered tools."""
        return list(self._schemas.values())

    def execute(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call safely and return structured ToolResult."""
        tool = self._tools.get(tool_call.name)
        if tool is None:
            return ToolResult(
                tool_name=tool_call.name,
                status="error",
                error_message=f"Tool '{tool_call.name}' not found",
                output=None,
                call_id=tool_call.call_id,
            )

        try:
            result = tool(**tool_call.arguments)
            return ToolResult(
                tool_name=tool_call.name,
                status="success",
                output=result,
                call_id=tool_call.call_id,
                error_message=None,
            )
        except Exception as e:
            return ToolResult(
                tool_name=tool_call.name,
                status="error",
                error_message=str(e),
                output=None,
                call_id=tool_call.call_id,
            )

    def _build_schema(self, func: Callable[..., Any], tool_name: str) -> dict[str, Any]:
        """Convert a python function's signature and type hints into a tool schema."""
        sig = inspect.signature(func)
        properties: dict[str, Any] = {}
        required: list[str] = []

        for param_name, param in sig.parameters.items():
            param_type = TYPE_MAP.get(param.annotation, "string")
            properties[param_name] = {"type": param_type}

            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        return {
            "name": tool_name,
            "description": inspect.getdoc(func) or "",
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }
