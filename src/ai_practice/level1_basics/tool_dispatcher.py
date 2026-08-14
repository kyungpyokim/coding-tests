import inspect
from collections.abc import Callable
from typing import Any, get_type_hints

from ai_practice.core.models import ToolCall, ToolResult

_TYPE_MAP = {
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
        self._schemas[tool_name] = self._build_schema(func, tool_name)

    def get_schemas(self) -> list[dict[str, Any]]:
        """Return OpenAI-compatible tool schemas for all registered tools."""
        return list(self._schemas.values())

    def execute(self, tool_call: ToolCall) -> ToolResult:
        """Execute a tool call safely and return structured ToolResult."""
        if tool_call.name not in self._tools:
            return ToolResult(
                call_id=tool_call.call_id,
                tool_name=tool_call.name,
                output=None,
                status="error",
                error_message=f"Tool '{tool_call.name}' not found in registry.",
            )

        func = self._tools[tool_call.name]
        try:
            output = func(**tool_call.arguments)
            return ToolResult(
                call_id=tool_call.call_id,
                tool_name=tool_call.name,
                output=output,
                status="success",
            )
        except Exception as err:
            return ToolResult(
                call_id=tool_call.call_id,
                tool_name=tool_call.name,
                output=None,
                status="error",
                error_message=f"Execution error in '{tool_call.name}': {err}",
            )

    def _build_schema(self, func: Callable[..., Any], tool_name: str) -> dict[str, Any]:
        """Convert a python function's signature and type hints into a tool schema."""
        sig = inspect.signature(func)
        try:
            hints = get_type_hints(func)
        except Exception:
            hints = {}

        properties: dict[str, Any] = {}
        required: list[str] = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            param_type = hints.get(param_name, str)
            json_type = _TYPE_MAP.get(param_type, "string")
            properties[param_name] = {"type": json_type}

            if param.default is inspect.Parameter.empty:
                required.append(param_name)

        doc = inspect.getdoc(func) or f"Tool {tool_name}"
        return {
            "name": tool_name,
            "description": doc.split("\n\n")[0],
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }
