import pytest

from ai_practice.core.models import ToolCall, ToolResult
from ai_practice.level1_basics.tool_dispatcher import ToolDispatcher


def calculate_tax(amount: float, rate: float = 0.1) -> float:
    """Calculate tax for a given amount and rate."""
    return round(amount * rate, 2)


def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"


@pytest.mark.unit
class TestToolDispatcher:
    def test_register_and_get_schema(self):
        dispatcher = ToolDispatcher()
        dispatcher.register(calculate_tax)

        schemas = dispatcher.get_schemas()
        assert len(schemas) == 1
        schema = schemas[0]

        assert schema["name"] == "calculate_tax"
        assert "Calculate tax" in schema["description"]
        assert "amount" in schema["parameters"]["properties"]
        assert "rate" in schema["parameters"]["properties"]
        assert schema["parameters"]["required"] == ["amount"]

    def test_execute_successful_tool_call(self):
        dispatcher = ToolDispatcher()
        dispatcher.register(calculate_tax)

        call = ToolCall(
            name="calculate_tax",
            arguments={"amount": 100.0, "rate": 0.05},
            call_id="call_123",
        )
        result: ToolResult = dispatcher.execute(call)

        assert result.status == "success"
        assert result.tool_name == "calculate_tax"
        assert result.output == 5.0
        assert result.call_id == "call_123"
        assert result.error_message is None

    def test_execute_with_default_arguments(self):
        dispatcher = ToolDispatcher()
        dispatcher.register(calculate_tax)

        call = ToolCall(
            name="calculate_tax",
            arguments={"amount": 200.0},
        )
        result = dispatcher.execute(call)

        assert result.status == "success"
        assert result.output == 20.0

    def test_execute_nonexistent_tool_returns_error(self):
        dispatcher = ToolDispatcher()
        call = ToolCall(name="unknown_tool", arguments={})
        result = dispatcher.execute(call)

        assert result.status == "error"
        assert "Tool 'unknown_tool' not found" in (result.error_message or "")

    def test_execute_invalid_arguments_returns_error(self):
        dispatcher = ToolDispatcher()
        dispatcher.register(calculate_tax)

        # 'amount' is required, but passed invalid kwargs
        call = ToolCall(name="calculate_tax", arguments={"invalid_key": 123})
        result = dispatcher.execute(call)

        assert result.status == "error"
        assert (
            "missing" in (result.error_message or "").lower()
            or "unexpected" in (result.error_message or "").lower()
        )
