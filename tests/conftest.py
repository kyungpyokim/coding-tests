from typing import Any

import pytest
from langchain_core.language_models import FakeListChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage


@pytest.fixture
def fake_llm():
    """Returns a fake chat model that outputs predefined sequential responses."""

    def _factory(responses: list[str]) -> FakeListChatModel:
        return FakeListChatModel(responses=responses)

    return _factory


@pytest.fixture
def sample_messages() -> list[BaseMessage]:
    """Fixture providing a typical conversation history."""
    return [
        HumanMessage(content="Hello! Can you help me calculate 25 * 4?"),
        AIMessage(content="Sure, 25 * 4 = 100."),
    ]


@pytest.fixture
def sample_tool_schema() -> dict[str, Any]:
    """Fixture providing a sample JSON schema for tool validation."""
    return {
        "name": "calculator",
        "description": "Perform basic arithmetic calculations",
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["add", "subtract", "multiply", "divide"],
                },
                "a": {"type": "number"},
                "b": {"type": "number"},
            },
            "required": ["operation", "a", "b"],
        },
    }
