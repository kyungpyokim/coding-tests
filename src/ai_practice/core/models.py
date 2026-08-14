from typing import Any, Literal

from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Represents a tool call request from an LLM."""

    name: str = Field(description="Name of the tool to execute")
    arguments: dict[str, Any] = Field(
        default_factory=dict, description="Arguments for the tool"
    )
    call_id: str | None = Field(default=None, description="Unique tool call ID")


class ToolResult(BaseModel):
    """Represents the execution result of a tool call."""

    call_id: str | None = Field(default=None, description="Matching tool call ID")
    tool_name: str = Field(description="Name of the tool that executed")
    output: Any = Field(description="Return value of the tool")
    status: Literal["success", "error"] = "success"
    error_message: str | None = None


class LLMMessage(BaseModel):
    """Generic message structure for agent states."""

    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
